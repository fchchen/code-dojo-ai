import Editor from "@monaco-editor/react";

interface CodeEditorProps {
  value: string;
  language: string;
  onChange: (value: string) => void;
}

export function CodeEditor({ value, language, onChange }: CodeEditorProps) {
  return (
    <div className="card">
      <h2 className="title">Code Input</h2>
      <Editor
        height="420px"
        language={language}
        theme="vs-dark"
        value={value}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "IBM Plex Mono, monospace",
          wordWrap: "on",
        }}
        onChange={(next) => onChange(next ?? "")}
      />
    </div>
  );
}
