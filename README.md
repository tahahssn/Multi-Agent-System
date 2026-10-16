# Multi-Agent Research

A web research assistant that searches the web, reads a relevant source, writes a structured report, and asks a critic agent to review it. Use the Streamlit chat interface to enter a topic and inspect or download the results.

## Features

- Searches the web with Tavily and returns up to three results.
- Selects a relevant result and extracts readable page text.
- Uses an OpenRouter-hosted chat model to write a report with an introduction, key findings, conclusion, and sources.
- Reviews the report and returns a score, strengths, areas to improve, and a verdict.
- Shows the report, critic feedback, search results, and scraped text in the app.
- Streams the report into the chat and provides a Markdown download.
- Can also run as an interactive command-line program.

## Requirements

- Python 3.10 or newer
- An [OpenRouter API key](https://openrouter.ai/keys)
- A [Tavily API key](https://app.tavily.com/home)

The application makes external API requests to OpenRouter and Tavily and needs an internet connection. Provider availability, rate limits, and applicable API usage charges may apply.

## Setup

From the project directory, create and activate a virtual environment in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the placeholders with your own keys:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Keep `.env` private. It is excluded from Git; `.env.example` contains placeholders only.

## Run the web app

```powershell
python -m streamlit run app.py
```

Streamlit prints a local URL in the terminal. Open it in a browser, enter a topic in the chat input, and wait for the search, reading, writing, and review steps to finish. The result view includes expandable sections for the critic feedback, search results, and scraped content.

## Run from the command line

```powershell
python pipeline.py
```

Enter a research topic when prompted. The program prints the generated report and critic feedback in the terminal.

## How it works

1. **Search:** `search_agent` calls the Tavily-backed `web_search` tool for up to three results.
2. **Read:** `scrape_agent` chooses a URL from the search results and calls `web_scrape` to fetch and extract page text.
3. **Write:** `writer_chain` combines the search results and scraped text into a structured research report.
4. **Review:** `critic_chain` evaluates the report and returns a score and written feedback.

The orchestration lives in `research_pipeline` in `pipeline.py`. `agents.py` configures the agents and report/critic chains; `tools.py` implements web search and scraping; `app.py` provides the Streamlit interface.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit chat interface, progress display, report rendering, and Markdown download |
| `pipeline.py` | Runs the search, reading, writing, and review steps; includes the CLI entry point |
| `agents.py` | Configures the OpenRouter chat model, LangChain agents, and prompt chains |
| `tools.py` | Tavily web-search and HTTP page-scraping tools |
| `requirements.txt` | Python dependencies |
| `.env.example` | Placeholder names for required local API keys |

## Current limitations

- Search is limited to three results per topic.
- The reader agent is given at most the first 800 characters of the search results when choosing a URL.
- Scraped page text is truncated to 3,000 characters.
- The scraper uses a direct HTTP request; pages that require JavaScript, authentication, or block automated requests may not be readable.
- The chat model is configured as `openrouter/free`. Its availability and behavior depend on OpenRouter's model routing.
- The application displays pipeline exceptions in the UI; it does not currently persist reports or conversation history between sessions.
