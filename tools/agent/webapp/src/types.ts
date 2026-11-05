export type DocType = "topic" | "card" | "method";

export type LibraryLink = { path: string; title?: string; external?: boolean };
export type DocumentResp = {
  path: string;
  body: string;
  error?: string;
  scripts?: LibraryLink[];
  sources?: LibraryLink[];
  methods?: LibraryLink[];
  kind_label?: string;
};
export type CodeResp = {
  path: string;
  body: string;
  language: string;
  dependencies: string[];
  arguments: string[];
  summary: string;
};

export type MatchInfo = {
  sources: string[];
  labels: string[];
  terms: string[];
  rrf?: Record<string, number>;
  graph?: { via: string; hop?: number | null; boost: boolean };
};

export type ApplicabilityCondition = {
  id: string;
  label: string;
  status: "known" | "unknown" | "unsatisfied";
  status_label: string;
  evidence?: string;
  check?: string;
  need?: string[];
  source?: string;
  trace?: "rule" | "requires";
};

export type Applicability = {
  error?: string;
  status: "known" | "unknown" | "unsatisfied";
  status_label: string;
  label?: string;
  conditions?: ApplicabilityCondition[];
  hint?: string;
  trace?: { rules: number; requires: number };
  reading?: {
    path: string | null;
    title: string;
    present: boolean;
    missing: boolean;
  }[];
  guide?: {
    id: string;
    title: string;
    source: { path: string; section: string; quote: string };
    next_check: string;
    contrasts: { path: string; title: string; difference: string }[];
  };
};

export type Hit = {
  focus_basis?: {
    field: string;
    label: string;
    text: string;
    entry_id?: string;
    entry_ids?: string[];
    missing?: boolean;
  }[];
  title: string;
  category: string;
  path: string;
  doc_id?: string;
  score: number;
  snippet: string;
  section?: string;
  doc_type?: DocType;
  doc_type_label?: string;
  match?: MatchInfo;
  applicability?: Applicability;
  graph_via?: string;
  scripts?: LibraryLink[];
  sources?: LibraryLink[];
  methods?: LibraryLink[];
  kind_label?: string;
};

export type SearchResp = {
  focus?: {
    workspace_id: string;
    title: string;
    basis: NonNullable<Hit["focus_basis"]>;
    hits: Hit[];
    excluded: Hit[];
  };
  hits: Hit[];
  graph?: Hit[];
  ms?: number;
  query?: string;
  category?: string | null;
  doc_type?: DocType | null;
  counts?: { topic: number; card: number; method?: number };
  applicability?: { known: number; unknown: number; unsatisfied: number };
  error?: string;
};

export type Stats = {
  docs: number;
  chunks: number;
  categories: Record<string, number>;
  error?: string;
};

export type Health = {
  ok: boolean;
  model_ok?: boolean;
  index_ok?: boolean;
  model?: string;
  models?: string[];
  docs?: number;
  index?: {
    ok: boolean;
    docs: number;
    chunks?: number;
    built_at?: string | null;
    error?: string;
  };
  attachment?: { max_bytes: number };
  error?: string;
};

export type AttachmentCarve = {
  type?: string;
  offset?: number;
  offset_hex?: string;
  size?: number;
};

export type AttachmentStructures = {
  png?: {
    width?: number;
    height?: number;
    chunks?: {
      type?: string;
      len?: number;
      offset?: number;
      crc_ok?: boolean | null;
    }[];
    truncated?: boolean;
  };
  wav?: {
    format?: string;
    channels?: number;
    sample_rate?: number;
    chunks?: unknown[];
    tail_text?: string;
  };
  zip?: {
    count?: number;
    entries?: {
      name: string;
      size?: number;
      compressed?: number;
      encrypted?: boolean;
    }[];
    truncated?: boolean;
    encrypted?: boolean;
  };
};

export type AttachmentReport = {
  schema_version?: number;
  ok?: boolean;
  executed: boolean;
  execution_note?: string;
  file: {
    name: string;
    size: number;
    sha256: string;
    ext?: string;
    saved?: string;
    original_name?: string;
    dir?: string;
  };
  type: {
    kind: string;
    detected?: boolean;
    is_text: boolean;
    preview?: string;
    extension?: string;
    extension_mismatch?: boolean;
  };
  carve?: AttachmentCarve[];
  structures?: AttachmentStructures;
  anomalies?: string[];
  decoded?: {
    method: string;
    encoded?: string;
    decoded: string;
    truncated?: boolean;
  }[];
  strings?: string[];
  warnings?: string[];
  storage?: { isolated: boolean; dir: string; saved: string };
  workspace?: { id: string; entry_id: string };
  error?: string;
};

export type WorkspaceEntryKind = "fact" | "attempt" | "reference";
export type AttemptResult = "pending" | "success" | "failed";
export type FailureKind = "unknown" | "runtime" | "condition";
export type WorkspaceStatus = "open" | "solved" | "archived";

export type WorkspaceEntry = {
  id: string;
  created: string;
  kind: WorkspaceEntryKind;
  text: string;
  result?: AttemptResult | null;
  direction?: string;
  conclusion?: string;
  failure_kind?: FailureKind | null;
  title?: string;
  path?: string;
  anchor?: string;
  url?: string;
  source?: string;
  attachment?: Record<string, unknown> | null;
  report?: AttachmentReport | null;
};

export type TimelineEvent = {
  ts: string;
  kind: string;
  summary: string;
};

export type Workspace = {
  goal?: string;
  hypotheses?: string;
  pending_checks?: string;
  schema_version: number;
  id: string;
  title: string;
  category: string | null;
  status: WorkspaceStatus;
  created: string;
  updated: string;
  entries: WorkspaceEntry[];
  timeline: TimelineEvent[];
};

export type WorkspaceSummary = {
  id: string;
  title: string;
  category: string | null;
  status: WorkspaceStatus;
  created: string;
  updated: string;
  entries: number;
  counts: Record<WorkspaceEntryKind, number>;
};
