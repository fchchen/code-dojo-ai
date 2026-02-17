import { useState } from "react";
import { streamSubmission } from "../api/client";
import type { AgentStep, CoachingResult } from "../types";

export function useCoaching() {
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [result, setResult] = useState<CoachingResult | null>(null);
  const [submissionId, setSubmissionId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function startStream(token: string, code: string, language: string) {
    setSteps([]);
    setResult(null);
    setError(null);
    setSubmissionId(null);
    setIsStreaming(true);

    try {
      await streamSubmission(token, { code, language }, (envelope) => {
        if (envelope.event === "submission.created") {
          const id = envelope.data.submissionId;
          if (typeof id === "string") {
            setSubmissionId(id);
          }
        }

        if (envelope.event === "agent.step") {
          const phase = envelope.data.phase;
          const message = envelope.data.message;
          const toolName = envelope.data.toolName;
          const timestamp = envelope.data.timestamp;
          if (typeof phase === "string" && typeof message === "string") {
            setSteps((prev) => [
              ...prev,
              {
                phase: phase as AgentStep["phase"],
                message,
                toolName: typeof toolName === "string" ? toolName : null,
                timestamp: typeof timestamp === "string" ? timestamp : new Date().toISOString(),
                meta: null,
              },
            ]);
          }
        }

        if (envelope.event === "submission.completed") {
          const data = envelope.data.result;
          if (data && typeof data === "object") {
            setResult(data as CoachingResult);
          }
        }

        if (envelope.event === "submission.failed") {
          const message = envelope.data.error;
          setError(typeof message === "string" ? message : "Submission failed");
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Streaming failed");
      throw err;
    } finally {
      setIsStreaming(false);
    }
  }

  return { steps, result, submissionId, isStreaming, error, startStream };
}
