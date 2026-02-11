import streamlit as st
from dataclasses import dataclass
from datetime import datetime
from ui.entries import entries_view

st.set_page_config(layout="wide")

@dataclass
class Entry:
    id: int
    created_at: datetime
    updated_at: datetime
    start_date: datetime
    end_date: datetime
    content: str

ENTRIES = [
    Entry(1, datetime.now(), datetime.now(), datetime.now(), None, "Erster Tagebucheintrag"),
    Entry(2, datetime.now(), datetime.now(), datetime.now(), None, "Zweiter Eintrag"),
]

st.title("Diary – LLM Playground")

left, right = st.columns([2, 3])

with left:
    selected = entries_view(ENTRIES)

with right:
    if selected:
        st.text_area("Text", selected.content, height=300)

