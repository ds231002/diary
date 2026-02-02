from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import uuid

@dataclass
class DiaryEntry:
    id: str
    created_at: datetime
    entry_date: str
    text: str
    mood: Optional[int] = None
    tags: List[str] = None

    @staticmethod
    def create(text: str, entry_date: str, mood=None, tags=None):
        return DiaryEntry(
            id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            entry_date=entry_date,
            text=text,
            mood=mood,
            tags=tags or []
        )