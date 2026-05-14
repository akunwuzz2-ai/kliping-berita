import requests
from bs4 import BeautifulSoup
import os
import re
import time

BASE = "https://www.atrbpn.go.id"
URL = "https://www.atrbpn.go.id/berita"

OUTPUT_DIR = "docs/posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def get_list():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    links = []

    for a in soup.select("a.body-link[href^='/berita/']"):
        href = a.get("href")
        title = a.get_text(strip=True)

        if not href or not title:
            continue

        full_url = BASE + href

        links.append({
            "title": title,
            "url": full_url
        })

    return links


def scrape_detail(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else "no-title"

    paragraphs = soup.find_all("p")
    content = "\n\n".join(p.get_text(" ", strip=True) for p in paragraphs if len(p.get_text()) > 40)

    return title, content


print("Ambil list berita...")

items = get_list()

print("TOTAL:", len(items))

for item in items[:12]:

    try:
        print("SCRAPE:", item["title"])

        title, content = scrape_detail(item["url"])

        slug = slugify(title)

        md = f"""---
title: "{item['title']}"
date: "2026-05-15"
---

# {item['title']}

{content}

Source:
{item['url']}
"""

        with open(f"{OUTPUT_DIR}/{slug}.md", "w", encoding="utf-8") as f:
            f.write(md)

        time.sleep(1)

    except Exception as e:
        print("ERROR:", repr(e))

print("SELESAI")
