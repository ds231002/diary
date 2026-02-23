import os
from dotenv import load_dotenv
import streamlit as st
from datetime import date

from db.crud.chats import (
    list_chats,
    create_chat,
    update_chat,
    delete_chat,
)
from db.crud.messages import (
    list_messages,
    create_message,
)

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Chats",
    layout="wide"
    )

# ==================================================
# USER HANDLING
# ==================================================

load_dotenv()
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")

if not st.session_state.get("active_user_id") and DEFAULT_USER_ID:
    st.session_state.active_user_id = DEFAULT_USER_ID

user_id = st.session_state.get("active_user_id")

if not user_id:
    st.warning("Bitte zuerst einen User auswählen.")
    st.stop()

# ==================================================
# SESSION STATE
# ==================================================

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "pending_new_chat" not in st.session_state:
    st.session_state.pending_new_chat = True

# ==================================================
# SIDEBAR – CHAT NAVIGATION
# ==================================================

with st.sidebar:

    st.title("Chats")

    if st.button("➕ Neuer Chat", use_container_width=True):
        st.session_state.current_chat_id = None
        st.session_state.pending_new_chat = True
        st.rerun()

    st.divider()

    chats = list_chats(user_id)

    for chat in chats:
        label = chat["title"] or f"Chat vom {chat['created_at'].date()}"

        is_active = chat["id"] == st.session_state.current_chat_id

        if st.button(
            ("👉 " if is_active else "") + label,
            key=f"chat_select_{chat['id']}",
            use_container_width=True,
        ):
            st.session_state.current_chat_id = chat["id"]
            st.session_state.pending_new_chat = False
            st.rerun()

# ==================================================
# MAIN CHAT AREA
# ==================================================

st.title("Chat")

# --------------------------------------------------
# FALL 1: Neuer Chat
# --------------------------------------------------

if st.session_state.pending_new_chat:

    st.subheader("Neuer Chat")
    st.info("Schreibe eine Nachricht, um den Chat zu starten.")
    messages = []

# --------------------------------------------------
# FALL 2: Existierender Chat
# --------------------------------------------------

else:

    chat_id = st.session_state.current_chat_id
    messages = list_messages(chat_id, user_id)

    current_chat = next(
        (c for c in chats if c["id"] == chat_id),
        None
    )

    title = current_chat["title"] or "Chat"

    col1, col2 = st.columns([8, 1])

    with col1:
        st.subheader(title)

    with col2:
        if st.button("⚙", key="edit_chat_settings"):
            st.session_state.edit_chat_mode = True

    # ----------------------------------------------
    # EDIT MODE
    # ----------------------------------------------

    if st.session_state.get("edit_chat_mode"):

        with st.expander("Chat bearbeiten", expanded=True):

            new_title = st.text_input(
                "Titel",
                value=current_chat["title"] or "",
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Speichern"):
                    update_chat(
                        chat_id=chat_id,
                        user_id=user_id,
                        title=new_title.strip() or None,
                    )
                    st.session_state.edit_chat_mode = False
                    st.success("Titel aktualisiert.")
                    st.rerun()

            with c2:
                if st.button("Löschen"):
                    delete_chat(chat_id, user_id)
                    st.session_state.current_chat_id = None
                    st.session_state.pending_new_chat = True
                    st.session_state.edit_chat_mode = False
                    st.success("Chat gelöscht.")
                    st.rerun()

# ==================================================
# CHAT VERLAUF
# ==================================================

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==================================================
# CHAT INPUT
# ==================================================

prompt = st.chat_input("Nachricht schreiben...")

if prompt:

    # --------------------------------------------------
    # Neuer Chat → jetzt erst anlegen
    # --------------------------------------------------

    if st.session_state.pending_new_chat:

        new_chat = create_chat(
            user_id=user_id,
            title=None,
            start_date=date.today(),
        )

        st.session_state.current_chat_id = new_chat["id"]
        st.session_state.pending_new_chat = False

        chat_id = new_chat["id"]

    else:
        chat_id = st.session_state.current_chat_id

    # Nachricht speichern
    create_message(
        chat_id=chat_id,
        user_id=user_id,
        role="user",
        content=prompt,
    )

    st.rerun()
