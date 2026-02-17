import streamlit as st
import os
from dotenv import load_dotenv

from db.crud.tags import (
    list_tags_by_user,
    create_tag,
    update_tag,
    delete_tag,
)

st.set_page_config(layout="wide")

# --------------------------------------------------
# DEFAULT USER FALLBACK
# --------------------------------------------------

load_dotenv()
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")

if not st.session_state.get("active_user_id") and DEFAULT_USER_ID:
    st.session_state.active_user_id = DEFAULT_USER_ID

user_id = st.session_state.get("active_user_id")

if not user_id:
    st.warning("Bitte zuerst einen User auswählen.")
    st.stop()

# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("Tags")

st.subheader("Tag Management")

tags = list_tags_by_user(user_id)

if not tags:
    st.info("Keine Tags vorhanden.")
else:
    for tag in tags:

        with st.container(border=True):

            col1, col2, col3 = st.columns([6, 1, 1])

            # ------------------------------
            # TAG NAME + BADGE
            # ------------------------------

            with col1:
                name_row = st.columns([3, 2])

                with name_row[0]:
                    name_style = (
                        f"color:{tag['color']};"
                        if tag.get("color") else ""
                    )

                    st.markdown(
                        f"<span style='font-size:1.1rem;"
                        f"font-weight:600;{name_style}'>"
                        f"{tag['name']}</span>",
                        unsafe_allow_html=True
                    )

                with name_row[1]:
                    if tag.get("favourite"):
                        st.markdown(
                            "<span style='background-color:#fef5e7;"
                            "color:#d35400;padding:4px 8px;"
                            "border-radius:6px;font-size:0.75rem;'>"
                            "Favorit</span>",
                            unsafe_allow_html=True
                        )

                st.caption(f"ID: {tag['id']}")

            # ------------------------------
            # EDIT
            # ------------------------------

            with col2:                    
                if st.button("✏️", key=f"edit_btn_{tag['id']}"):
                    st.session_state[f"edit_tag_{tag['id']}"] = True
            # ------------------------------
            # DELETE TOGGLE
            # ------------------------------

            with col3:
                if st.button("🗑", key=f"delete_btn_{tag['id']}"):
                    st.session_state[f"delete_confirm_open_{tag['id']}"] = True

            # ------------------------------
            # EDIT SECTION
            # ------------------------------

            if st.session_state.get(f"edit_tag_{tag['id']}"):

                new_name = st.text_input(
                    "Name",
                    value=tag["name"],
                    key=f"name_input_{tag['id']}"
                )

                new_description = st.text_area(
                    "Beschreibung",
                    value=tag.get("description") or "",
                    key=f"description_input_{tag['id']}"
                )

                new_color = st.text_input(
                    "Farbe (z.B. #ff0000)",
                    value=tag.get("color") or "",
                    key=f"color_input_{tag['id']}"
                )

                new_fav = st.checkbox(
                    "Favorit",
                    value=tag.get("favourite") or False,
                    key=f"fav_input_{tag['id']}"
                )

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        "Speichern",
                        key=f"save_tag_{tag['id']}"
                    ):
                        update_tag(
                            tag_id=tag["id"],
                            user_id=user_id,
                            name=new_name.strip(),
                            description=new_description.strip() or None,
                            color=new_color.strip() or None,
                            favourite=new_fav,
                        )

                        st.session_state.pop(
                            f"edit_tag_{tag['id']}",
                            None
                        )

                        st.success("Tag aktualisiert.")
                        st.rerun()

            # ------------------------------
            # DELETE CONFIRM
            # ------------------------------

            if st.session_state.get(f"delete_confirm_open_{tag['id']}"):

                st.error("⚠️ Dieser Tag wird dauerhaft gelöscht.")

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        "Endgültig löschen",
                        key=f"confirm_delete_btn_{tag['id']}"
                    ):
                        delete_tag(tag["id"], user_id)

                        # State zurücksetzen
                        st.session_state.pop(
                            f"delete_confirm_open_{tag['id']}",
                            None
                        )

                        st.success("Tag gelöscht.")
                        st.rerun()

                with c2:
                    if st.button(
                        "Abbrechen",
                        key=f"cancel_delete_btn_{tag['id']}"
                    ):
                        st.session_state.pop(
                            f"delete_confirm_open_{tag['id']}",
                            None
                        )
                        st.rerun()

st.divider()

# ------------------------------
# TAG ERSTELLEN
# ------------------------------

st.subheader("Neuen Tag erstellen")

new_tag_name = st.text_input("Name")
new_tag_description = st.text_area("Beschreibung (optional)")
new_tag_color = st.text_input("Farbe (optional)")
# new_tag_position = st.number_input(
#     "Position",
#     value=0,
#     step=1
# )
new_tag_fav = st.checkbox("Favorit")

if st.button("Tag erstellen"):
    if new_tag_name.strip():
        create_tag(
            user_id,
            name=new_tag_name.strip(),
            description=new_tag_description.strip() or None,
            color=new_tag_color.strip() or None,
            # position=new_tag_position,
            favourite=new_tag_fav,
        )
        st.success("Tag erstellt.")
        st.rerun()
    else:
        st.warning("Bitte Namen eingeben.")
