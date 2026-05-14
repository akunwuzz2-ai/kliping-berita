import requests
import re
import os
import time
from bs4 import BeautifulSoup

BASE = "https://www.atrbpn.go.id"

BERITA_PAGE = f"{BASE}/berita"
DETAIL_API = f"{BASE}/items/page_menu_components"

OUTPUT_DIR = "docs/posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
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
# 1. ambil HTML halaman berita (SPA)
# =========================================================
def fetch_berita_html():
    r = session.get(BERITA_PAGE, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


# =========================================================
# 2. extract UUID dari HTML (INI KUNCI FIX)
# =========================================================
def extract_ids(html):
    # UUID pattern
    ids = re.findall(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", html)

    # unique
    return list(set(ids))


# =========================================================
# 3. ambil detail berita
# =========================================================
def fetch_detail(content_id):
    url = f"{DETAIL_API}?filter[id]={content_id}&fields=components.id,components.code,content,setting,order"

    r = session.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    data = r.json()

    return data["data"][0]


# =========================================================
# 4. convert HTML → text
# =========================================================
def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


# =========================================================
# MAIN
# =========================================================
print("Ambil halaman berita...")

html = fetch_berita_html()

ids = extract_ids(html)

print("TOTAL ID ditemukan:", len(ids))

if not ids:
    raise Exception("Tidak menemukan ID di halaman /berita (struktur berubah)")

# batasi biar aman di GitHub Actions
ids = ids[:12]


for cid in ids:

    try:
        print("=" * 60)
        print("SCRAPE ID:", cid)

        item = fetch_detail(cid)

        content_html = item["content"]

        text = html_to_text(content_html)

        title = BeautifulSoup(content_html, "html.parser").get_text(" ", strip=True)[:120]

        slug = slugify(title)

        md = f"""---
title: "{title}"
date: "{time.strftime('%Y-%m-%d')}"
---

# {title}

{text}

Source:
{BASE}
"""

        path = f"{OUTPUT_DIR}/{slug}.md"

        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

        print("SAVE:", slug)

        time.sleep(1.5)

    except Exception as e:
        print("ERROR:", repr(e))

print("SELESAI")
