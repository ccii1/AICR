from dataclasses import dataclass


@dataclass
class AICRConfig:
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    top_k: int = 3
    max_tokens_per_day: int = 2_000_000
