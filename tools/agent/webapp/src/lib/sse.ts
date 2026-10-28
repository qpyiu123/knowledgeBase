export type AskEvent = {
  t?: string;
  v?: string;
  info?: string;
  /** 兼容旧后端字段；新契约统一用 t=err。 */
  err?: string;
};

export type AskHandlers = {
  onStart?: () => void;
  onToken: (text: string) => void;
  onError?: (message: string) => void;
  onDone?: (info: string) => void;
};

/** 从缓冲区切出完整 SSE 事件，返回事件与剩余的半截数据。 */
export function extractSSEEvents(buffer: string): {
  events: AskEvent[];
  rest: string;
} {
  const events: AskEvent[] = [];
  let rest = buffer;
  for (;;) {
    let idx = rest.indexOf('\r\n\r\n');
    let sep = 4;
    const lf = rest.indexOf('\n\n');
    if (lf >= 0 && (idx < 0 || lf < idx)) {
      idx = lf;
      sep = 2;
    }
    if (idx < 0) break;
    const block = rest.slice(0, idx);
    rest = rest.slice(idx + sep);
    const data = block
      .split(/\r?\n/)
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).replace(/^ /, ''))
      .join('\n');
    if (!data) continue;
    try {
      events.push(JSON.parse(data) as AskEvent);
    } catch {
      // 半截/非法事件直接跳过，不打断后续渲染。
    }
  }
  return { events, rest };
}

/** 按固定契约分发事件：tok / err / done。 */
export function dispatchAskEvent(ev: AskEvent, handlers: AskHandlers): void {
  if (ev.t === 'tok' && typeof ev.v === 'string') {
    handlers.onToken(ev.v);
    return;
  }
  if (ev.t === 'err') {
    handlers.onError?.(String(ev.v || '模型返回错误'));
    return;
  }
  if (ev.t === 'done') {
    handlers.onDone?.(String(ev.info || '完成'));
    return;
  }
  if (ev.err) handlers.onError?.(String(ev.err));
}

/** 读取 SSE 响应体；调用方负责把 stream 交给 fetch。 */
export async function readAskStream(
  stream: ReadableStream<Uint8Array>,
  handlers: AskHandlers,
  signal?: AbortSignal,
): Promise<{ tokens: number; terminal: boolean }> {
  const reader = stream.getReader();
  const dec = new TextDecoder();
  let buf = '';
  let tokens = 0;
  let terminal = false;

  const consume = (events: AskEvent[]) => {
    for (const ev of events) {
      if (ev.t === 'tok') tokens += 1;
      if (ev.t === 'done' || ev.t === 'err' || ev.err) terminal = true;
      if (ev.t === 'tok') {
        handlers.onToken(String(ev.v ?? ''));
      } else {
        dispatchAskEvent(ev, handlers);
      }
    }
  };

  try {
    for (;;) {
      if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
      const { done: eof, value } = await reader.read();
      if (eof) break;
      buf += dec.decode(value, { stream: true });
      const { events, rest } = extractSSEEvents(buf);
      buf = rest;
      consume(events);
    }
    buf += dec.decode();
    if (buf.trim()) {
      // 流结束时最后一帧没有空行分隔，也尝试解析一次。
      const parsed = extractSSEEvents(buf + '\n\n');
      consume(parsed.events);
    }
  } finally {
    if (signal?.aborted) {
      try {
        await reader.cancel();
      } catch {
        // 连接已断，忽略。
      }
    }
    try {
      reader.releaseLock();
    } catch {
      // 仍有挂起读取时忽略；流会随连接关闭而结束。
    }
  }

  return { tokens, terminal };
}
