"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import { createExperiment, listStrategies } from "@/lib/api";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

type FormState = {
  name: string;
  description: string;
  llm_provider: string;
  llm_model: string;
  llm_temperature: number;
  llm_max_tokens: number;
  conv_domain: string;
  conv_total_turns: number;
  conv_seed: number;
  facts_count: number;
  facts_types: string[];
  facts_injection_strategy: string;
  memory_strategy: string;
  memory_window_size: number;
  recall_intervals: string;
  recall_scoring_methods: string[];
};

const DEFAULTS: FormState = {
  name: "",
  description: "",
  llm_provider: "openai",
  llm_model: "gpt-4o-mini",
  llm_temperature: 0.7,
  llm_max_tokens: 512,
  conv_domain: "casual",
  conv_total_turns: 100,
  conv_seed: 42,
  facts_count: 10,
  facts_types: ["personal", "technical", "temporal"],
  facts_injection_strategy: "uniform",
  memory_strategy: "no_memory",
  memory_window_size: 20,
  recall_intervals: "10, 50, 100",
  recall_scoring_methods: ["fuzzy", "embedding"],
};

const FACT_TYPES = ["personal", "technical", "temporal", "spatial", "numerical"];
const SCORING_METHODS = ["exact", "fuzzy", "embedding"];
const PROVIDERS = ["openai", "claude", "gemini", "groq", "openrouter", "ollama"];
const DOMAINS = ["casual", "programming", "education", "travel", "shopping", "mixed"];
const INJECTION_STRATEGIES = ["uniform", "early", "late", "random"];
const DEFAULT_MODELS: Record<string, string> = {
  openai: "gpt-4o-mini",
  claude: "claude-haiku-4-5-20251001",
  gemini: "gemini-1.5-flash",
  groq: "llama3-8b-8192",
  openrouter: "openai/gpt-4o-mini",
  ollama: "llama3",
};

