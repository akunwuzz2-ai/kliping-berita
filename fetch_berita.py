import os
import re
import json
import time
import requests

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.atrbpn.go.id"

OUTPUT_DIR = "docs/posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


print("Menjalankan browser...")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("Buka homepage...")
    page.goto(BASE_URL, wait_until="domcontentloaded")

    time.sleep(5)

    print("Buka halaman berita...")
    page.goto(
        "https://www.atrbpn.go.id/berita",
        wait_until="domcontentloaded"
    )

    time.sleep(8)

    html = page.content()

    browser.close()

print("Parsing halaman berita...")

soup = BeautifulSoup(html, "html.parser")

links = soup.find_all("a", href=True)

berita_list = []

for a in links:

    href = a["href"]

    if "/berita/" in href:

        title = a.get_text(strip=True)

        if len(title) < 10:
            continue

        url = href

        if not url.startswith("http"):
            url = BASE_URL + href

        berita_list.append({
            "title": title,
            "url": url
        })

# hapus duplikat
unique = []

used = set()

for item in berita_list:

    if item["url"] not in used:

        used.add(item["url"])
        unique.append(item)

berita_list = unique[:12]

print("TOTAL:", len(berita_list))

for berita in berita_list:

    try:

        print("=" * 60)
        print("SCRAPE:", berita["title"])

        url = berita["url"]

        res = requests.get(url, headers=HEADERS, timeout=30)

        soup = BeautifulSoup(res.text, "html.parser")

        # ambil semua paragraf
        paragraphs = soup.find_all("p")

        isi_list = []

        for p in paragraphs:

            txt = p.get_text(" ", strip=True)

            if len(txt) > 40:
                isi_list.append(txt)

        isi = "\n\n".join(isi_list)

        if not isi:
            isi = "Isi artikel gagal diambil."

        slug = slugify(berita["title"])

        markdown = f"""---
title: "{berita['title']}"
date: "{time.strftime('%Y-%m-%d')}"
---

# {berita['title']}

{isi}

Sumber resmi:

{url}
"""

        filepath = f"{OUTPUT_DIR}/{slug}.md"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)

        print("SAVE:", slug)

        time.sleep(2)

    except Exception as e:

        print("ERROR:", str(e))

print("SELESAI")
