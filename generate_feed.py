import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone

SOURCE = "https://www.counterextremism.com/news-and-media"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    SOURCE,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

feed = FeedGenerator()

feed.title("Counter Extremism Project News")
feed.link(href=SOURCE)
feed.description(
    "Latest news from the Counter Extremism Project"
)
feed.language("en")

count = 0
seen = set()

# Look for all links on the page
for a in soup.find_all("a", href=True):

    title = a.get_text(" ", strip=True)
    url = urljoin(SOURCE, a["href"])

    # Keep article pages only
    if "/news/" not in url:
        continue

    if url in seen:
        continue

    if len(title) < 10:
        continue

    seen.add(url)

    item = feed.add_entry()
    item.title(title)
    item.link(href=url)
    item.guid(url)
    item.description(
        "Counter Extremism Project article"
    )

    count += 1


feed.lastBuildDate(
    datetime.now(timezone.utc)
)

feed.rss_file("feed.xml")

print("Articles found:", count)
