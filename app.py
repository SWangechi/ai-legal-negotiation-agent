import streamlit as st
from frontend.ui import run_ui

if __name__ == "__main__":
    st.set_page_config(page_title="⚖️ AI Legal Negotiation & Mediation Agent", layout="wide")
    run_ui()
