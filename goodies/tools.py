from pathlib import Path
import shutil

from ddgs import DDGS

def web_news_search(query: str) -> list[dict]:
    """
    Searches the live web specifically for recent news articles, breaking updates, 
    and press releases. Use this if the user asks for 'news', 'latest events', or 'recent updates'.
    """
    print("Gemini is searching NEWS:", query)
    try:
        # DDGS().news returns results with 'title', 'url', 'body', 'date', and 'source'
        results = DDGS().news(query, max_results=10)
        
        # Format it cleanly so Gemini gets a uniform list of results
        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r.get("title"),
                "href": r.get("url"), # Renamed url to href to keep it consistent for your UI links
                "body": r.get("body")
            })
        return formatted_results
    except Exception as e:
        print(f"News search failed: {e}")
        return []


def web_search(query: str) -> list[dict]:
    """
    Searches the live web for general information, guides, and articles. 
    Returns a list of dictionaries with title, href, and body.
    """
    print("Gemini is searching text:", query)
    try:
        return DDGS().text(query, max_results=22)
    except Exception as e:
        print(f"Text search failed: {e}")
        return []

def image_search(query: str) -> list[dict]:
    """
    Searches the web for pictures and send to user as markdown.
    """
    print("Gemini is searching Images:", query)
    try:
        return DDGS().images(query, max_results=15)
    except Exception as e:
        print(f"Text search failed: {e}")
        return []

def clean_session():
    try:
        sessions = Path("./flask_session/")
        for item in sessions.iterdir():
            if item.is_dir():
                shutil.rmtree(item)  # Removes subdirectories and their contents
                print("Session Cleaned")
            else:
                item.unlink()        # Removes individual files
    except:
        print("No jobs, already cleaned")