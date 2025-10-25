# rss feed module for meshing-around 2025
from modules.log import logger
from modules.settings import rssFeedURL, rssFeedNames, rssMaxItems, rssTruncate, urlTimeoutSeconds, ERROR_FETCHING_DATA
import urllib.request
import xml.etree.ElementTree as ET
import html
from html.parser import HTMLParser
import bs4 as bs

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

    try:
        logger.debug(f"Fetching RSS feed from {feed_url} from message '{msg}'")
        agent = {'User-Agent': COMMON_USER_AGENT}
        request = urllib.request.Request(feed_url, headers=agent)
        with urllib.request.urlopen(request, timeout=urlTimeoutSeconds) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        # Try both namespaced and non-namespaced item tags
        items = root.findall('.//item')
        ns = None
        if not items:
            # Try Atom <entry> elements (Reddit, etc.)
            items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            ns = 'http://www.w3.org/2005/Atom'
        if not items:
            # Try to find the namespace dynamically for RSS
            for elem in root.iter():
                if elem.tag.endswith('item'):
                    ns_uri = elem.tag.split('}')[0].strip('{')
                    items = root.findall(f'.//{{{ns_uri}}}item')
                    ns = ns_uri
                    break
        items = items[:RSS_RETURN_COUNT]
        if not items:
            logger.debug(f"No RSS or Atom feed entries found in feed xml_data: {xml_data[:500]}...")
            return "No RSS or Atom feed entries found."
        formatted_entries = []
        for item in items:
            if ns == 'http://www.w3.org/2005/Atom':
                # Atom feed
                title = item.findtext('{http://www.w3.org/2005/Atom}title', default='No title')
                # Atom links are in <link href="..."/>
                link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                link = link_elem.attrib.get('href') if link_elem is not None else None
                # Atom content or summary
                description = item.findtext('{http://www.w3.org/2005/Atom}content')
                if not description:
                    description = item.findtext('{http://www.w3.org/2005/Atom}summary', default='No description')
                pub_date = item.findtext('{http://www.w3.org/2005/Atom}updated', default='No date')
            else:
                # RSS feed
                title = item.findtext('title', default='No title')
                link = item.findtext('link', default=None)
                description = item.findtext('description', default='No description')
                pub_date = item.findtext('pubDate', default='No date')

            # Unescape HTML entities and strip tags
            description = html.unescape(description) if description else ""
            description = strip_tags(description)
            if len(description) > RSS_TRIM_LENGTH:
                description = description[:RSS_TRIM_LENGTH - 3] + "..."

            formatted_entries.append(f"{title}\n{description}\n")
        return "\n".join(formatted_entries)
    except Exception as e:
        logger.error(f"Error fetching RSS feed from {feed_url}: {e}")
        return ERROR_FETCHING_DATA
