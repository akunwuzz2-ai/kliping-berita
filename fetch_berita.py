import requests
import os
import time
import re
from bs4 import BeautifulSoup

BASE = "https://www.atrbpn.go.id"

LIST_API = f"{BASE}/items/clipping_pages"

DETAIL_API = f"{BASE}/items/page_menu_components"

OUTPUT_DIR = "docs/posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": BASE
}

session = requests.Session()


# =========================================================
# slug
# =========================================================
def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# =========================================================
# 1. ambil list berita
# =========================================================
def get_list(page=1):
    url = f"{LIST_API}?page={page}&limit=12&sort=-date_created"

    r = session.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    return r.json()


# =========================================================
# 2. ambil detail (pakai ID → API page_menu_components)
# =========================================================
def get_detail(content_id):
    url = f"{DETAIL_API}?filter[id]={content_id}&fields=components.id,components.code,content,setting,order"

    r = session.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    data = r.json()

    return data["data"][0]


# =========================================================
# 3. extract text dari HTML
# =========================================================
def extract(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


# =========================================================
# 4. main
# =========================================================
list_data = get_list()

items = list_data["data"]

print("TOTAL LIST:", len(items))

for item in items:

    try:
        print("=" * 60)
        print("SCRAPE:", item["name"])

        detail = get_detail(item["id"])

        html = detail["content"]

        text = extract(html)

        title = item["name"]

        slug = slugify(title)

        md = f"""---
title: "{title}"
date: "{item['date_created'][:10]}"
---

# {title}

{text}

Source:
{BASE}/berita/{item['slug']}
"""

        path = f"{OUTPUT_DIR}/{slug}.md"

        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

        print("SAVE:", slug)

        time.sleep(1.5)

    except Exception as e:
        print("ERROR:", repr(e))

print("SELESAI")
