from abc import ABC, abstractmethod
from typing import List
from .entry import DiaryEntry

class EntryRepository(ABC):

    @abstractmethod
    def add(self, entry: DiaryEntry) -> None:
        pass

    @abstractmethod
    def list(self) -> List[DiaryEntry]:
        pass