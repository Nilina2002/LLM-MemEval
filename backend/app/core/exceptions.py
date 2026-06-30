"""
Domain and application exceptions.
Use specific exception types so callers can handle failures precisely.
"""


class MemEvalBaseException(Exception):
    """Base exception for all framework errors."""


class ExperimentNotFoundError(MemEvalBaseException):
    def __init__(self, experiment_id: str) -> None:
        super().__init__(f"Experiment '{experiment_id}' not found.")
        self.experiment_id = experiment_id


class ExperimentAlreadyRunningError(MemEvalBaseException):
    def __init__(self, experiment_id: str) -> None:
        super().__init__(f"Experiment '{experiment_id}' is already running.")


class StrategyNotFoundError(MemEvalBaseException):
    def __init__(self, strategy_name: str) -> None:
        super().__init__(
            f"Memory strategy '{strategy_name}' is not registered. "
            "Register it in strategies/registry.py."
        )
        self.strategy_name = strategy_name


class LLMProviderError(MemEvalBaseException):
    """Raised when an LLM provider call fails."""


class ScoringError(MemEvalBaseException):
    """Raised when a scoring method fails."""


class ConfigurationError(MemEvalBaseException):
    """Raised for invalid experiment configurations."""


class FactInjectionError(MemEvalBaseException):
    """Raised when fact injection fails."""
