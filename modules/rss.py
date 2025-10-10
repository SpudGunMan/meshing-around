# rss feed module for meshing-around 2025
from modules.log import *
import urllib.request
import xml.etree.ElementTree as ET

RSS_FEED_URLS = rssFeedURL
RSS_FEED_NAMES = rssFeedNames
RSS_RETURN_COUNT = rssMaxItems
RSS_TRIM_LENGTH = rssTruncate

def get_rss_feed(msg):
    # Determine which feed to use
    feed_name = "default"
    if msg and any(name in msg for name in RSS_FEED_NAMES):
        for name in RSS_FEED_NAMES:
            if name in msg:
                feed_name = name
                break

    try:
        idx = RSS_FEED_NAMES.index(feed_name)
        feed_url = RSS_FEED_URLS[idx]
    except (ValueError, IndexError):
        return f"Feed '{feed_name}' not found."

    if "?" in msg:
        return f"Fetches the latest {RSS_RETURN_COUNT} entries from the {feed_name} RSS feed."

    try:
        with urllib.request.urlopen(feed_url) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')[:RSS_RETURN_COUNT]
        if not items:
            return "No RSS feed entries found."
        formatted_entries = []
        for item in items:
            title = item.findtext('title', default='No title')
            link = item.findtext('link', default='No link')
            description = item.findtext('description', default='No description')
            pub_date = item.findtext('pubDate', default='No date')

            # strip all HTML tags and markup
            description = ''.join(ET.fromstring(f"<div>{description}</div>").itertext())
            if len(description) > RSS_TRIM_LENGTH:
                description = description[:97] + "..."

            formatted_entries.append(f"{title}\n{description}\n")
        return "\n".join(formatted_entries)
    except Exception as e:
        return ERROR_FETCHING_DATA
