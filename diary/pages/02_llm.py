import streamlit as st
from datetime import date

st.set_page_config(layout="wide")

st.title("LLM Chats")

# ==================================================
# SESSION STATE INITIALISIERUNG
# ==================================================

if "llm_chats" not in st.session_state:
    st.session_state.llm_chats = {
        "Erster Chat": []
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Erster Chat"

# ==================================================
# LAYOUT
# ==================================================

left, right = st.columns([1, 3])

# ==================================================
# LINKER BEREICH – CHAT MANAGEMENT
# ==================================================

with left:

    st.subheader("Chats")

    # Chat Auswahl
    selected_chat = st.radio(
        "Chat auswählen",
        list(st.session_state.llm_chats.keys()),
        key="chat_selector"
    )

    st.session_state.active_chat = selected_chat

    st.divider()

    # Neuer Chat
    new_chat_name = st.text_input("Neuer Chat Name")

    if st.button("Chat erstellen"):
        if new_chat_name and new_chat_name not in st.session_state.llm_chats:
            st.session_state.llm_chats[new_chat_name] = []
            st.session_state.active_chat = new_chat_name
            st.rerun()

# ==================================================
# RECHTER BEREICH – CHAT INTERFACE
# ==================================================

with right:

    st.subheader(f"Chat: {st.session_state.active_chat}")

    # ----------------------------------------------
    # KONTEXT FILTER (Platzhalter)
    # ----------------------------------------------

    with st.expander("🔎 Kontext Filter", expanded=False):

        col1, col2 = st.columns(2)

        with col1:
            from_date = st.date_input("Von", value=None)

        with col2:
            to_date = st.date_input("Bis", value=None)

        st.multiselect("Tags", ["Arbeit", "Freunde", "Sport"])

        st.info("Hier wird später konfiguriert, welche Entries als Kontext genutzt werden.")

    st.divider()

    # ----------------------------------------------
    # CHAT HISTORY
    # ----------------------------------------------

    chat_history = st.session_state.llm_chats[st.session_state.active_chat]

    for message in chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

    st.divider()

    # ----------------------------------------------
    # PROMPT EINGABE
    # ----------------------------------------------

    user_input = st.chat_input("Nachricht eingeben...")

    if user_input:

        # User Message speichern
        chat_history.append({
            "role": "user",
            "content": user_input
        })

        # Dummy-Antwort (Backend kommt später)
        chat_history.append({
            "role": "assistant",
            "content": "Dies ist eine Platzhalter-Antwort."
        })

        st.rerun()
