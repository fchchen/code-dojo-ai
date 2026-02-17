export type AgentState =
  | "planning"
  | "executing"
  | "reflecting"
  | "synthesizing"
  | "complete"
  | "failed";

export interface AgentStep {
  phase: AgentState;
  message: string;
  toolName?: string | null;
  meta?: Record<string, unknown> | null;
  timestamp: string;
}

export interface CoachingResult {
  summary: string;
  score: number;
  issues: string[];
  improved_code: string;
  best_practices: string[];
  concept_explanation?: string | null;
}

export interface Submission {
  id: string;
  username: string;
  language?: string | null;
  status: AgentState;
  result?: CoachingResult | null;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface SubmissionListResponse {
  items: Submission[];
  page: number;
  page_size: number;
  total: number;
}

export interface SubmissionRequest {
  code: string;
  language?: string;
}

export interface AuthResponse {
  token: string;
  username: string;
  expiresIn: number;
}

export interface StreamEnvelope {
  event: string;
  data: Record<string, unknown>;
}
