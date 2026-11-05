import type {
  AttachmentReport,
  CodeResp,
  DocumentResp,
  FailureKind,
  Health,
  SearchResp,
  Stats,
  TimelineEvent,
  Workspace,
  WorkspaceEntry,
  WorkspaceEntryKind,
  WorkspaceStatus,
  WorkspaceSummary,
} from "./types";
import { readAskStream, type AskHandlers } from "./lib/sse";

export type { AskHandlers } from "./lib/sse";

async function errorMessage(r: Response): Promise<string> {
  let detail = "";
  try {
    const j = (await r.json()) as { error?: string };
    if (j && typeof j.error === "string") detail = j.error;
  } catch {
    // 非 JSON 错误体，保留 HTTP 状态。
  }
  return detail ? `${detail}（HTTP ${r.status}）` : `HTTP ${r.status}`;
}

async function getJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(await errorMessage(r));
  return (await r.json()) as T;
}

/** 只有后端明确返回“工作区不存在”时，才允许调用方回落。 */
async function isMissingWorkspace(r: Response): Promise<boolean> {
  if (r.status !== 404) return false;
  try {
    const j = (await r.clone().json()) as { error?: unknown; code?: unknown };
    if (j.code === "workspace_not_found") return true;
    return typeof j.error === "string" && j.error.includes("工作区不存在");
  } catch {
    return false;
  }
}

function postJSON<T>(url: string, body: unknown): Promise<T> {
  return getJSON<T>(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function delJSON<T>(url: string): Promise<T> {
  return getJSON<T>(url, { method: "DELETE" });
}

const wsPath = (id: string) => "/api/workspaces/" + encodeURIComponent(id);

export const api = {
  health: () => getJSON<Health>("/api/health"),
  stats: () => getJSON<Stats>("/api/stats"),
  doc: (path: string) =>
    getJSON<DocumentResp>("/api/doc?path=" + encodeURIComponent(path)),
  code: (path: string) =>
    getJSON<CodeResp>("/api/code?path=" + encodeURIComponent(path)),
  cancel: (request_id: string) =>
    postJSON<{ ok: boolean; accepted: boolean; cancelled: boolean }>(
      "/api/cancel",
      { request_id },
    ),
  search: (
    q: string,
    top_k = 10,
    category?: string | null,
    doc_type?: string | null,
    retrieval: "fts" | "hybrid" = "hybrid",
    signal?: AbortSignal,
    withConditions = true,
    focusWorkspace?: string,
  ) =>
    getJSON<SearchResp>("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal,
      body: JSON.stringify({
        q,
        top_k,
        category: category || null,
        doc_type: doc_type || null,
        retrieval,
        with_conditions: withConditions,
        ...(focusWorkspace ? { workspace_id: focusWorkspace } : {}),
      }),
    }),
  feedback: (
    query: string,
    path: string,
    verdict: "useful" | "useless" | "adopted",
    note = "",
  ) =>
    getJSON<{ ok: boolean; saved: number; error?: string }>("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, path, verdict, note }),
    }),

  /** 原始字节上传（不是 multipart），附件由后端隔离落盘后只读解析。 */
  analyze: async (
    name: string,
    data: ArrayBuffer,
    workspaceId?: string | null,
  ): Promise<AttachmentReport> => {
    const qs =
      "?name=" +
      encodeURIComponent(name) +
      (workspaceId ? "&workspace=" + encodeURIComponent(workspaceId) : "");
    const r = await fetch("/api/analyze" + qs, {
      method: "POST",
      headers: { "Content-Type": "application/octet-stream" },
      body: data,
    });
    if (!r.ok) throw new Error(await errorMessage(r));
    return (await r.json()) as AttachmentReport;
  },

  workspaces: {
    list: () => getJSON<{ workspaces: WorkspaceSummary[] }>("/api/workspaces"),
    get: (id: string) => getJSON<{ workspace: Workspace }>(wsPath(id)),
    create: (title: string, id?: string, category?: string | null) =>
      postJSON<{ ok: boolean; workspace: Workspace }>("/api/workspaces", {
        title,
        id: id || undefined,
        category: category || undefined,
      }),
    update: (
      id: string,
      patch: {
        title?: string;
        status?: WorkspaceStatus;
        category?: string | null;
        goal?: string;
        hypotheses?: string;
        pending_checks?: string;
      },
    ) => postJSON<{ ok: boolean; workspace: Workspace }>(wsPath(id), patch),
    remove: (id: string) => delJSON<{ ok: boolean }>(wsPath(id)),
    addEntry: (
      id: string,
      entry: {
        kind: WorkspaceEntryKind;
        text?: string;
        result?: string;
        direction?: string;
        conclusion?: string;
        failure_kind?: FailureKind;
        title?: string;
        path?: string;
        anchor?: string;
        url?: string;
        source?: string;
        attachment?: Record<string, unknown> | null;
        report?: AttachmentReport | null;
      },
    ) =>
      postJSON<{ ok: boolean; workspace: Workspace; entry: WorkspaceEntry }>(
        wsPath(id) + "/entries",
        entry,
      ),
    updateEntry: (
      id: string,
      entryId: string,
      patch: { result?: string; text?: string; failure_kind?: FailureKind },
    ) =>
      postJSON<{ ok: boolean; workspace: Workspace; entry: WorkspaceEntry }>(
        wsPath(id) + "/entries/" + encodeURIComponent(entryId),
        patch,
      ),
    removeEntry: (id: string, entryId: string) =>
      delJSON<{ ok: boolean; workspace: Workspace }>(
        wsPath(id) + "/entries/" + encodeURIComponent(entryId),
      ),
    timeline: (id: string) =>
      getJSON<{ timeline: TimelineEvent[] }>(wsPath(id) + "/timeline"),
    exportUrl: (id: string, mode: "normal" | "writeup" = "normal") =>
      wsPath(id) +
      "/export?format=md" +
      (mode === "writeup" ? "&mode=writeup" : ""),
  },
};

