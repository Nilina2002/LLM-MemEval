"""
ExperimentConfig — the single object that fully describes one benchmark run.
Every experiment is deterministically reproducible from this config alone.
"""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


class LLMConfig(BaseModel):
    provider: Literal["openai", "claude", "gemini", "groq", "ollama", "openrouter", "llamaindex"] = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, gt=0)
    seed: int | None = None
    api_key_env_var: str | None = None     # e.g. "OPENAI_API_KEY" — read from env
    base_url: str | None = None            # for Ollama / OpenRouter overrides


class ConversationConfig(BaseModel):
    domain: Literal["casual", "programming", "education", "travel", "shopping", "mixed"] = "casual"
    total_turns: int = Field(default=200, gt=0)
    seed: int = 42
    allow_topic_drift: bool = True


class FactConfig(BaseModel):
    count: int = Field(default=10, gt=0)
    types: list[str] = Field(default=["personal", "technical", "temporal"])
    injection_strategy: Literal["uniform", "early", "late", "random"] = "uniform"
    difficulty_range: tuple[float, float] = (0.2, 0.8)
    seed: int = 42


class MemoryConfig(BaseModel):
    strategy_name: str = "no_memory"
    strategy_params: dict[str, Any] = Field(default_factory=dict)


class RecallConfig(BaseModel):
    intervals: list[int] = Field(default=[10, 50, 100, 250, 500, 1000])
    scoring_methods: list[Literal["exact", "fuzzy", "embedding", "llm_judge"]] = ["fuzzy", "embedding"]
    scoring_threshold: float = Field(default=0.8, ge=0.0, le=1.0)

    @field_validator("intervals")
    @classmethod
    def intervals_must_be_sorted(cls, v: list[int]) -> list[int]:
        return sorted(set(v))


class OutputConfig(BaseModel):
    output_dir: str = "results"
    export_json: bool = True
    export_csv: bool = False
    save_prompts: bool = True
    save_raw_responses: bool = False


class ExperimentConfig(BaseModel):
    """
    Complete specification for one benchmark run.
    Serialize to JSON and pass to /experiments POST endpoint.
    """
    name: str
    description: str = ""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    facts: FactConfig = Field(default_factory=FactConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    recall: RecallConfig = Field(default_factory=RecallConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json_file(cls, path: str) -> "ExperimentConfig":
        import json
        with open(path) as f:
            return cls.model_validate(json.load(f))
