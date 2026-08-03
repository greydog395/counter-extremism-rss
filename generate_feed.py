import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime
from email.utils import format_datetime

BASE = "https://www.counterextremism.com"
URL = "https://www.counterextremism.com/news-and-media/eye-on-extremism"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

fg = FeedGenerator()
fg.title("Counter Extremism Project - Eye on Extremism")
fg.link(href=URL)
fg.description("Daily Eye on Extremism updates")
fg.language("en")

seen = set()

# Find all links to Eye on Extremism articles
for link in soup.find_all("a", href=True):

    href = link["href"]

    if "/roundup/eye-extremism-" not in href:
        continue

    article_url = urljoin(BASE, href)

    if article_url in seen:
        continue

    seen.add(article_url)

    title = link.get_text(" ", strip=True)

    if not title:
        title = href.split("/")[-1].replace("-", " ").title()

    # Download article page
    article = requests.get(article_url, headers=headers, timeout=30)
    article.raise_for_status()

    article_soup = BeautifulSoup(article.text, "html.parser")

    # --------------------------
    # Find publication date
    # --------------------------

    pub_date = None

    # Try schema.org metadata
    meta = article_soup.find("meta", attrs={"property": "article:published_time"})
    if meta:
        pub_date = meta.get("content")

    if not pub_date:
        meta = article_soup.find("meta", attrs={"name": "publish-date"})
        if meta:
            pub_date = meta.get("content")

    if not pub_date:
        time_tag = article_soup.find("time")
        if time_tag:
            pub_date = time_tag.get("datetime") or time_tag.get_text(strip=True)

    # Convert date
    if pub_date:

        try:

            if "T" in pub_date:
                dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(pub_date, "%B %d, %Y")

            rss_date = format_datetime(dt)

        except Exception:
            rss_date = format_datetime(datetime.utcnow())

    else:
        rss_date = format_datetime(datetime.utcnow())

    # --------------------------
    # Summary
    # --------------------------

    summary = ""

    desc = article_soup.find("meta", attrs={"name": "description"})
    if desc:
        summary = desc.get("content", "")

    entry = fg.add_entry()

    entry.title(title)
    entry.link(href=article_url)
    entry.guid(article_url, permalink=True)
    entry.description(summary)
    entry.pubDate(rss_date)

print(f"FOUND ARTICLES: {len(seen)}")

fg.rss_file("feed.xml")
