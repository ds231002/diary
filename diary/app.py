import streamlit as st
from ui.entries import entries_view
from ui.llm_panel import llm_panel
from ui.sidebar import sidebar

st.set_page_config(layout="wide")

sidebar()

col1, col2 = st.columns([2, 3])

with col1:
    selected_entry = entries_view()

with col2:
    if selected_entry:
        llm_panel(selected_entry)
