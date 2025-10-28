# meshbot wiki module

from modules.log import logger
from modules.settings import (use_kiwix_server, kiwix_url, kiwix_library_name,
                              urlTimeoutSeconds, wiki_return_limit, ERROR_FETCHING_DATA, wikipedia_enabled)
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
    """Extract main article text from HTML content"""
    soup = bs.BeautifulSoup(body, 'html.parser')
    # Try to find the main content div (works for both Kiwix and Wikipedia HTML)
    main = soup.find('div', class_='mw-parser-output')
    if not main:
        # Fallback: just use the body if main content div not found
        main = soup.body
    if not main:
        return ""
    texts = main.find_all(string=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts if t.strip())

def get_kiwix_summary(search_term, truncate=True):
    """Query local Kiwix server for Wikipedia article using only search results."""
    if search_term is None or search_term.strip() == "":
        return ERROR_FETCHING_DATA
    try:
        search_encoded = quote(search_term)
        search_url = f"{kiwix_url}/search?content={kiwix_library_name}&pattern={search_encoded}"
        response = requests.get(search_url, timeout=urlTimeoutSeconds)

        if response.status_code == 200 and "No results were found" not in response.text:
            soup = bs.BeautifulSoup(response.text, 'html.parser')
            results = soup.select('div.results ul li')
            logger.debug(f"Kiwix: Found {len(results)} results in search results for:{search_term}")
            for li in results[:3]:
                a = li.find('a', href=True)
                if not a:
                    continue
                article_url = f"{kiwix_url}{a['href']}"
                article_response = requests.get(article_url, timeout=urlTimeoutSeconds)
                if article_response.status_code == 200:
                    text = text_from_html(article_response.text)
                    # Remove navigation and search jump text
                    # text = text.split("Jump to navigation", 1)[-1]
                    # text = text.split("Jump to search", 1)[-1]
                    sentences = text.split('. ')
                    summary = '. '.join(sentences[:wiki_return_limit])
                    if summary and not summary.endswith('.'):
                        summary += '.'
                    if truncate:
                        return summary.strip()[:500]
                    else:
                        return summary.strip()

        logger.debug(f"System: No Kiwix Results for:{search_term}")
        if wikipedia_enabled:
            logger.debug("Kiwix: Falling back to Wikipedia API.")
            return get_wikipedia_summary(search_term, force=True)
        return ERROR_FETCHING_DATA

    except Exception as e:
        logger.warning(f"System: Error with Kiwix for:{search_term} URL:{search_url} {e}")
        return ERROR_FETCHING_DATA

def get_wikipedia_summary(search_term, location=None, force=False, truncate=True):
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
        logger.debug(f"Wikipedia API response for '{search_term}': {len(data)} keys")
        if "extract" not in data or not data.get("extract"):
            #logger.debug(f"System: Wikipedia API returned no extract for:{search_term} (data: {data})")
            return ERROR_FETCHING_DATA
        if data.get("type") == "disambiguation" or "may refer to:" in data.get("extract", ""):
            #logger.warning(f"System: Disambiguation page for:{search_term} (data: {data})")
            # Fetch and parse the HTML disambiguation page
            html_url = f"https://en.wikipedia.org/wiki/{requests.utils.quote(search_term)}"
            html_resp = requests.get(html_url, timeout=5, headers=headers)
            if html_resp.status_code == 200:
                soup = bs.BeautifulSoup(html_resp.text, 'html.parser')
                items = soup.select('div.mw-parser-output ul li a[href^="/wiki/"]')
                choices = []
                for a in items:
                    title = a.get('title')
                    href = a.get('href')
                    # Filter out non-article links
                    if title and href and ':' not in href:
                        choices.append(f"{title} (https://en.wikipedia.org{href})")
                    if len(choices) >= 5:
                        break
                if choices:
                    return f"'{search_term}' is ambiguous. Did you mean:\n- " + "\n- ".join(choices)
            return f"'{search_term}' is ambiguous. Please be more specific. See: {html_url}"
        summary = data.get("extract")
        if not summary or not isinstance(summary, str) or not summary.strip():
            #logger.debug(f"System: No summary found for:{search_term} (data: {data})")
            return ERROR_FETCHING_DATA
        sentences = [s for s in summary.split('. ') if s.strip()]
        if not sentences:
            return ERROR_FETCHING_DATA
        summary = '. '.join(sentences[:wiki_return_limit])
        if summary and not summary.endswith('.'):
            summary += '.'
        if truncate:
            # Truncate to 500 characters
            return summary.strip()[:500]
        else:
            return summary.strip()
    except Exception as e:
        logger.warning(f"System: Wikipedia API error for:{search_term} {e}")
        return ERROR_FETCHING_DATA
