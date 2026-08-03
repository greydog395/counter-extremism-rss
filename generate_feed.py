import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone
from email.utils import format_datetime
import re

BASE = "https://www.counterextremism.com"
SOURCE = "https://www.counterextremism.com/news-and-media/eye-on-extremism"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Get archive page
response = requests.get(
    SOURCE,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Create RSS
feed = FeedGenerator()

feed.title("Counter Extremism Project - Eye on Extremism")
feed.link(href=SOURCE)
feed.description("Daily Eye on Extremism updates")
feed.language("en")

seen = set()
count = 0

# Find roundup links
for a in soup.find_all("a", href=True):

    href = a["href"]

    if "/roundup/eye-extremism-" not in href:
        continue

    url = urljoin(BASE, href)

    if url in seen:
        continue

    seen.add(url)

    # Extract title
    title = a.get_text(" ", strip=True)

    if not title:
        title = url.split("/")[-1].replace("-", " ").title()

    # Extract date from URL
    match = re.search(
        r"eye-extremism-([a-z]+)-(\d+)-(\d{4})",
        url
    )

    if match:

        month, day, year = match.groups()

        try:
            pub_date = datetime.strptime(
                f"{month} {day} {year}",
                "%B %d %Y"
            )

        except ValueError:
            pub_date = datetime.now(timezone.utc)

    else:
        pub_date = datetime.now(timezone.utc)


    # Create RSS item
    item = feed.add_entry()

    item.title(title)
    item.link(href=url)
    item.guid(url, permalink=True)
    item.description(
        "Counter Extremism Project Eye on Extremism roundup"
    )
    item.pubDate(
        format_datetime(pub_date)
    )

    count += 1


print("FOUND ARTICLES:", count)

feed.lastBuildDate(
    format_datetime(datetime.now(timezone.utc))
)

feed.rss_file("feed.xml")
