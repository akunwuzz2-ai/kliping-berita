import requests
from bs4 import BeautifulSoup
import os
import re
import time

BASE = "https://www.atrbpn.go.id"
URL = BASE + "/berita"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_DIR = "docs/posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def get_list():
    r = requests.get(URL, headers=HEADERS, timeout=30)

    print("STATUS:", r.status_code)

    soup = BeautifulSoup(r.text, "html.parser")

    links = []

    # 🔥 FIX: ambil semua a tag tanpa class filter
    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "/berita/" not in href:
            continue

        title = a.get_text(" ", strip=True)

        # filter noise
        if len(title) < 10:
            continue

        full_url = BASE + href if href.startswith("/") else href

        links.append({
            "title": title,
            "url": full_url
        })

    # deduplicate
    seen = set()
    result = []

    for x in links:
        if x["url"] not in seen:
            seen.add(x["url"])
            result.append(x)

    return result


def scrape_detail(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else "no-title"

    paragraphs = soup.find_all("p")

    content = "\n\n".join(
        p.get_text(" ", strip=True)
        for p in paragraphs
        if len(p.get_text(strip=True)) > 40
    )

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
