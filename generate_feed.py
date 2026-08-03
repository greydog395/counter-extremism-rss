import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime
from email.utils import format_datetime
import re

BASE = "https://www.counterextremism.com"
URL = "https://www.counterextremism.com/news-and-media/eye-on-extremism"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

feed = FeedGenerator()

feed.title("Counter Extremism Project - Eye on Extremism")
feed.link(href=URL)
feed.description("Daily Eye on Extremism updates")
feed.language("en")

seen = set()
count = 0

# Find roundup headings
for heading in soup.find_all(["h2", "h3"]):

    title = heading.get_text(" ", strip=True)

    if "Eye on Extremism:" not in title:
        continue

    # Extract date from title
    match = re.search(
        r"Eye on Extremism:\s*(.*)",
        title
    )

    if not match:
        continue

    date_text = match.group(1)

    try:
        pub_date = datetime.strptime(
            date_text,
            "%B %d, %Y"
        )

    except:
        continue

    # Find the nearest link
    link = heading.find("a", href=True)

    if not link:
        continue

    url = urljoin(BASE, link["href"])

    if url in seen:
        continue

    seen.add(url)

    entry = feed.add_entry()

    entry.title(title)
    entry.link(href=url)
    entry.guid(url, permalink=True)
    entry.description(
        "Counter Extremism Project Eye on Extremism roundup"
    )
    entry.pubDate(
        format_datetime(pub_date)
    )

    count += 1

print("FOUND ARTICLES:", count)

feed.lastBuildDate(
    format_datetime(datetime.utcnow())
)

feed.rss_file("feed.xml")
