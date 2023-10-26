import time
from dataclasses import dataclass, field
from typing import TypeVar, Generic
from uuid import uuid4, UUID

T = TypeVar("T")


@dataclass
class Event(Generic[T]):
    channel: str
    data: T

    issues_at: float = field(default_factory=time.time)
    id: UUID = field(default_factory=uuid4)
