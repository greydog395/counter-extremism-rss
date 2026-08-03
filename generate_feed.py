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

html = requests.get(URL, headers=headers, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

fg = FeedGenerator()

fg.title("Counter Extremism Project - Eye on Extremism")
fg.link(href=URL)
fg.description("Daily Eye on Extremism updates")
fg.language("en")

seen = set()
count = 0

for a in soup.find_all("a", href=True):

    href = a["href"]

    if "/roundup/eye-extremism-" not in href:
        continue

    link = urljoin(BASE, href)

    if link in seen:
        continue

    seen.add(link)

    title = a.get_text(" ", strip=True)
if not title:
    continue
    if not title:
        title = link.split("/")[-1].replace("-", " ").title()

    # Extract date from URL
    match = re.search(
        r"eye-extremism-([a-z]+)-(\d+)-(\d{4})",
        link
    )

    if match:
        month, day, year = match.groups()

        pub_date = datetime.strptime(
            f"{month} {day} {year}",
            "%B %d %Y"
        )

    else:
        pub_date = datetime.utcnow()

    entry = fg.add_entry()

    entry.title(title)
    entry.link(href=link)
    entry.guid(link, permalink=True)
    entry.description(
        "Counter Extremism Project Eye on Extremism roundup"
    )
    entry.pubDate(
        format_datetime(pub_date)
    )

    count += 1


print("FOUND ARTICLES:", count)

fg.rss_file("feed.xml")
