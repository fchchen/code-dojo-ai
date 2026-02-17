import type { CoachingResult } from "../types";

interface CoachingReportProps {
  result: CoachingResult | null;
}

export function CoachingReport({ result }: CoachingReportProps) {
  return (
    <div className="card">
      <h2 className="title">Coaching Report</h2>
      {!result ? <p className="small">Run a submission to see results.</p> : null}
      {result ? (
        <>
          <div className="kv">
            <strong>Score</strong>
            <span>{result.score}/100</span>
          </div>
          <div className="kv">
            <strong>Summary</strong>
            <span>{result.summary}</span>
          </div>
          <strong>Issues</strong>
          <ul>
            {result.issues.map((issue) => (
              <li key={issue}>{issue}</li>
            ))}
          </ul>
          <strong>Best Practices</strong>
          <ul>
            {result.best_practices.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <strong>Concept Explanation</strong>
          <p>{result.concept_explanation ?? "N/A"}</p>
          <strong>Improved Code</strong>
          <pre className="mono">{result.improved_code}</pre>
        </>
      ) : null}
    </div>
  );
}
