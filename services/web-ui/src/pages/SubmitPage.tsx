import { useState } from "react";
import { AgentTrace } from "../components/AgentTrace";
import { CoachingReport } from "../components/CoachingReport";
import { CodeEditor } from "../components/CodeEditor";
import { useCoaching } from "../hooks/useCoaching";

interface SubmitPageProps {
  token: string;
}

const STARTER = `def factorial(n: int) -> int:\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)`;

export function SubmitPage({ token }: SubmitPageProps) {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(STARTER);
  const { steps, result, isStreaming, error, startStream, submissionId } = useCoaching();

  async function handleAnalyze() {
    await startStream(token, code, language);
  }

  return (
    <div className="app-shell stack">
      <div className="card">
        <h1 className="title">Submit for AI Coaching</h1>
        <label className="label" htmlFor="language">
          Language
        </label>
        <select
          id="language"
          className="select"
          value={language}
          onChange={(event) => setLanguage(event.target.value)}
          style={{ maxWidth: "200px" }}
        >
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
          <option value="typescript">TypeScript</option>
        </select>
        <div style={{ height: "10px" }} />
        <button className="btn" type="button" onClick={handleAnalyze} disabled={isStreaming}>
          {isStreaming ? "Analyzing..." : "Start Coaching"}
        </button>
        {submissionId ? <p className="small mono">submission: {submissionId}</p> : null}
        {error ? <p className="error">{error}</p> : null}
      </div>
      <div className="grid">
        <CodeEditor value={code} language={language} onChange={setCode} />
        <div className="stack">
          <AgentTrace steps={steps} isStreaming={isStreaming} />
          <CoachingReport result={result} />
        </div>
      </div>
    </div>
  );
}
