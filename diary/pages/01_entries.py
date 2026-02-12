import streamlit as st
import os
from dotenv import load_dotenv
from datetime import date

from db.crud.entries import (
    list_entries_by_user,
    update_entry,
    delete_entry,
    create_entry,
)
from db.crud.tags import list_tags_by_user
from db.crud.entry_tags import (
    list_tags_for_entry,
    sync_entry_tags,
)

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(layout="wide")

# ==================================================
# DEFAULT USER
# ==================================================

load_dotenv()
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")

if not st.session_state.get("active_user_id") and DEFAULT_USER_ID:
    st.session_state.active_user_id = DEFAULT_USER_ID

user_id = st.session_state.get("active_user_id")

if not user_id:
    st.warning("Bitte zuerst einen User auswählen.")
    st.stop()

st.title("Entries")

# ==================================================
# DATEN LADEN
# ==================================================

all_tags = list_tags_by_user(user_id)
tag_map = {t["name"]: t["id"] for t in all_tags}

# ==================================================
# TABS
# ==================================================

tab_edit, tab_create = st.tabs(["📝 Bearbeiten", "➕ Neuer Eintrag"])

# ==================================================
# TAB 1 — BEARBEITEN
# ==================================================

with tab_edit:

    # ----------------------------------------------
    # FILTER
    # ----------------------------------------------

    with st.expander("🔎 Filter", expanded=False):

        f1, f2, f3 = st.columns(3)

        with f1:
            from_date = st.date_input(
                "Von",
                value=None,
                key="filter_from"
            )

        with f2:
            to_date = st.date_input(
                "Bis",
                value=None,
                key="filter_to"
            )

        with f3:
            filter_tag_names = st.multiselect(
                "Tags",
                list(tag_map.keys()),
                key="filter_tags"
            )

        filter_tag_ids = [tag_map[name] for name in filter_tag_names]

    # ----------------------------------------------
    # ENTRIES LADEN
    # ----------------------------------------------

    entries = list_entries_by_user(
        user_id,
        from_date=from_date,
        to_date=to_date,
    )

    # Tag-Filter clientseitig
    if filter_tag_ids:
        filtered = []
        for entry in entries:
            entry_tags = list_tags_for_entry(entry["id"])
            entry_tag_ids = [t["id"] for t in entry_tags]

            if any(tid in entry_tag_ids for tid in filter_tag_ids):
                filtered.append(entry)

        entries = filtered

    if not entries:
        st.info("Keine Einträge gefunden.")
        st.stop()

    # ----------------------------------------------
    # AUSWAHL
    # ----------------------------------------------

    entry_map = {
        f"{e['entry_date']} – {e['content'][:100]}": e
        for e in entries
    }

    selected_label = st.selectbox(
        "Eintrag auswählen",
        list(entry_map.keys()),
        key="edit_select"
    )

    selected_entry = entry_map[selected_label]

    st.divider()

    # ----------------------------------------------
    # FORMULAR
    # ----------------------------------------------

    left, right = st.columns([1, 3])

    entry_tags = list_tags_for_entry(selected_entry["id"])
    default_tag_names = [t["name"] for t in entry_tags]

    with left:

        entry_date_input = st.date_input(
            "Datum",
            value=selected_entry["entry_date"],
            key=f"edit_date_{selected_entry['id']}"
        )

        tag_selection = st.multiselect(
            "Tags",
            list(tag_map.keys()),
            default=default_tag_names,
            key=f"edit_tags_{selected_entry['id']}"
        )

        tag_ids = [tag_map[name] for name in tag_selection]

        use_mood = st.checkbox(
            "Mood speichern",
            value=selected_entry.get("mood") is not None,
            key=f"edit_use_mood_{selected_entry['id']}"
        )

        if use_mood:
            mood_input = st.slider(
                "Mood",
                1,
                10,
                selected_entry.get("mood") or 5,
                key=f"edit_mood_{selected_entry['id']}"
            )
        else:
            mood_input = None

        st.divider()

        # -----------------------------
        # SPEICHERN
        # -----------------------------

        if st.button("Speichern", key=f"save_{selected_entry['id']}"):

            update_entry(
                selected_entry["id"],
                entry_date=entry_date_input,
                content=st.session_state[f"edit_content_{selected_entry['id']}"],
                mood=mood_input,
            )

            sync_entry_tags(
                selected_entry["id"],
                tag_ids
            )

            st.success("Eintrag gespeichert.")
            st.rerun()

        # -----------------------------
        # LÖSCHEN MIT CONFIRM
        # -----------------------------

        confirm_key = f"confirm_delete_{selected_entry['id']}"

        if confirm_key not in st.session_state:
            st.session_state[confirm_key] = False

        if not st.session_state[confirm_key]:

            if st.button("Löschen", key=f"delete_btn_{selected_entry['id']}"):
                st.session_state[confirm_key] = True
                st.rerun()

        else:

            st.error("⚠️ Dieser Eintrag wird dauerhaft gelöscht.")

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Endgültig löschen",
                    key=f"confirm_delete_btn_{selected_entry['id']}"
                ):
                    delete_entry(selected_entry["id"])
                    st.session_state[confirm_key] = False
                    st.success("Eintrag gelöscht.")
                    st.rerun()

            with c2:
                if st.button(
                    "Abbrechen",
                    key=f"cancel_delete_{selected_entry['id']}"
                ):
                    st.session_state[confirm_key] = False
                    st.rerun()

    with right:

        st.text_area(
            "Content",
            value=selected_entry["content"],
            height=500,
            key=f"edit_content_{selected_entry['id']}"
        )

# ==================================================
# TAB 2 — NEUER EINTRAG
# ==================================================

with tab_create:

    left, right = st.columns([1, 3])

    default_tag_names = [
        t["name"] for t in all_tags if t.get("favourite")
    ]

    with left:

        entry_date_input = st.date_input(
            "Datum",
            value=date.today(),
            key="create_date"
        )

        use_mood = st.checkbox(
            "Mood speichern",
            value=False,
            key="create_use_mood"
        )

        if use_mood:
            mood_input = st.slider(
                "Mood",
                1,
                10,
                5,
                key="create_mood"
            )
        else:
            mood_input = None

        tag_selection = st.multiselect(
            "Tags",
            list(tag_map.keys()),
            default=default_tag_names,
            key="create_tags"
        )

        tag_ids = [tag_map[name] for name in tag_selection]

        st.divider()

        if st.button("Eintrag erstellen", key="create_save"):

            content_value = st.session_state["create_content"]

            if content_value.strip():

                create_entry(
                    user_id,
                    entry_date=entry_date_input,
                    content=content_value,
                    mood=mood_input,
                    tag_ids=tag_ids
                )

                st.success("Eintrag erstellt.")
                st.rerun()

            else:
                st.warning("Content darf nicht leer sein.")

    with right:

        st.text_area(
            "Content",
            value="",
            height=500,
            key="create_content"
        )
