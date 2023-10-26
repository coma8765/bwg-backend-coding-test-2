from dataclasses import dataclass


@dataclass
class BinanceConfig:
    api_key: str
    api_secret: str
    target_currencies: list[tuple[str, str]]
    timeout: int = 1


__all__ = ["BinanceConfig"]