/** POST /api/ask，按 SSE 契约逐段回调 tok / err / done。 */
export async function ask(
  q: string,
  paths: string[],
  handlers: AskHandlers,
  signal?: AbortSignal,
  workspaceId?: string | null,
  sections?: Record<string, string>,
): Promise<void> {
  if (signal?.aborted) throw new DOMException("已取消", "AbortError");
  const requestId =
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  let cancellation: ReturnType<typeof api.cancel> | undefined;
  let terminal = false;
  const tracked: AskHandlers = {
    ...handlers,
    onDone: (info) => {
      terminal = true;
      handlers.onDone?.(info);
    },
    onError: (message) => {
      terminal = true;
      handlers.onError?.(message);
    },
  };
  const onAbort = () => {
    cancellation = api
      .cancel(requestId)
      .catch(() => ({ ok: false, accepted: false, cancelled: false }));
  };
  signal?.addEventListener("abort", onAbort, { once: true });
  const send = (withWorkspace: boolean) =>
    fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(
        withWorkspace && workspaceId
          ? {
              q,
              paths,
              workspace_id: workspaceId,
              request_id: requestId,
              sections,
            }
          : { q, paths, request_id: requestId, sections },
      ),
      signal,
    });

  try {
    let r = await send(true);
    // 仅当后端明确说“工作区不存在”时，回落到无上下文提问一次并提示。
    if (workspaceId && (await isMissingWorkspace(r))) {
      handlers.onNotice?.("默认工作区不存在，已改为无上下文提问。");
      r = await send(false);
    }
    if (!r.ok || !r.body) throw new Error(await errorMessage(r));

    handlers.onStart?.();
    const { tokens, terminal: streamTerminal } = await readAskStream(
      r.body,
      tracked,
      signal,
    );
    if (!streamTerminal) {
      if (tokens === 0) {
        tracked.onError?.("模型没有返回内容。确认本地模型已启动。");
      } else {
        tracked.onDone?.("完成");
      }
    }
  } finally {
    signal?.removeEventListener("abort", onAbort);
    if (cancellation) {
      const result = await cancellation;
      if (!terminal) {
        handlers.onDone?.(result.cancelled ? "已取消" : "已停止接收");
        if (!result.ok)
          handlers.onNotice?.(
            "取消请求未送达，模型可能仍在计算，请检查服务状态。",
          );
        else if (!result.cancelled)
          handlers.onNotice?.("取消请求已发送，模型正在收尾。");
      }
    }
  }
}
