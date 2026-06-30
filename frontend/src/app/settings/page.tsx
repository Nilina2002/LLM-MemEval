"use client";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">
          API keys and defaults are configured via <code className="text-xs bg-secondary px-1 py-0.5 rounded">backend/.env</code>.
          This page documents the available options.
        </p>
      </div>

      <Section title="LLM Providers">
        <EnvRow var="OPENAI_API_KEY" desc="OpenAI API key (gpt-4o, gpt-4o-mini, …)" />
        <EnvRow var="ANTHROPIC_API_KEY" desc="Anthropic API key (claude-* models)" />
        <EnvRow var="GEMINI_API_KEY" desc="Google Gemini API key" />
        <EnvRow var="GROQ_API_KEY" desc="Groq API key (llama3, mixtral, …)" />
        <EnvRow var="OPENROUTER_API_KEY" desc="OpenRouter API key (multi-provider)" />
        <EnvRow var="OLLAMA_BASE_URL" desc="Ollama local endpoint (default: http://localhost:11434)" />
      </Section>

      <Section title="Storage">
        <EnvRow var="DATABASE_URL" desc="SQLite path (default: sqlite+aiosqlite:///./memeval.db)" />
        <EnvRow var="RESULTS_DIR" desc="JSONL log directory (default: ./results)" />
      </Section>

      <Section title="Architecture">
        <div className="rounded-md bg-secondary/30 border px-4 py-3 space-y-2 text-sm text-muted-foreground">
          <p>
            <span className="font-medium text-foreground">Strategy-agnostic design:</span>{" "}
            The benchmark never imports strategy-specific code. Adding a new memory strategy
            requires only a single class — no pipeline changes.
          </p>
          <p>
            <span className="font-medium text-foreground">Deterministic reproduction:</span>{" "}
            Every experiment uses a seeded RNG. The same seed always produces the identical
            conversation and fact sequence, making results reproducible without storing raw LLM outputs.
          </p>
          <p>
            <span className="font-medium text-foreground">Dual-write logging:</span>{" "}
            All runs are logged to both SQLite (queryable) and JSONL files (portable). Use JSONL
            exports to share benchmark results independent of this server.
          </p>
        </div>
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider border-b pb-2">
        {title}
      </h2>
      {children}
    </div>
  );
}

function EnvRow({ var: varName, desc }: { var: string; desc: string }) {
  return (
    <div className="flex items-start gap-3 py-1">
      <code className="text-xs bg-secondary px-2 py-1 rounded font-mono flex-shrink-0">{varName}</code>
      <p className="text-sm text-muted-foreground">{desc}</p>
    </div>
  );
}
