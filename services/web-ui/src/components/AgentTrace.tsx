import type { AgentStep } from "../types";

interface AgentTraceProps {
  steps: AgentStep[];
  isStreaming: boolean;
}

export function AgentTrace({ steps, isStreaming }: AgentTraceProps) {
  return (
    <div className="card">
      <h2 className="title">Agent Trace</h2>
      <p className="small">{isStreaming ? "Streaming in progress..." : "Idle"}</p>
      <div className="step-list">
        {steps.map((step, index) => (
          <div className="step" key={`${step.timestamp}-${index}`}>
            <span className={`badge ${step.phase}`}>{step.phase}</span>
            <div>{step.message}</div>
            {step.toolName ? <div className="small mono">tool: {step.toolName}</div> : null}
          </div>
        ))}
      </div>
    </div>
  );
}
