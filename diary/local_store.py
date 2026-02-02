import json
from pathlib import Path
from datetime import datetime
from .repository import EntryRepository
from .entry import DiaryEntry

DATA_DIR = Path("data/entries")

class JsonEntryRepository(EntryRepository):

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def add(self, entry: DiaryEntry):
        path = DATA_DIR / f"{entry.id}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump({
                "id": entry.id,
                "created_at": entry.created_at.isoformat(),
                "entry_date": entry.entry_date,
                "text": entry.text,
                "mood": entry.mood,
                "tags": entry.tags
            }, f, ensure_ascii=False, indent=2)

    def list(self):
        entries = []
        for file in DATA_DIR.glob("*.json"):
            data = json.loads(file.read_text(encoding="utf-8"))
            entries.append(
                DiaryEntry(
                    id=data["id"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    entry_date=data["entry_date"],
                    text=data["text"],
                    mood=data.get("mood"),
                    tags=data.get("tags", [])
                )
            )
        return sorted(entries, key=lambda e: e.entry_date)