export default function NewExperimentPage() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>(DEFAULTS);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: strategies } = useSWR("strategies-list", listStrategies);

  function set<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function toggleArray(key: keyof FormState, item: string) {
    const arr = form[key] as string[];
    const next = arr.includes(item) ? arr.filter((v) => v !== item) : [...arr, item];
    setForm((f) => ({ ...f, [key]: next as FormState[K] }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) { setError("Experiment name is required."); return; }
    if (form.facts_types.length === 0) { setError("Select at least one fact type."); return; }
    if (form.recall_scoring_methods.length === 0) { setError("Select at least one scoring method."); return; }

    const intervals = form.recall_intervals
      .split(",")
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n) && n > 0)
      .sort((a, b) => a - b);
    if (intervals.length === 0) { setError("Enter at least one valid recall interval."); return; }

    const strategyParams: Record<string, unknown> =
      form.memory_strategy === "sliding_window" ? { window_size: form.memory_window_size } : {};

    const payload = {
      config: {
        name: form.name.trim(),
        description: form.description.trim(),
        llm: {
          provider: form.llm_provider,
          model: form.llm_model,
          temperature: form.llm_temperature,
          max_tokens: form.llm_max_tokens,
        },
        conversation: { domain: form.conv_domain, total_turns: form.conv_total_turns, seed: form.conv_seed },
        facts: {
          count: form.facts_count,
          types: form.facts_types,
          injection_strategy: form.facts_injection_strategy,
          seed: form.conv_seed,
        },
        memory: { strategy_name: form.memory_strategy, strategy_params: strategyParams },
        recall: { intervals, scoring_methods: form.recall_scoring_methods },
      },
    };

    setSubmitting(true);
    setError(null);
    try {
      const exp = await createExperiment(payload);
      router.push(`/experiments/${exp.id}`);
    } catch (e: unknown) {
      const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? (e instanceof Error ? e.message : "Failed to create experiment."));
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">New Experiment</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Configure a benchmark run. All fields have research-appropriate defaults.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/15 border border-destructive/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Info */}
        <Section title="Basic Info">
          <Field label="Experiment Name *">
            <input className={inp} placeholder="e.g. sliding-window-casual-100t" value={form.name}
              onChange={(e) => set("name", e.target.value)} required />
          </Field>
          <Field label="Description">
            <input className={inp} placeholder="Optional notes" value={form.description}
              onChange={(e) => set("description", e.target.value)} />
          </Field>
        </Section>

        {/* LLM */}
        <Section title="LLM Configuration">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Provider">
              <select className={inp} value={form.llm_provider}
                onChange={(e) => { set("llm_provider", e.target.value); set("llm_model", DEFAULT_MODELS[e.target.value] ?? ""); }}>
                {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </Field>
            <Field label="Model">
              <input className={inp} value={form.llm_model} onChange={(e) => set("llm_model", e.target.value)} />
            </Field>
            <Field label={`Temperature: ${form.llm_temperature}`}>
              <input type="range" min="0" max="2" step="0.1" className="w-full accent-primary"
                value={form.llm_temperature} onChange={(e) => set("llm_temperature", parseFloat(e.target.value))} />
            </Field>
            <Field label="Max Tokens">
              <input type="number" min="64" max="8192" step="64" className={inp}
                value={form.llm_max_tokens} onChange={(e) => set("llm_max_tokens", parseInt(e.target.value, 10))} />
            </Field>
          </div>
        </Section>

        {/* Conversation */}
        <Section title="Conversation">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Domain">
              <select className={inp} value={form.conv_domain} onChange={(e) => set("conv_domain", e.target.value)}>
                {DOMAINS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </Field>
            <Field label="Total Turns">
              <input type="number" min="10" max="5000" className={inp}
                value={form.conv_total_turns} onChange={(e) => set("conv_total_turns", parseInt(e.target.value, 10))} />
            </Field>
            <Field label="Random Seed">
              <input type="number" className={inp}
                value={form.conv_seed} onChange={(e) => set("conv_seed", parseInt(e.target.value, 10))} />
            </Field>
          </div>
        </Section>

        {/* Facts */}
        <Section title="Fact Injection">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Fact Count">
              <input type="number" min="1" max="50" className={inp}
                value={form.facts_count} onChange={(e) => set("facts_count", parseInt(e.target.value, 10))} />
            </Field>
            <Field label="Injection Strategy">
              <select className={inp} value={form.facts_injection_strategy}
                onChange={(e) => set("facts_injection_strategy", e.target.value)}>
                {INJECTION_STRATEGIES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </Field>
          </div>
          <Field label="Fact Types">
            <div className="flex gap-2 flex-wrap mt-1">
              {FACT_TYPES.map((t) => (
                <Toggle key={t} active={form.facts_types.includes(t)}
                  onClick={() => toggleArray("facts_types", t)} label={t} />
              ))}
            </div>
          </Field>
        </Section>

        {/* Memory */}
        <Section title="Memory Strategy">
          <Field label="Strategy">
            {strategies ? (
              <select className={inp} value={form.memory_strategy}
                onChange={(e) => set("memory_strategy", e.target.value)}>
                {strategies.map((s) => (
                  <option key={s.name} value={s.name}>{s.name} — {s.description}</option>
                ))}
              </select>
            ) : <LoadingSpinner label="Loading…" />}
          </Field>
          {form.memory_strategy === "sliding_window" && (
            <Field label="Window Size (messages)">
              <input type="number" min="2" max="500" className={inp}
                value={form.memory_window_size} onChange={(e) => set("memory_window_size", parseInt(e.target.value, 10))} />
            </Field>
          )}
        </Section>

        {/* Recall */}
        <Section title="Recall Testing">
          <Field label="Intervals (comma-separated turn numbers)">
            <input className={inp} placeholder="10, 50, 100, 250, 500"
              value={form.recall_intervals} onChange={(e) => set("recall_intervals", e.target.value)} />
          </Field>
          <Field label="Scoring Methods">
            <div className="flex gap-2 flex-wrap mt-1">
              {SCORING_METHODS.map((m) => (
                <Toggle key={m} active={form.recall_scoring_methods.includes(m)}
                  onClick={() => toggleArray("recall_scoring_methods", m)} label={m} />
              ))}
            </div>
          </Field>
        </Section>

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={submitting}
            className="bg-primary text-primary-foreground px-6 py-2.5 rounded-md text-sm font-medium disabled:opacity-60 hover:opacity-90 transition">
            {submitting ? "Creating…" : "Create Experiment"}
          </button>
          <button type="button" onClick={() => router.back()}
            className="bg-secondary text-secondary-foreground px-6 py-2.5 rounded-md text-sm font-medium hover:opacity-90 transition">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

const inp = "w-full rounded-md border bg-secondary px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider border-b border-border pb-2">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs text-muted-foreground">{label}</label>
      {children}
    </div>
  );
}

function Toggle({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button type="button" onClick={onClick}
      className={`px-3 py-1 rounded-full text-xs border transition ${
        active
          ? "bg-primary/20 border-primary text-primary"
          : "border-border text-muted-foreground hover:border-primary/40"
      }`}>
      {label}
    </button>
  );
}
