from dataclasses import dataclass


@dataclass
class CoingeckoConfig:
    target_currencies: list[tuple[str, str]]
    delay: int = 1


__all__ = ["CoingeckoConfig"]
