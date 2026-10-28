export type Hit = {
  title: string;
  category: string;
  path: string;
  score: number;
  snippet: string;
  graph_via?: string;
};

export type SearchResp = {
  hits: Hit[];
  graph?: { title: string; path: string; via: string }[];
  ms?: number;
  query?: string;
  category?: string | null;
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
  model?: string;
  models?: string[];
  docs?: number;
};
