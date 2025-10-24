# meshbot wiki module

from modules.log import *
#import wikipedia # pip install wikipedia
import requests
import bs4 as bs
from urllib.parse import quote

def tag_visible(element):
    """Filter visible text from HTML elements for Kiwix"""
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, bs.element.Comment):
        return False
    return True

def text_from_html(body):
    """Extract visible text from HTML content"""
    soup = bs.BeautifulSoup(body, 'html.parser')
    texts = soup.find_all(string=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts if t.strip())

def get_kiwix_summary(search_term):
    """Query local Kiwix server for Wikipedia article"""
    if search_term is None or search_term.strip() == "":
        return ERROR_FETCHING_DATA
    try:
        search_encoded = quote(search_term)
        # Try direct article access first
        wiki_article = search_encoded.capitalize().replace("%20", "_")
        exact_url = f"{kiwix_url}/raw/{kiwix_library_name}/content/A/{wiki_article}"
        
        response = requests.get(exact_url, timeout=urlTimeoutSeconds)
        if response.status_code == 200:
            # Extract and clean text
            text = text_from_html(response.text)
            # Remove common Wikipedia metadata prefixes
            text = text.split("Jump to navigation", 1)[-1]
            text = text.split("Jump to search", 1)[-1]
            # Truncate to reasonable length (first few sentences)
            sentences = text.split('. ')
            summary = '. '.join(sentences[:wiki_return_limit])
            if summary and not summary.endswith('.'):
                summary += '.'
            return summary.strip()[:500]  # Hard limit at 500 chars

        # If direct access fails, try search
        logger.debug(f"System: Kiwix direct article not found for:{search_term} Status Code:{response.status_code}")
        search_url = f"{kiwix_url}/search?content={kiwix_library_name}&pattern={search_encoded}"
        response = requests.get(search_url, timeout=urlTimeoutSeconds)
        
        if response.status_code == 200 and "No results were found" not in response.text:
            soup = bs.BeautifulSoup(response.text, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True) if "start=" not in a['href']]
            
            for link in links[:3]:  # Check first 3 results
                article_name = link.split("/")[-1]
                if not article_name or article_name[0].islower():
                    continue
                    
                article_url = f"{kiwix_url}{link}"
                article_response = requests.get(article_url, timeout=urlTimeoutSeconds)
                if article_response.status_code == 200:
                    text = text_from_html(article_response.text)
                    text = text.split("Jump to navigation", 1)[-1]
                    text = text.split("Jump to search", 1)[-1]
                    sentences = text.split('. ')
                    summary = '. '.join(sentences[:wiki_return_limit])
                    if summary and not summary.endswith('.'):
                        summary += '.'
                    return summary.strip()[:500]
        
        logger.warning(f"System: No Kiwix Results for:{search_term}")
        # try to fall back to online Wikipedia if available
        return get_wikipedia_summary(search_term, force=True)

        
    except requests.RequestException as e:
        logger.warning(f"System: Kiwix connection error: {e}")
        return "Unable to connect to local wiki server"
        # Fallback to online Wikipedia
        return get_wikipedia_summary(search_term, force=True)
    except Exception as e:
        logger.warning(f"System: Error with Kiwix for:{search_term} {e}")
        return ERROR_FETCHING_DATA

def get_wikipedia_summary(search_term, location=None, force=False):
    if use_kiwix_server and not force:
        return get_kiwix_summary(search_term)

    if not search_term or not search_term.strip():
        return ERROR_FETCHING_DATA

    api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(search_term)}"
    headers = {
        "User-Agent": "MeshBot/1.0 (https://github.com/kkeeton/meshing-around; contact: youremail@example.com)"
    }
    try:
        response = requests.get(api_url, timeout=5, headers=headers)
        if response.status_code == 404:
            logger.warning(f"System: No Wikipedia Results for:{search_term}")
            return ERROR_FETCHING_DATA
        response.raise_for_status()
        data = response.json()
        # Check for error response from Wikipedia API
        if "extract" not in data or not data.get("extract"):
            logger.warning(f"System: Wikipedia API returned no extract for:{search_term} (data: {data})")
            return ERROR_FETCHING_DATA
        summary = data.get("extract")
        if not summary or not isinstance(summary, str) or not summary.strip():
            logger.warning(f"System: No summary found for:{search_term}")
            return ERROR_FETCHING_DATA
        sentences = [s for s in summary.split('. ') if s.strip()]
        if not sentences:
            logger.warning(f"System: Wikipedia summary split produced no sentences for:{search_term}")
            return ERROR_FETCHING_DATA
        summary = '. '.join(sentences[:wiki_return_limit])
        if summary and not summary.endswith('.'):
            summary += '.'
        return summary.strip()[:500]
    except Exception as e:
        logger.warning(f"System: Wikipedia API error for:{search_term} {e}")
        return ERROR_FETCHING_DATA

# def get_wikipedia_summary(search_term, location=None, force=False):
#     lat, lon = location if location else (None, None)
#     # Use Kiwix if configured
#     if use_kiwix_server and not force:
#         return get_kiwix_summary(search_term)
    
#     try:
#         # Otherwise use online Wikipedia
#         wikipedia_search = wikipedia.search(search_term, results=3)
#         wikipedia_suggest = wikipedia.suggest(search_term)
#         #wikipedia_aroundme = wikipedia.geosearch(lat,lon, results=3)
#         #logger.debug(f"System: Wikipedia Nearby:{wikipedia_aroundme}")
#     except Exception as e:
#         logger.debug(f"System: Wikipedia search error for:{search_term} {e}")
#         return ERROR_FETCHING_DATA
    
#     if len(wikipedia_search) == 0:
#         logger.warning(f"System: No Wikipedia Results for:{search_term}")
#         return ERROR_FETCHING_DATA
    
#     try:
#         logger.debug(f"System: Searching Wikipedia for:{search_term}, First Result:{wikipedia_search[0]}, Suggest Word:{wikipedia_suggest}")
#         summary = wikipedia.summary(search_term, sentences=wiki_return_limit, auto_suggest=False, redirect=True)
#     except wikipedia.DisambiguationError as e:
#         logger.warning(f"System: Disambiguation Error for:{search_term} trying {wikipedia_search[0]}")
#         summary = wikipedia.summary(wikipedia_search[0], sentences=wiki_return_limit, auto_suggest=True, redirect=True)
#     except wikipedia.PageError as e:
#         logger.warning(f"System: Wikipedia Page Error for:{search_term} {e} trying {wikipedia_search[0]}")
#         summary = wikipedia.summary(wikipedia_search[0], sentences=wiki_return_limit, auto_suggest=True, redirect=True)
#     except Exception as e:
#         logger.warning(f"System: Error with Wikipedia for:{search_term} {e}")
#         return ERROR_FETCHING_DATA
    
#     return summary