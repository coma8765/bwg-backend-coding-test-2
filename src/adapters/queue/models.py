"""Models for HTTP request adapter"""
import time
from dataclasses import dataclass, field
from typing import Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


@dataclass
class Event(Generic[T]):
    channel: str
    data: T

    issues_at: float = field(default_factory=time.time)
    id: UUID = field(default_factory=uuid4)
