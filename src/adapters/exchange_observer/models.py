from dataclasses import dataclass


@dataclass
class ExchangeRate:
    exchanger: str
    currencies: tuple[str, str]
    value: float

    @property
    def direction(self) -> str:
        return "-".join(self.currencies)
