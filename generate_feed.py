import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone

BASE = "https://www.counterextremism.com"
URL = "https://www.counterextremism.com/news-and-media"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

feed = FeedGenerator()

feed.title("Counter Extremism Project News")
feed.link(href=URL)
feed.description("Latest news from the Counter Extremism Project")
feed.language("en")

found = set()
count = 0

# Find headings and nearby article links
for tag in soup.find_all(["h1", "h2", "h3", "h4"]):

    link = tag.find("a", href=True)

    if not link:
        continue

    title = link.get_text(" ", strip=True)
    href = link["href"]

    if len(title) < 5:
        continue

    url = urljoin(BASE, href)

    if url in found:
        continue

    found.add(url)

    item = feed.add_entry()
    item.title(title)
    item.link(href=url)
    item.guid(url)
    item.description(
        "Counter Extremism Project article"
    )

    count += 1

print("FOUND ARTICLES:", count)

feed.lastBuildDate(datetime.now(timezone.utc))
feed.rss_file("feed.xml")
