import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone

BASE = "https://www.counterextremism.com"
URL = "https://www.counterextremism.com/news-and-media/eye-on-extremism"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

fg = FeedGenerator()
fg.title("Counter Extremism Project - Eye on Extremism")
fg.link(href=URL)
fg.description("Daily Eye on Extremism updates")
fg.language("en")

seen = set()
count = 0

for a in soup.find_all("a", href=True):

    href = a["href"]

    if "/eye-extremism-" not in href:
        continue

    link = urljoin(BASE, href)

    if link in seen:
        continue

    seen.add(link)

    title = a.get_text(" ", strip=True)

    if not title:
        title = href.split("/")[-1].replace("-", " ").title()

    # Fetch the individual article
    try:
        article = requests.get(link, headers=headers, timeout=30)
        article.raise_for_status()
        article_soup = BeautifulSoup(article.text, "html.parser")

        # Look for a <time> tag
        time_tag = article_soup.find("time")

        if time_tag and time_tag.has_attr("datetime"):
            pub_date = datetime.fromisoformat(
                time_tag["datetime"].replace("Z", "+00:00")
            )
        else:
            pub_date = datetime.now(timezone.utc)

    except Exception:
        pub_date = datetime.now(timezone.utc)

    entry = fg.add_entry()
    entry.title(title)
    entry.link(href=link)
    entry.guid(link, permalink=True)
    entry.description(title)
    entry.pubDate(pub_date)

print(f"FOUND ARTICLES: {count}")

fg.lastBuildDate(datetime.now(timezone.utc))
fg.rss_file("feed.xml")
