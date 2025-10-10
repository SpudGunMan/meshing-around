# rss feed module for meshing-around 2025
from modules.log import *
import urllib.request
import xml.etree.ElementTree as ET

RSS_FEED_URL = rssFeedURL
RSS_RETURN_COUNT = rssMaxItems
RSS_TRIM_LENGTH = rssTruncate

def get_rss_feed():
    try:
        with urllib.request.urlopen(RSS_FEED_URL) as response:
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
        return f"Error fetching RSS feed: {e}"
