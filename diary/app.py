import streamlit as st
from db.crud.users import (
    list_users,
    create_user,
    delete_user,
    update_user,
)

st.set_page_config(
    page_title="Diary – User Auswahl",
    layout="wide"
)

st.title("Diary")

users = list_users()
active_user_id = st.session_state.get("active_user_id")

st.subheader("User")

if not users:
    st.info("Noch keine User vorhanden.")
else:
    for user in users:

        is_active = (active_user_id == user["id"])

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

            with col1:
                name_row = st.columns([3, 2])

                with name_row[0]:
                    name_style = (
                        "color:#27ae60;"
                        if is_active else ""
                    )

                    st.markdown(
                        f"<span style='font-size:1.2rem;font-weight:600;{name_style}'>"
                        f"{user['user_name']}</span>",
                        unsafe_allow_html=True
                    )

                with name_row[1]:
                    if is_active:
                        st.markdown(
                            "<span style='background-color:#e8f8f1;"
                            "color:#27ae60;padding:4px 8px;"
                            "border-radius:6px;font-size:0.75rem;'>"
                            "Aktiver User</span>",
                            unsafe_allow_html=True
                        )

                st.caption(f"ID: {user['id']}")

            with col2:
                if st.button("Öffnen", key=f"open_{user['id']}"):
                    st.session_state.active_user_id = user["id"]
                    st.switch_page("pages/01_entries.py")

            with col3:
                if st.button("✏️", key=f"rename_toggle_{user['id']}"):
                    st.session_state[f"rename_{user['id']}"] = True

            with col4:
                if st.button("🗑", key=f"delete_toggle_{user['id']}"):
                    st.session_state[f"confirm_delete_{user['id']}"] = True

            if st.session_state.get(f"rename_{user['id']}"):

                new_name = st.text_input(
                    "Neuer Name",
                    key=f"rename_input_{user['id']}"
                )

                if st.button(
                    "Speichern",
                    key=f"rename_save_{user['id']}"
                ):
                    if new_name.strip():
                        update_user(
                            user["id"],
                            user_name=new_name.strip()
                        )
                        st.session_state.pop(
                            f"rename_{user['id']}",
                            None
                        )
                        st.success("User umbenannt.")
                        st.rerun()
                    else:
                        st.warning("Name darf nicht leer sein.")

            if st.session_state.get(f"confirm_delete_{user['id']}"):

                st.error(
                    "⚠️ Dieser User und alle zugehörigen Einträge "
                    "und Tags werden dauerhaft gelöscht."
                )

                st.markdown(
                    f"Gib zur Bestätigung den Namen "
                    f"**{user['user_name']}** ein:"
                )

                confirm_input = st.text_input(
                    "Usernamen eingeben",
                    key=f"confirm_input_{user['id']}"
                )

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        "Endgültig löschen",
                        key=f"confirm_delete_btn_{user['id']}"
                    ):
                        if confirm_input == user["user_name"]:
                            delete_user(user["id"])

                            if (
                                st.session_state.get("active_user_id")
                                == user["id"]
                            ):
                                st.session_state.pop(
                                    "active_user_id",
                                    None
                                )

                            st.success("User wurde gelöscht.")
                            st.rerun()
                        else:
                            st.warning(
                                "Name stimmt nicht überein."
                            )

                with c2:
                    if st.button(
                        "Abbrechen",
                        key=f"cancel_delete_{user['id']}"
                    ):
                        st.session_state.pop(
                            f"confirm_delete_{user['id']}",
                            None
                        )
                        st.rerun()

st.divider()

st.subheader("Neuen User erstellen")

new_user_name = st.text_input("User Name")

if st.button("User erstellen"):
    if new_user_name.strip():
        create_user(new_user_name.strip())
        st.success("User erstellt.")
        st.rerun()
    else:
        st.warning("Bitte Namen eingeben.")
