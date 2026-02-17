import { render, screen } from "@testing-library/react";
import { AgentTrace } from "./AgentTrace";

it("renders steps and streaming indicator", () => {
  render(
    <AgentTrace
      isStreaming={true}
      steps={[
        {
          phase: "planning",
          message: "Planning analysis strategy",
          timestamp: new Date().toISOString(),
          toolName: null,
          meta: null,
        },
      ]}
    />,
  );

  expect(screen.getByText(/streaming in progress/i)).toBeInTheDocument();
  expect(screen.getByText(/planning analysis strategy/i)).toBeInTheDocument();
});
