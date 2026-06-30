# Adding a New Memory Strategy

This is the primary extension point of the framework.
Adding your Adaptive Hybrid Memory System (or any other strategy) requires only these steps.

## Step 1 — Create the strategy class

Create a new file in `backend/app/strategies/`:

```python
# backend/app/strategies/adaptive_hybrid.py
from app.strategies.base import MemoryStrategy
from app.domain.entities.message import Message

class AdaptiveHybridMemory(MemoryStrategy):

    def __init__(self, **params):
        # Initialize your memory system here
        ...

    @property
    def name(self) -> str:
        return "adaptive_hybrid"

    @property
    def description(self) -> str:
        return "Adaptive Hybrid Memory Management System."

    def build_context(self, messages, query=None) -> str:
        # Return the context string to inject into the LLM prompt
        ...

    def update_memory(self, message) -> None:
        # Update your internal state after each turn
        ...

    def retrieve(self, query, top_k=5) -> list[str]:
        # Return relevant memories for a given query
        ...

    def clear(self) -> None:
        # Reset state between experiments
        ...
```

## Step 2 — Register the strategy

In `backend/app/strategies/__init__.py`, add:

```python
from app.strategies.adaptive_hybrid import AdaptiveHybridMemory

def register_all_strategies() -> None:
    registry.register(NoMemoryStrategy)
    registry.register(SlidingWindowStrategy)
    registry.register(AdaptiveHybridMemory)   # ← add this line
```

## Step 3 — Run an experiment

Use your strategy by name in a config file:

```json
{
  "memory": {
    "strategy_name": "adaptive_hybrid",
    "strategy_params": {
      "param1": "value1"
    }
  }
}
```

Or via the API:

```bash
curl -X POST http://localhost:8000/api/v1/experiments \
  -H "Content-Type: application/json" \
  -d '{"config": {"name": "Test", "memory": {"strategy_name": "adaptive_hybrid"}}}'
```

## That's it.

No other files in the framework need to change.
The benchmark, pipeline, metrics engine, and visualization are all strategy-agnostic.
