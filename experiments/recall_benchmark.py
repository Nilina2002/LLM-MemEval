#!/usr/bin/env python3
"""
Minimal Fact Recall Benchmark
==============================
Tests whether a chatbot forgets injected facts over 100 conversation turns.

Key design choice — sliding context window:
  Both modes use the same CONTEXT_WINDOW_TURNS window when calling the LLM.
  Once the conversation grows past that window, facts injected at turn 0
  fall out of the context. Baseline has no recovery mechanism; LlamaIndex
  retrieves the facts from an external index and re-injects them at recall time.

Modes:
  baseline   — no external memory, context window only
  llamaindex — facts stored in vector index at turn 0, retrieved at recall turns

Usage:
    cd LLM-MemEval
    python experiments/recall_benchmark.py --mode both
    python experiments/recall_benchmark.py --mode baseline --model llama3.2 --seed 42
    python experiments/recall_benchmark.py --mode llamaindex --model llama3.2
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# ─────────────────────────────────────────────────────────────────────────────
# Ground-truth facts  (fixed for all runs — the "what was told to the model")
# ─────────────────────────────────────────────────────────────────────────────

FACTS: dict[str, tuple[str, str]] = {
    # key → (ground_truth_answer, recall_question)
    "name":     ("Nilina",      "What is my name?"),
    "language": ("Python",      "What programming language do I prefer?"),
    "location": ("Colombo",     "Where do I live?"),
    "domain":   ("AI research", "What is my favorite domain or area of interest?"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Experiment parameters
# ─────────────────────────────────────────────────────────────────────────────

RECALL_TURNS        = [10, 50, 100]   # turns where recall is tested
TOTAL_TURNS         = 100             # total filler + recall turns
CONTEXT_WINDOW      = 20             # LLM sees only the last N turn-pairs
                                      # facts fall out of window after ~turn 20
DEFAULT_MODEL       = "llama3"
DEFAULT_TEMPERATURE = 0.7
OLLAMA_BASE_URL     = "http://localhost:11434"

RESULTS_DIR = Path(__file__).parent.parent / "results" / "recall_benchmark"

SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant in a casual conversation. "
    "Be concise. Remember everything the user tells you about themselves."
)

# ─────────────────────────────────────────────────────────────────────────────
# Filler topics — shuffled deterministically per seed
# ─────────────────────────────────────────────────────────────────────────────

FILLER_TOPICS = [
    "Tell me something interesting about machine learning.",
    "What are your thoughts on open source software?",
    "Can you explain what a neural network does in simple terms?",
    "What are some good practices for writing clean code?",
    "How does the internet work at a basic level?",
    "What is the difference between supervised and unsupervised learning?",
    "Can you give me a simple example of a sorting algorithm?",
    "What makes a programming language well-suited for data science?",
    "How do large language models generate text?",
    "What is the difference between RAM and disk storage?",
    "What are some popular Python libraries used in research?",
    "How do version control systems like Git work?",
    "What is the purpose of a REST API?",
    "Can you explain what containerization means?",
    "What are the main differences between Python 2 and Python 3?",
    "How does gradient descent work in machine learning?",
    "What is a transformer architecture in deep learning?",
    "What are some common challenges in natural language processing?",
    "How do relational databases store and retrieve data efficiently?",
    "What is the difference between a stack and a queue?",
    "Can you explain what recursion is with a short example?",
    "What are the benefits of using type hints in Python?",
    "How does caching improve application performance?",
    "What is a microservices architecture and when is it useful?",
    "How do you evaluate the performance of a machine learning model?",
    "What is the difference between precision and recall in classification?",
    "Can you explain what a confusion matrix is?",
    "What are word embeddings in the context of NLP?",
    "How does the attention mechanism work in transformers?",
    "What is the difference between deep learning and traditional machine learning?",
    "Can you explain what overfitting means and how to avoid it?",
    "How do you handle missing data in a dataset?",
    "What is feature engineering and why does it matter?",
    "What are hyperparameters and how do you tune them?",
    "What is the difference between a list and a tuple in Python?",
    "How does asynchronous programming work in Python?",
    "What are decorators in Python and what are they used for?",
    "What is the difference between SQL and NoSQL databases?",
    "How do recommendation systems work in general?",
    "What is transfer learning and why is it useful?",
    "Can you explain what BERT is and what it does?",
    "How does tokenization work in natural language processing?",
    "What is the difference between batch and online learning?",
    "What are activation functions in neural networks?",
    "How does backpropagation work?",
    "What is the vanishing gradient problem?",
    "What is regularization and when is it needed?",
    "What is the difference between generative and discriminative models?",
    "How does k-means clustering work?",
    "What is principal component analysis used for?",
    "How does a decision tree make predictions?",
    "What is an ensemble method in machine learning?",
    "What is the difference between bagging and boosting?",
    "How does a random forest algorithm work?",
    "What are recurrent neural networks typically used for?",
    "How does LSTM differ from a standard RNN?",
    "What is a convolutional neural network and what is it good at?",
    "What are generative adversarial networks?",
    "How does reinforcement learning work at a high level?",
    "What is semantic search and how is it different from keyword search?",
    "How do vector databases work?",
    "What is retrieval-augmented generation?",
    "What are some challenges of deploying ML models in production?",
    "What is model drift and how do you detect it?",
    "How does A/B testing work for evaluating ML models?",
    "What is the difference between a model and an algorithm?",
    "How do you measure the quality of text generation?",
    "What is the BLEU score used for?",
    "What is zero-shot learning?",
    "What is few-shot learning and how does it differ from fine-tuning?",
    "How does in-context learning work in large language models?",
    "What is prompt engineering?",
    "What are chain-of-thought prompts?",
    "How does fine-tuning differ from pre-training a language model?",
    "What is parameter-efficient fine-tuning?",
    "What are quantized models and why are they useful?",
    "How does knowledge distillation work?",
    "What is the difference between inference and training in ML?",
    "What hardware is commonly used to train large AI models?",
    "What is multi-head attention in transformers?",
    "What is positional encoding and why do transformers need it?",
    "How does beam search work in text generation?",
    "What is temperature in the context of language model sampling?",
    "What is top-k and top-p sampling?",
    "How do you evaluate hallucinations in large language models?",
    "What is the difference between open-source and proprietary LLMs?",
    "What are some ethical concerns around large AI models?",
    "How can AI tools support scientific research?",
    "What is the difference between AI, machine learning, and deep learning?",
    "How does a language model learn grammar and syntax?",
    "What is semantic similarity and how is it measured?",
    "What are knowledge graphs and how are they used in AI?",
    "What is the role of data augmentation in machine learning?",
    "How does cross-validation work?",
    "What is the bias-variance tradeoff?",
    "What is the F1 score and when do you use it instead of accuracy?",
    "How does self-supervised learning differ from supervised learning?",
    "What is contrastive learning?",
    "How do attention heads specialize in transformer models?",
]


# ─────────────────────────────────────────────────────────────────────────────
# Ollama helper
# ─────────────────────────────────────────────────────────────────────────────

async def _chat(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
) -> str:
    payload = {
        "model":   model,
        "messages": messages,
        "options": {"temperature": temperature},
        "stream":  False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()


# ─────────────────────────────────────────────────────────────────────────────
# Shared utilities
# ─────────────────────────────────────────────────────────────────────────────

def _fact_injection_message() -> str:
    return (
        "Here are some things about me I'd like you to remember:\n"
        f"- My name is {FACTS['name'][0]}.\n"
        f"- My preferred programming language is {FACTS['language'][0]}.\n"
        f"- I live in {FACTS['location'][0]}.\n"
        f"- My favorite domain is {FACTS['domain'][0]}.\n"
        "Please keep these in mind throughout our conversation."
    )


def _is_correct(fact_key: str, model_answer: str) -> bool:
    """Exact-substring match: ground truth present anywhere in model answer."""
    return FACTS[fact_key][0].lower() in model_answer.lower()


def _window(history: list[dict], n_turns: int) -> list[dict]:
    """Slice the last n_turns turn-pairs (2 messages each) from history."""
    return history[-(n_turns * 2):]


def _fact_status(history: list[dict]) -> str:
    """Debug helper — are the original fact messages still in the window?"""
    windowed = _window(history, CONTEXT_WINDOW)
    return "IN  window" if len(windowed) < len(history) - 1 else "IN  window"


# ─────────────────────────────────────────────────────────────────────────────
# Mode A — Baseline
# ─────────────────────────────────────────────────────────────────────────────

class BaselineRunner:
    """
    No external memory.

    The fact injection message sits at position 0 in the conversation history.
    Once the conversation exceeds CONTEXT_WINDOW turns, those messages are
    excluded from the LLM prompt and the model has no way to recall them.
    """

    def __init__(self, model: str, temperature: float, seed: int) -> None:
        self.model       = model
        self.temperature = temperature
        self.history:    list[dict[str, str]] = []
        self.log:        list[dict[str, Any]] = []
        self._rng        = random.Random(seed)

    async def run(self) -> dict[str, Any]:
        print("\n── BASELINE  ──────────────────────────────────────────────────")
        await self._inject_facts()

        topics      = list(FILLER_TOPICS)
        self._rng.shuffle(topics)
        topic_cycle = iter(topics * 3)

        recall_results: dict[int, dict] = {}

        for turn in range(1, TOTAL_TURNS + 1):
            if turn in RECALL_TURNS:
                recall_results[turn] = await self._recall_checkpoint(turn)
            else:
                await self._filler_turn(turn, next(topic_cycle))
                if turn % 10 == 0:
                    n_msgs     = len(self.history)
                    fact_in_wnd = n_msgs <= CONTEXT_WINDOW * 2 + 2
                    status     = "facts IN window" if fact_in_wnd else "facts OUT of window"
                    print(f"  Turn {turn:3d} | history={n_msgs//2} pairs | {status}")

        return self._build_result(recall_results)

    async def _inject_facts(self) -> None:
        msg = _fact_injection_message()
        self.history.append({"role": "user", "content": msg})
        reply = await _chat(
            [{"role": "system", "content": SYSTEM_PROMPT}] + self.history,
            self.model, self.temperature,
        )
        self.history.append({"role": "assistant", "content": reply})
        self.log.append({"turn": 0, "type": "fact_injection",
                         "user": msg, "assistant": reply})
        print(f"  Turn   0 | Facts injected into conversation history.")

    async def _filler_turn(self, turn: int, topic: str) -> None:
        self.history.append({"role": "user", "content": topic})
        prompt = [{"role": "system", "content": SYSTEM_PROMPT}] + _window(self.history, CONTEXT_WINDOW)
        reply  = await _chat(prompt, self.model, self.temperature)
        self.history.append({"role": "assistant", "content": reply})
        self.log.append({"turn": turn, "type": "filler",
                         "user": topic, "assistant": reply[:120]})

    async def _recall_checkpoint(self, turn: int) -> dict:
        print(f"  Turn {turn:3d} | RECALL TEST ─────────────────────────────")
        results: dict[str, Any] = {}
        for fact_key, (expected, question) in FACTS.items():
            self.history.append({"role": "user", "content": question})
            prompt = [{"role": "system", "content": SYSTEM_PROMPT}] + _window(self.history, CONTEXT_WINDOW)
            answer = await _chat(prompt, self.model, temperature=0.0)
            self.history.append({"role": "assistant", "content": answer})

            correct = _is_correct(fact_key, answer)
            mark    = "✓" if correct else "✗"
            print(f"    {mark} [{fact_key:8s}] expected={expected!r:12s} | got: {answer[:60]!r}")
            results[fact_key] = {
                "question": question, "expected": expected,
                "answer": answer[:200], "correct": correct,
            }
            self.log.append({
                "turn": turn, "type": "recall", "fact_key": fact_key,
                "question": question, "expected": expected,
                "answer": answer[:200], "correct": correct,
            })
        return {"turn": turn, "results": results}

    def _build_result(self, recall_results: dict[int, dict]) -> dict[str, Any]:
        checkpoints, n_correct, n_total = {}, 0, 0
        for t in RECALL_TURNS:
            r   = recall_results.get(t, {}).get("results", {})
            ok  = sum(1 for v in r.values() if v["correct"])
            tot = len(r)
            acc = round(ok / tot, 3) if tot else 0.0
            checkpoints[f"turn_{t}"] = {
                "accuracy": acc, "correct": ok, "total": tot, "detail": r,
            }
            n_correct += ok
            n_total   += tot
        return {
            "mode":                  "baseline",
            "model":                 self.model,
            "total_turns":           TOTAL_TURNS,
            "context_window_turns":  CONTEXT_WINDOW,
            "recall_turns":          RECALL_TURNS,
            "checkpoints":           checkpoints,
            "overall": {
                "total_correct": n_correct,
                "total_tests":   n_total,
                "accuracy": round(n_correct / n_total, 3) if n_total else 0.0,
            },
            "log": self.log,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Mode B — LlamaIndex
# ─────────────────────────────────────────────────────────────────────────────

class LlamaIndexRunner:
    """
    LlamaIndex-augmented memory.

    At turn 0 the four facts are loaded into an in-memory VectorStoreIndex
    (using a local HuggingFace embedding model — no API key needed).

    The sliding context window is identical to the baseline.  The only
    difference: at each recall checkpoint the question is sent to the
    retriever first, and the retrieved context is prepended to the system
    prompt before calling the LLM.
    """

    def __init__(self, model: str, temperature: float, seed: int) -> None:
        self.model       = model
        self.temperature = temperature
        self.history:    list[dict[str, str]] = []
        self.log:        list[dict[str, Any]] = []
        self._rng        = random.Random(seed)
        self._retriever  = None

    # ── Index setup ──────────────────────────────────────────────────────────

    def _build_index(self) -> None:
        try:
            from llama_index.core import VectorStoreIndex, Document, Settings
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        except ImportError as exc:
            sys.exit(
                f"\n[LlamaIndex] Missing dependency: {exc}\n"
                "Install:  pip install llama-index-embeddings-huggingface\n"
            )

        print("[LlamaIndex] Loading local embedding model (BAAI/bge-small-en-v1.5)…")
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.llm = None     # LLM inference handled by _chat()

        documents = [
            Document(text=f"The user's name is {FACTS['name'][0]}."),
            Document(text=f"The user's preferred programming language is {FACTS['language'][0]}."),
            Document(text=f"The user lives in {FACTS['location'][0]}."),
            Document(text=f"The user's favorite domain is {FACTS['domain'][0]}."),
        ]
        index            = VectorStoreIndex.from_documents(documents)
        self._retriever  = index.as_retriever(similarity_top_k=4)
        print("[LlamaIndex] Fact index ready. 4 documents stored.\n")

    def _retrieve(self, question: str) -> str:
        nodes = self._retriever.retrieve(question)
        if not nodes:
            return ""
        lines = ["[Retrieved context]\n"] + [f"- {n.text}" for n in nodes]
        return "\n".join(lines)

    # ── Main run ─────────────────────────────────────────────────────────────

    async def run(self) -> dict[str, Any]:
        self._build_index()
        print("── LLAMAINDEX  ────────────────────────────────────────────────")
        await self._inject_facts()

        topics      = list(FILLER_TOPICS)
        self._rng.shuffle(topics)
        topic_cycle = iter(topics * 3)

        recall_results: dict[int, dict] = {}

        for turn in range(1, TOTAL_TURNS + 1):
            if turn in RECALL_TURNS:
                recall_results[turn] = await self._recall_checkpoint(turn)
            else:
                await self._filler_turn(turn, next(topic_cycle))
                if turn % 10 == 0:
                    print(f"  Turn {turn:3d} | Conversation continues. "
                          f"(Index available regardless of window.)")

        return self._build_result(recall_results)

    async def _inject_facts(self) -> None:
        msg = _fact_injection_message()
        self.history.append({"role": "user", "content": msg})
        reply = await _chat(
            [{"role": "system", "content": SYSTEM_PROMPT}] + self.history,
            self.model, self.temperature,
        )
        self.history.append({"role": "assistant", "content": reply})
        self.log.append({"turn": 0, "type": "fact_injection",
                         "user": msg, "assistant": reply})
        print(f"  Turn   0 | Facts injected into conversation and indexed.")

    async def _filler_turn(self, turn: int, topic: str) -> None:
        self.history.append({"role": "user", "content": topic})
        prompt = [{"role": "system", "content": SYSTEM_PROMPT}] + _window(self.history, CONTEXT_WINDOW)
        reply  = await _chat(prompt, self.model, self.temperature)
        self.history.append({"role": "assistant", "content": reply})
        self.log.append({"turn": turn, "type": "filler",
                         "user": topic, "assistant": reply[:120]})

    async def _recall_checkpoint(self, turn: int) -> dict:
        print(f"  Turn {turn:3d} | RECALL TEST (+ LlamaIndex retrieval) ──────")
        results: dict[str, Any] = {}
        for fact_key, (expected, question) in FACTS.items():
            retrieved = self._retrieve(question)
            system    = f"{retrieved}\n\n{SYSTEM_PROMPT}" if retrieved else SYSTEM_PROMPT

            self.history.append({"role": "user", "content": question})
            prompt = [{"role": "system", "content": system}] + _window(self.history, CONTEXT_WINDOW)
            answer = await _chat(prompt, self.model, temperature=0.0)
            self.history.append({"role": "assistant", "content": answer})

            correct = _is_correct(fact_key, answer)
            mark    = "✓" if correct else "✗"
            print(f"    {mark} [{fact_key:8s}] expected={expected!r:12s} | got: {answer[:60]!r}")
            results[fact_key] = {
                "question":          question,
                "expected":          expected,
                "answer":            answer[:200],
                "correct":           correct,
                "retrieved_context": retrieved,
            }
            self.log.append({
                "turn": turn, "type": "recall", "fact_key": fact_key,
                "question": question, "expected": expected,
                "answer": answer[:200], "correct": correct,
                "retrieved_context": retrieved,
            })
        return {"turn": turn, "results": results}

    def _build_result(self, recall_results: dict[int, dict]) -> dict[str, Any]:
        checkpoints, n_correct, n_total = {}, 0, 0
        for t in RECALL_TURNS:
            r   = recall_results.get(t, {}).get("results", {})
            ok  = sum(1 for v in r.values() if v["correct"])
            tot = len(r)
            acc = round(ok / tot, 3) if tot else 0.0
            checkpoints[f"turn_{t}"] = {
                "accuracy": acc, "correct": ok, "total": tot, "detail": r,
            }
            n_correct += ok
            n_total   += tot
        return {
            "mode":                  "llamaindex",
            "model":                 self.model,
            "total_turns":           TOTAL_TURNS,
            "context_window_turns":  CONTEXT_WINDOW,
            "recall_turns":          RECALL_TURNS,
            "checkpoints":           checkpoints,
            "overall": {
                "total_correct": n_correct,
                "total_tests":   n_total,
                "accuracy": round(n_correct / n_total, 3) if n_total else 0.0,
            },
            "log": self.log,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Output — printing and saving
# ─────────────────────────────────────────────────────────────────────────────

def _save(result: dict[str, Any], run_id: str) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    mode = result["mode"]

    summary      = {k: v for k, v in result.items() if k != "log"}
    summary_path = RESULTS_DIR / f"{run_id}_{mode}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log_path = RESULTS_DIR / f"{run_id}_{mode}_log.jsonl"
    with log_path.open("w", encoding="utf-8") as f:
        for entry in result.get("log", []):
            f.write(json.dumps(entry) + "\n")

    return summary_path, log_path


def _print_result(result: dict[str, Any]) -> None:
    mode = result["mode"].upper()
    print(f"\n{'═'*62}")
    print(f"  {mode}  |  model={result['model']}  |  context window={result['context_window_turns']} turns")
    print(f"{'═'*62}")
    for cp_key, cp in result["checkpoints"].items():
        label = cp_key.replace("turn_", "Turn ")
        bar   = "█" * round(cp["accuracy"] * 20)
        print(f"  {label:6s}  {bar:<20s}  {cp['accuracy']*100:5.1f}%  "
              f"({cp['correct']}/{cp['total']})")
    ov = result["overall"]
    print(f"\n  Overall   {ov['accuracy']*100:5.1f}%  ({ov['total_correct']}/{ov['total_tests']})")
    print(f"{'═'*62}")


def _print_comparison(baseline: dict, llamaindex: dict) -> None:
    print(f"\n{'═'*62}")
    print("  COMPARISON — BASELINE vs LLAMAINDEX")
    print(f"  Context window: {CONTEXT_WINDOW} turns  (facts fall out after ~turn {CONTEXT_WINDOW})")
    print(f"{'─'*62}")
    print(f"  {'Turn':>6s}   {'Baseline':>9s}   {'LlamaIndex':>10s}   {'Delta':>7s}")
    print(f"  {'─'*6}   {'─'*9}   {'─'*10}   {'─'*7}")
    for t in RECALL_TURNS:
        key   = f"turn_{t}"
        b_acc = baseline["checkpoints"].get(key, {}).get("accuracy", 0.0)
        l_acc = llamaindex["checkpoints"].get(key, {}).get("accuracy", 0.0)
        delta = l_acc - b_acc
        sign  = "+" if delta >= 0 else ""
        print(f"  {t:6d}   {b_acc*100:8.1f}%   {l_acc*100:9.1f}%   "
              f"{sign}{delta*100:5.1f}%")
    print(f"{'═'*62}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fact recall benchmark: baseline vs LlamaIndex memory"
    )
    parser.add_argument(
        "--mode", choices=["baseline", "llamaindex", "both"], default="both",
        help="Which mode to run (default: both)",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL}). Run 'ollama list' to see available models.",
    )
    parser.add_argument(
        "--temperature", type=float, default=DEFAULT_TEMPERATURE,
        help=f"Sampling temperature for filler turns (default: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for deterministic topic ordering (default: 42)",
    )
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    print(f"\nFact Recall Benchmark")
    print(f"  run_id  : {run_id}")
    print(f"  model   : {args.model}")
    print(f"  seed    : {args.seed}")
    print(f"  window  : {CONTEXT_WINDOW} turns")
    print(f"  facts   : {', '.join(f'{k}={v[0]}' for k, v in FACTS.items())}")
    print(f"  recall  : turns {RECALL_TURNS}")

    collected: list[dict] = []

    if args.mode in ("baseline", "both"):
        t0  = time.monotonic()
        res = await BaselineRunner(args.model, args.temperature, args.seed).run()
        res["elapsed_seconds"] = round(time.monotonic() - t0, 1)
        _print_result(res)
        sp, lp = _save(res, run_id)
        print(f"  → {sp.name}")
        print(f"  → {lp.name}")
        collected.append(res)

    if args.mode in ("llamaindex", "both"):
        t0  = time.monotonic()
        res = await LlamaIndexRunner(args.model, args.temperature, args.seed).run()
        res["elapsed_seconds"] = round(time.monotonic() - t0, 1)
        _print_result(res)
        sp, lp = _save(res, run_id)
        print(f"  → {sp.name}")
        print(f"  → {lp.name}")
        collected.append(res)

    if len(collected) == 2:
        _print_comparison(collected[0], collected[1])
        combined = {
            "run_id":     run_id,
            "model":      args.model,
            "seed":       args.seed,
            "baseline":   {k: v for k, v in collected[0].items() if k != "log"},
            "llamaindex": {k: v for k, v in collected[1].items() if k != "log"},
        }
        cp = RESULTS_DIR / f"{run_id}_combined.json"
        cp.write_text(json.dumps(combined, indent=2), encoding="utf-8")
        print(f"\n  Combined → {cp.name}")


if __name__ == "__main__":
    asyncio.run(main())
