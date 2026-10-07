"""Core research agent: one CrewAI agent + a DuckDuckGo search tool + Groq LLM.

This file has NO Streamlit code, so you can test it on its own (see test_agent.py).
"""
import os

# Turn off CrewAI's anonymous telemetry (must be set before importing crewai).
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

from crewai import LLM, Agent, Crew, Process, Task  # noqa: E402
from crewai.tools import tool  # noqa: E402
from ddgs import DDGS  # noqa: E402

# "groq/" tells CrewAI which provider to use. "openai/gpt-oss-120b" is the model name on Groq.
MODEL_NAME = "groq/openai/gpt-oss-120b"


class ResearchError(Exception):
    """An error whose message is safe to show to the user."""


# ---------------------------------------------------------------------------
# Tool: DuckDuckGo web search (free, no API key)
# ---------------------------------------------------------------------------
@tool("DuckDuckGo Web Search")
def web_search(query: str) -> str:
    """Search the web with DuckDuckGo. Input: a short search query.
    Returns a list of results with title, URL and a text snippet."""
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as exc:  # DuckDuckGo can rate-limit or fail; tell the agent, don't crash
        return f"Search failed ({type(exc).__name__}). Try a different or shorter query."
    if not results:
        return "No results found. Try rephrasing the query."
    lines = []
    for r in results:
        snippet = (r.get("body") or "")[:400]
        lines.append(f"Title: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {snippet}")
    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Build and run the crew
# ---------------------------------------------------------------------------
def _build_crew(api_key: str) -> Crew:
    llm = LLM(model=MODEL_NAME, api_key=api_key, temperature=0.2, max_tokens=4000)

    agent = Agent(
        role="Senior Research Analyst",
        goal=(
            "Research the topic '{topic}' using web search and write an accurate, "
            "well-structured research report based only on what the sources say."
        ),
        backstory=(
            "You are a careful research analyst. You search several times with different "
            "queries, compare sources, never invent facts or URLs, and clearly say when "
            "evidence is weak, missing or contradictory."
        ),
        tools=[web_search],
        llm=llm,
        allow_delegation=False,
        max_iter=8,
        verbose=False,
    )

    task = Task(
        description=(
            "Research this topic: {topic}\n\n"
            "Steps:\n"
            "1. Run 3 to 5 web searches with different queries (overview, recent developments, "
            "evidence/statistics, criticism or other viewpoints).\n"
            "2. Use ONLY information found in the search results. Do not invent facts, numbers or URLs.\n"
            "3. Cross-check claims across sources where possible.\n"
            "4. Clearly separate facts (from sources) from your own analysis.\n"
            "5. If reliable information is missing, say so explicitly."
        ),
        expected_output=(
            "A Markdown research report with exactly these sections:\n"
            "# Research Report: <topic>\n"
            "## Executive Summary (3-5 sentences)\n"
            "## Introduction\n"
            "## Key Findings (bullet points)\n"
            "## Detailed Analysis\n"
            "## Evidence and Facts (each with its source URL)\n"
            "## Different Perspectives\n"
            "## Limitations and Uncertainty\n"
            "## Conclusion\n"
            "## Sources (list of URLs actually found in the search results)"
        ),
        agent=agent,
    )

    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)


def friendly_error(exc: Exception) -> str:
    """Turn technical errors into short, safe messages (no keys, no stack traces)."""
    text = f"{type(exc).__name__} {exc}".lower()
    if any(k in text for k in ("authentication", "invalid_api_key", "invalid api key", "401")):
        return "Groq rejected the API key. Check that GROQ_API_KEY is correct."
    if ("rate" in text and "limit" in text) or "429" in text:
        return "Groq rate limit reached. Wait a minute and try again, or use a shorter topic."
    if any(k in text for k in ("model_not_found", "decommissioned", "does not exist", "404")):
        return "The Groq model was not found. Check MODEL_NAME in research_agent.py."
    if any(k in text for k in ("connection", "timeout", "timed out", "network")):
        return "Network problem or timeout while contacting Groq/DuckDuckGo. Please try again."
    return "Something went wrong while researching. Check the app logs and try again."


def run_research(topic: str, api_key: str | None) -> str:
    """Run the research agent and return the report as Markdown text."""
    topic = (topic or "").strip()
    if not topic:
        raise ResearchError("Please enter a research topic.")
    if not api_key:
        raise ResearchError("GROQ_API_KEY is missing. See the README for how to add it.")
    if len(topic) > 500:
        raise ResearchError("Topic is too long. Please keep it under 500 characters.")

    try:
        result = _build_crew(api_key).kickoff(inputs={"topic": topic})
    except Exception as exc:
        raise ResearchError(friendly_error(exc)) from exc

    report = (getattr(result, "raw", None) or str(result)).strip()
    if not report:
        raise ResearchError("The agent returned an empty report. Please try again.")
    return report
