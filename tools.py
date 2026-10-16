import os
import requests
from langchain.tools import tool
from bs4 import BeautifulSoup
from tavily import TavilyClient
from rich import print
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# WEB SEARCH TOOL
@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information on a given topic. Returns Title, URL, and snippets.
    """
    result = tavily.search(query=query, max_results=3)

    output = []

    for r in result["results"]:
        # Tavily API uses 'content' key, not 'snippet'
        snippet = r.get('content') or r.get('snippet') or 'No preview available'
        output.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {snippet}\n"
        )

    return "\n----\n".join(output)

# WEB SCRAPING TOOL
@tool
def web_scrape(url: str) -> str:
    """
    Scrape and return clean text content from a given URL for deeper reading.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"