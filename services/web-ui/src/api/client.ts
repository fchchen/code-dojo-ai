import type {
  AuthResponse,
  StreamEnvelope,
  Submission,
  SubmissionListResponse,
  SubmissionRequest,
} from "../types";

const API_BASE = "/api";

function authHeaders(token?: string): HeadersInit {
  if (!token) {
    return { "Content-Type": "application/json" };
  }
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getDemoToken(username: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/demo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });

  if (!response.ok) {
    throw new Error(`Auth failed (${response.status})`);
  }

  return response.json();
}

export async function submitCode(token: string, payload: SubmissionRequest): Promise<Submission> {
  const response = await fetch(`${API_BASE}/submissions`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Submission failed (${response.status})`);
  }

  return response.json();
}

export async function getSubmission(token: string, id: string): Promise<Submission> {
  const response = await fetch(`${API_BASE}/submissions/${id}`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    throw new Error(`Fetch submission failed (${response.status})`);
  }
  return response.json();
}

export async function listSubmissions(
  token: string,
  page = 1,
  pageSize = 20,
): Promise<SubmissionListResponse> {
  const response = await fetch(`${API_BASE}/submissions?page=${page}&pageSize=${pageSize}`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    throw new Error(`List submissions failed (${response.status})`);
  }
  return response.json();
}

export async function streamSubmission(
  token: string,
  payload: SubmissionRequest,
  onEvent: (event: StreamEnvelope) => void,
): Promise<void> {
  const response = await fetch(`${API_BASE}/submissions/stream`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });

  if (!response.ok || !response.body) {
    throw new Error(`Stream failed (${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    let idx = buffer.indexOf("\n\n");
    while (idx !== -1) {
      const frame = buffer.slice(0, idx).trim();
      buffer = buffer.slice(idx + 2);

      if (frame.length > 0) {
        let event = "message";
        let data = "{}";

        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) {
            event = line.slice(6).trim();
          }
          if (line.startsWith("data:")) {
            data = line.slice(5).trim();
          }
        }

        try {
          const parsed = JSON.parse(data) as Record<string, unknown>;
          onEvent({ event, data: parsed });
        } catch {
          onEvent({ event, data: { raw: data } });
        }
      }

      idx = buffer.indexOf("\n\n");
    }
  }
}
