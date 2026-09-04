import streamlit as st
import os
from dotenv import load_dotenv
from datetime import date

from db.crud.user_profiles import (
    get_user_profile,
    upsert_user_profile,
)

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(layout="wide")

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

st.title("Profil")

# ==================================================
# PROFIL LADEN
# ==================================================

profile = get_user_profile(user_id)

# Falls noch kein Profil existiert → leere Defaults
first_name = profile["first_name"] if profile else ""
last_name = profile["last_name"] if profile else ""
birth_date = profile["birth_date"] if profile else None
summary = profile["summary"] if profile else ""

# ==================================================
# FORM
# ==================================================

with st.form("profile_form"):

    st.subheader("Persönliche Daten")

    col1, col2 = st.columns(2)

    with col1:
        first_name_input = st.text_input(
            "Vorname",
            value=first_name or ""
        )

    with col2:
        last_name_input = st.text_input(
            "Nachname",
            value=last_name or ""
        )

    birth_date_input = st.date_input(
        "Geburtsdatum",
        value=birth_date if birth_date else None
    )

    st.subheader("Über mich")

    summary_input = st.text_area(
        "Kurzbeschreibung",
        value=summary or "",
        height=150
    )

    submitted = st.form_submit_button("Speichern")

    if submitted:

        upsert_user_profile(
            user_id=user_id,
            first_name=first_name_input.strip() or None,
            last_name=last_name_input.strip() or None,
            birth_date=birth_date_input,
            summary=summary_input.strip() or None,
        )

        st.success("Profil gespeichert.")
        st.rerun()
