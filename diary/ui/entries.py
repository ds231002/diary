import streamlit as st
from db.crud import get_entries

def entries_view():
    st.header("Einträge")

    entries = get_entries(limit=50)

    selected = st.selectbox(
        "Eintrag auswählen",
        entries,
        format_func=lambda e: f"{e.id} – {e.created_at:%Y-%m-%d}"
    )

    if selected:
        st.text_area(
            "Text",
            value=selected.content,
            height=300
        )

    return selected
