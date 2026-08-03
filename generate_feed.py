import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone

SOURCE = "https://www.counterextremism.com/news-and-media"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(
    SOURCE,
    headers=headers,
    timeout=30
).text

soup = BeautifulSoup(html, "html.parser")

feed = FeedGenerator()

feed.title("Counter Extremism Project News")
feed.link(href=SOURCE)
feed.description(
    "Latest news from the Counter Extremism Project"
)
feed.language("en")

count = 0

for a in soup.find_all("a", href=True):

    title = a.get_text(" ", strip=True)
    link = urljoin(SOURCE, a["href"])

    if not title:
        continue

    if "/news/" not in link:
        continue

    item = feed.add_entry()
    item.title(title)
    item.link(href=link)
    item.guid(link)
    item.description(
        "Counter Extremism Project news article"
    )

    count += 1

feed.lastBuildDate(
    datetime.now(timezone.utc)
)

feed.rss_file("feed.xml")

print("Created feed with", count, "items")
