# 🔎 AI Research Agent

Enter a research topic and a single **CrewAI** agent searches the web with **DuckDuckGo**, analyses what it finds, and writes a structured Markdown report using **Groq** (`openai/gpt-oss-120b`). The UI is built with **Streamlit**.

## Features
- One CrewAI agent (research analyst) with a free DuckDuckGo search tool, no search API key needed
- Structured report: summary, key findings, evidence with source URLs, other perspectives, limitations, conclusion
- Friendly error messages (missing/invalid key, rate limit, network, empty topic)
- Download the report as `.md`
- Ready for GitHub and Streamlit Community Cloud

## How it works
```text
User topic -> Streamlit (app.py) -> CrewAI agent (research_agent.py)
   -> DuckDuckGo search tool -> web results -> agent analysis
   -> Groq LLM (openai/gpt-oss-120b) -> report -> Streamlit
```

## Project structure
```text
ai-research-agent/
├── app.py                  # Streamlit interface
├── research_agent.py       # CrewAI agent, search tool, Groq config
├── test_agent.py           # Run the agent without Streamlit
├── requirements.txt
├── .gitignore
├── .env.example            # copy to .env (local only)
└── .streamlit/
    └── secrets.toml.example  # copy to secrets.toml (local only)
```

## Installation
Use **Python 3.11 or 3.12** (CrewAI supports 3.10 to 3.13).
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## API key
Get a free key at https://console.groq.com (API Keys -> Create).

**Local:** copy `.env.example` to `.env` and set `GROQ_API_KEY=your_key`.
(Or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.)

**Streamlit Cloud:** Manage app -> Settings -> Secrets, then paste:
```toml
GROQ_API_KEY = "your_key"
```
Never commit `.env` or `secrets.toml`. They are in `.gitignore`.

## Run locally
Test the agent first:
```bash
python test_agent.py "Impact of AI on education"
```
Then the app:
```bash
streamlit run app.py
```
Open http://localhost:8501.

## Deploy
1. Push to GitHub:
```bash
git init
git add .
git status          # make sure .env / secrets.toml are NOT listed
git commit -m "Initial AI Research Agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-research-agent.git
git push -u origin main
```
2. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**.
3. Pick the repository, branch `main`, main file `app.py`.
4. **Advanced settings:** choose Python 3.12 (or 3.11) and paste your `GROQ_API_KEY` in Secrets.
5. Click **Deploy**. The first build takes several minutes. Use **Manage app** to see logs.

## Troubleshooting
| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the virtual environment; on Cloud check requirements.txt spelling. |
| CrewAI install/import fails | Use Python 3.11 or 3.12, not 3.14. |
| Invalid API key / 401 | Recopy the key; check quotes in Secrets. |
| Model not found | Check the current model list at https://console.groq.com/docs/models and edit `MODEL_NAME`. |
| Rate limit / 429 | Wait a minute; shorter topics use fewer tokens. |
| DuckDuckGo returns nothing | The free search is sometimes rate-limited. Retry after a short wait. |
| Missing secrets on Cloud | Add `GROQ_API_KEY` in Settings -> Secrets, then reboot the app. |

## Limitations
- Free DuckDuckGo search can be rate-limited and returns snippets, not full pages.
- The agent only sees search snippets, so details may be shallow; always verify important claims.
- Reports are not saved between sessions (download them).

## Future improvements
- Read full web pages (a scraping tool), save report history, add a second "fact-checker" agent, streaming progress, PDF export.
