export type DocType = 'topic' | 'card';

export type MatchInfo = {
  sources: string[];
  labels: string[];
  terms: string[];
  rrf?: Record<string, number>;
  graph?: { via: string; hop?: number | null; boost: boolean };
};

export type Hit = {
  title: string;
  category: string;
  path: string;
  score: number;
  snippet: string;
  section?: string;
  doc_type?: DocType;
  doc_type_label?: string;
  match?: MatchInfo;
  graph_via?: string;
};

export type SearchResp = {
  hits: Hit[];
  graph?: Hit[];
  ms?: number;
  query?: string;
  category?: string | null;
  doc_type?: DocType | null;
  counts?: { topic: number; card: number };
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
  error?: string;
};
