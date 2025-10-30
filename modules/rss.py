# rss feed module for meshing-around 2025
from modules.log import logger
from modules.settings import rssFeedURL, rssFeedNames, rssMaxItems, rssTruncate, urlTimeoutSeconds, ERROR_FETCHING_DATA, newsAPI_KEY
import urllib.request
import xml.etree.ElementTree as ET
import html
from html.parser import HTMLParser
import bs4 as bs
import requests
import datetime

# Common User-Agent for all RSS requests
COMMON_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html_text):
    # use BeautifulSoup to strip HTML tags
    if not html_text:
        return ""
    soup = bs.BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return ' '.join(text.split())

RSS_FEED_URLS = rssFeedURL
RSS_FEED_NAMES = rssFeedNames
RSS_RETURN_COUNT = rssMaxItems
RSS_TRIM_LENGTH = rssTruncate

def get_rss_feed(msg):
    # Determine which feed to use
    feed_name = ""
    msg_lower = msg.lower() if msg else ""
    if msg_lower and any(name.lower() in msg_lower for name in RSS_FEED_NAMES):
        for name in RSS_FEED_NAMES:
            if name.lower() in msg_lower:
                feed_name = name
                break
    else:
        logger.debug(f"RSS: No feed name found in message '{msg}'. Using default feed.")
        feed_name = RSS_FEED_NAMES[0] if RSS_FEED_NAMES else "default"

    try:
        idx = RSS_FEED_NAMES.index(feed_name)
        feed_url = RSS_FEED_URLS[idx]
    except (ValueError, IndexError):
        logger.warning(f"RSS: Feed '{feed_name}' not found in RSS_FEED_URLS ({RSS_FEED_URLS}).")
        return f"Feed '{feed_name}' not found."

    if "?" in msg_lower:
        return f"Fetches the latest {RSS_RETURN_COUNT} entries RSS feeds. Available feeds are: {', '.join(RSS_FEED_NAMES)}. To fetch a specific feed, include its name in your request."

    # Fetch and parse the RSS feed
    try:
        logger.debug(f"Fetching RSS feed from {feed_url} from message '{msg}'")
        agent = {'User-Agent': COMMON_USER_AGENT}
        request = urllib.request.Request(feed_url, headers=agent)
        with urllib.request.urlopen(request, timeout=urlTimeoutSeconds) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)

        # Find all <item> (RSS) and <entry> (Atom) elements, regardless of namespace
        items = []
        for elem in root.iter():
            if elem.tag.endswith('item') or elem.tag.endswith('entry'):
                items.append(elem)
        items = items[:RSS_RETURN_COUNT]

        if not items:
            logger.debug(f"No RSS or Atom feed entries found in feed xml_data: {xml_data[:500]}...")
            return "No RSS or Atom feed entries found."

        formatted_entries = []
        seen_first3 = set()  # Track first 3 words (lowercased) to avoid duplicates
        for item in items:
            # Helper to try multiple tag names
            def find_any(item, tags):
                for tag in tags:
                    val = item.findtext(tag)
                    if val:
                        return val
                return None

            title = find_any(item, [
                'title',
                '{http://purl.org/rss/1.0/}title',
                '{http://www.w3.org/2005/Atom}title'
            ])

            # Atom links are often attributes, not text
            link = find_any(item, [
                'link',
                '{http://purl.org/rss/1.0/}link',
                '{http://www.w3.org/2005/Atom}link'
            ])
            if not link:
                link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                if link_elem is not None and 'href' in link_elem.attrib:
                    link = link_elem.attrib['href']

            description = find_any(item, [
                'description',
                '{http://purl.org/rss/1.0/}description',
                '{http://purl.org/rss/1.0/modules/content/}encoded',
                '{http://www.w3.org/2005/Atom}summary',
                '{http://www.w3.org/2005/Atom}content'
            ])
            pub_date = find_any(item, [
                'pubDate',
                '{http://purl.org/dc/elements/1.1/}date',
                '{http://www.w3.org/2005/Atom}updated'
            ])

            # Unescape HTML entities and strip tags
            description = html.unescape(description) if description else ""
            description = strip_tags(description)
            if len(description) > RSS_TRIM_LENGTH:
                description = description[:RSS_TRIM_LENGTH - 3] + "..."

            # Duplicate check: use first 3 words of description (or title if description is empty)
            text_for_dupe = description if description else (title or "")
            first3 = " ".join(text_for_dupe.lower().split()[:3])
            if first3 in seen_first3:
                continue
            seen_first3.add(first3)

            formatted_entries.append(f"{title}\n{description}\n")
        return "\n".join(formatted_entries)
    except Exception as e:
        logger.error(f"Error fetching RSS feed from {feed_url}: {e}")
        return ERROR_FETCHING_DATA

def get_newsAPI(user_search="meshtastic"):
    # Fetch news from NewsAPI.org
    user_search = user_search.lower().replace("latest ", "", 1).strip()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'}
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)
        newsAPIurl = (
            f"https://newsapi.org/v2/everything?"
            f"q={user_search}&language=en&from={last_week.strftime('%Y-%m-%d')}&sortBy=popularity&pageSize=7&apiKey={newsAPI_KEY}"
        )

        response = requests.get(newsAPIurl, headers=headers, timeout=10)
        news_data = response.json()

        if news_data.get("status") != "ok":
            error_message = news_data.get("message", "Unknown error")
            logger.error(f"NewsAPI error: {error_message}")
            return [f"NewsAPI error: {error_message}"]
        logger.debug(f"System: NewsAPI Searching for '{user_search}' got {news_data.get('totalResults', 0)} results")
        articles = news_data.get("articles", [])[:3]
        news_list = []
        for article in articles:
            title = article.get("title", "No Title")
            url = article.get("url", "")
            description = article.get("description", '')
            news_list.append(f"📰{title}\n{description}")
        

        # Make a nice newspaper style output
        msg = f"🗞️:"
        for item in news_list:
            msg += item + "\n\n"
        return msg.strip()
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return [f"Exception: {e}"]