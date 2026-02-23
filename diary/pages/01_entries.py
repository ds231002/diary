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
from db.crud.entry_tags import sync_entry_tags

load_dotenv()


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Einträge",
    layout="wide"
    )


# --------------------------------------------------
# USER
# --------------------------------------------------

DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")

if not st.session_state.get("active_user_id") and DEFAULT_USER_ID:
    st.session_state.active_user_id = DEFAULT_USER_ID

user_id = st.session_state.get("active_user_id")

if not user_id:
    st.warning("Bitte zuerst einen User auswählen.")
    st.stop()

user_id = st.session_state.get("active_user_id")

if not user_id:
    user_id = os.getenv("DEFAULT_USER_ID")

if not user_id:
    st.warning("Bitte zuerst einen User auswählen.")
    st.stop()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

all_tags = list_tags_by_user(user_id)
tag_map = {t["name"]: t["id"] for t in all_tags}
favourite_tag_names = [
    t["name"] for t in all_tags if t.get("favourite")
]


# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------

# if "previous_selected_id" not in st.session_state:
#     st.session_state["previous_selected_id"] = None

if st.session_state.get("reset_to_create"):
    st.session_state["entry_selector"] = None
    st.session_state["create_tags"] = favourite_tag_names.copy()
    st.session_state["create_content"] = ""
    st.session_state["create_llm_allowed"] = True
    st.session_state["reset_to_create"] = False


# ==================================================
# HEADER
# ==================================================

st.title("Einträge")


# --------------------------------------------------
# FILTER
# --------------------------------------------------

with st.expander("🔎 Filter", expanded=False):

    f1, f2, f3 = st.columns([1, 1, 3])

    with f1:
        from_date = st.date_input("Von", value=None, key="filter_from")

    with f2:
        to_date = st.date_input("Bis", value=None, key="filter_to")

    with f3:

        UNTAGGED_OPTION = "— Ohne Tags —"
        tag_options = [UNTAGGED_OPTION] + list(tag_map.keys())

        filter_tag_names = st.multiselect(
            "Tags",
            tag_options,
            key="filter_tags",
        )

        include_untagged = UNTAGGED_OPTION in filter_tag_names

        selected_real_tags = [
            name for name in filter_tag_names
            if name != UNTAGGED_OPTION
        ]

        filter_tag_ids = (
            [tag_map[name] for name in selected_real_tags]
            if selected_real_tags
            else None
        )

        if include_untagged and not selected_real_tags:
            filter_tag_ids = []


# --------------------------------------------------
# SELECT ENTRIES
# --------------------------------------------------

entries = list_entries_by_user(
    user_id,
    from_date=from_date,
    to_date=to_date,
    tag_ids=filter_tag_ids,
    include_untagged=include_untagged,
)

if not entries:
    st.info("Keine Einträge gefunden.")

entry_options = {
    e["id"]: f"{e['entry_date']} – {e['content'][:50]}"
    for e in entries
}

# entry_options = {
#     e["id"]: f"{e['id']} | {e['entry_date']} – {e['content'][:100]}"
#     for e in entries
# }

def load_entry_into_state():
    selected_id = st.session_state["entry_selector"]

    if selected_id is None:
        return

    selected_entry = next(
        (e for e in entries if e["id"] == selected_id),
        None
    )

    if selected_entry:
        st.session_state["edit_date"] = selected_entry["entry_date"]
        st.session_state["edit_tags"] = [
            t["name"] for t in selected_entry["tags"]
        ]
        st.session_state["edit_content"] = selected_entry["content"]
        st.session_state["edit_llm_allowed"] = selected_entry["llm_allowed"]
        st.session_state["confirm_delete"] = False

selected_id = st.selectbox(
    "Eintrag auswählen",
    options=[None] + list(entry_options.keys()),
    format_func=lambda item: (
        "— Neuer Eintrag —"
        if item is None
        else entry_options[item]
    ),
    key="entry_selector",
    on_change=load_entry_into_state
)

st.write("Selected ID:", selected_id)

# if st.button("➕ Neuer Eintrag", use_container_width=True):
#     st.session_state["entry_selector"] = None
#     st.rerun()

st.divider()


# ==================================================
# CREATE
# ==================================================

def render_create_form():

    entry_date_col, entry_tags_col = st.columns([1, 3])

    with entry_date_col:
        entry_date_input = st.date_input(
            "Datum",
            value=date.today(),
            key="create_date"
        )

    with entry_tags_col:

        if "create_tags" not in st.session_state:
            st.session_state["create_tags"] = favourite_tag_names.copy()

        tag_selection = st.multiselect(
            "Tags",
            options=list(tag_map.keys()),
            key="create_tags"
        )

        tag_ids = [tag_map[name] for name in tag_selection]

    if "create_content" not in st.session_state:
        st.session_state["create_content"] = ""

    st.text_area(
        "Content",
        height=500,
        key="create_content"
    )

    if "create_llm_allowed" not in st.session_state:
        st.session_state["create_llm_allowed"] = True

    llm_allowed = st.checkbox(
        "Für KI-Reflexion verwenden",
        key="create_llm_allowed"
    )

    if st.button("Eintrag erstellen", use_container_width=True):

        content_value = st.session_state["create_content"]

        if content_value.strip():

            create_entry(
                user_id,
                entry_date=entry_date_input,
                content=content_value,
                tag_ids=tag_ids,
                llm_allowed=llm_allowed
            )

            st.session_state["reset_to_create"] = True
            st.success("Eintrag erstellt.")
            st.rerun()

        else:
            st.warning("Content darf nicht leer sein.")


# ==================================================
# EDIT
# ==================================================

def render_edit_form():

    entry_date_col, entry_tags_col = st.columns([1, 3])

    with entry_date_col:

        st.date_input("Datum", key=f"edit_date")

    with entry_tags_col:

        tag_selection = st.multiselect(
            "Tags",
            options=list(tag_map.keys()),
            key="edit_tags"
        )

        tag_ids = [tag_map[name] for name in tag_selection]

    st.text_area(
        "Content",
        height=500,
        key="edit_content"
    )

    st.checkbox(
        "Für KI-Reflexion verwenden",
        key="edit_llm_allowed"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Speichern", use_container_width=True):

            update_entry(
                selected_id,
                user_id,
                entry_date=st.session_state["edit_date"],
                content=st.session_state["edit_content"],
                llm_allowed=st.session_state["edit_llm_allowed"]
            )

            sync_entry_tags(
                selected_id,
                user_id,
                tag_ids
            )

            st.session_state["reset_to_create"] = True
            st.success("Eintrag gespeichert.")
            st.rerun()

    with col2:

        if not st.session_state["confirm_delete"]:

            if st.button("Löschen", use_container_width=True):
                st.session_state["confirm_delete"] = True
                st.rerun()

        else:

            st.error("⚠️ Dieser Eintrag wird dauerhaft gelöscht.")

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Endgültig löschen"):
                    delete_entry(selected_id, user_id)

                    st.session_state["reset_to_create"] = True
                    st.success("Eintrag gelöscht.")              
                    st.rerun()

            with c2:
                if st.button("Abbrechen"):
                    st.session_state["confirm_delete"] = False
                    st.rerun()


# ==================================================
# FORM RENDER
# ==================================================

if selected_id is None:
    render_create_form()
else:
    render_edit_form()
