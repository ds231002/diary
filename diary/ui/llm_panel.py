import streamlit as st
from llm.client import run_llm
from llm.prompts import PROMPTS
from db.crud import save_llm_result

def llm_panel(entry):
    st.header("LLM")

    prompt_key = st.selectbox("Prompt", PROMPTS.keys())
    model = st.selectbox("Model", ["gpt-4o", "gpt-4.1-mini"])

    if st.button("Run"):
        with st.spinner("LLM arbeitet…"):
            result = run_llm(
                text=entry.content,
                prompt=PROMPTS[prompt_key],
                model=model
            )

        st.subheader("Output")
        st.text_area("", result, height=300)

        if st.button("Speichern"):
            save_llm_result(entry.id, result, prompt_key, model)
