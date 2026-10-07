"""Test the agent WITHOUT Streamlit:  python test_agent.py "your topic" """
import os
import sys

from dotenv import load_dotenv

from research_agent import ResearchError, run_research

load_dotenv()
topic = " ".join(sys.argv[1:]) or "Impact of artificial intelligence on education"
print(f"Researching: {topic}\n(this can take 1-3 minutes)\n")
try:
    print(run_research(topic, os.environ.get("GROQ_API_KEY")))
except ResearchError as exc:
    print("ERROR:", exc)
