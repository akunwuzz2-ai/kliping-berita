import requests
import os
import time
import re
from bs4 import BeautifulSoup

BASE = "https://www.atrbpn.go.id"

API = f"{BASE}/items/page_menu_components"

OUTPUT_DIR = "docs/posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": BASE
}

session = requests.Session()


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def extract_text(html):
    return BeautifulSoup(html, "html.parser").get_text("\n", strip=True)


def get_page(page=1):
    url = f"{API}?page={page}&limit=10&fields=components.id,components.code,content,setting,order"
    r = session.get(url, headers=HEADERS, timeout=30)

    print("PAGE", page, "STATUS:", r.status_code)

    r.raise_for_status()
    return r.json()


page = 1
total_saved = 0

while True:

    data = get_page(page)

    items = data.get("data", [])

    if not items:
        break

    for item in items:

        try:
            content = item.get("content", "")

            if not content:
                continue

            text = extract_text(content)

            # ambil judul dari paragraf pertama
            soup = BeautifulSoup(content, "html.parser")
            title = soup.get_text(" ", strip=True)[:120]

            slug = slugify(title)

            md = f"""---
title: "{title}"
date: "2026-05-15"
---

# {title}

{text}
"""

            path = f"{OUTPUT_DIR}/{slug}.md"

            with open(path, "w", encoding="utf-8") as f:
                f.write(md)

            print("SAVE:", slug)
            total_saved += 1

        except Exception as e:
            print("ERROR:", repr(e))

    page += 1
    time.sleep(1)

    if page > 20:  # safety limit GitHub Actions
        break

print("TOTAL SAVED:", total_saved)
print("SELESAI")
