from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar('T')


class QueueMessage(Enum):
    PAYLOAD = 1
    DONE = 2
    ERROR = 3


@dataclass
class Task(Generic[T]):
    payload: T = None
    message: QueueMessage = QueueMessage.PAYLOAD