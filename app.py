import os

import streamlit as st
from dotenv import load_dotenv

from research_agent import ResearchError, run_research

load_dotenv()  # reads a local .env file if it exists (ignored on Streamlit Cloud)

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="wide")


def get_api_key():
    """Streamlit Secrets first (cloud / .streamlit/secrets.toml), then environment/.env."""
    try:
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        key = None
    return key or os.environ.get("GROQ_API_KEY")


st.session_state.setdefault("report", None)
st.session_state.setdefault("topic", "")

st.title("🔎 AI Research Agent")
st.caption(
    "Enter a topic. One CrewAI agent searches the web with DuckDuckGo and writes a structured "
    "report using Groq (openai/gpt-oss-120b)."
)

api_key = get_api_key()
if not api_key:
    st.error(
        "GROQ_API_KEY is missing. Locally: put it in a .env file. "
        "On Streamlit Cloud: Manage app → Settings → Secrets."
    )
    st.stop()

topic = st.text_area(
    "Research topic",
    placeholder="What is the impact of artificial intelligence on education?",
    height=100,
)

if st.button("Start Research", type="primary"):
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        with st.status("Researching... this can take 1-3 minutes.", expanded=True) as status:
            st.write("Agent is searching the web and analysing sources...")
            try:
                st.session_state.report = run_research(topic, api_key)
                st.session_state.topic = topic.strip()
                status.update(label="Research complete", state="complete", expanded=False)
            except ResearchError as exc:
                st.session_state.report = None
                status.update(label="Research failed", state="error")
                st.error(str(exc))
            except Exception:
                st.session_state.report = None
                status.update(label="Research failed", state="error")
                st.error("Unexpected error. Check the app logs and try again.")

if st.session_state.report:
    st.divider()
    st.markdown(st.session_state.report)
    st.download_button(
        "Download report (.md)",
        data=st.session_state.report,
        file_name="research_report.md",
        mime="text/markdown",
    )
