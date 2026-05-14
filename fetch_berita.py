import os
import re
import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.atrbpn.go.id"
BERITA_URL = "https://www.atrbpn.go.id/berita"

OUTPUT_DIR = "docs/posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
}

session = requests.Session()

retry = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[403, 429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("http://", adapter)
session.mount("https://", adapter)


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def normalize_url(url):
    return urljoin(BASE_URL, url)


print("Mengambil halaman berita...")

res = session.get(BERITA_URL, headers=HEADERS, timeout=60)

print("STATUS:", res.status_code)

# DEBUG kalau kosong / kena JS render
if len(res.text) < 1000:
    raise Exception("HTML terlalu kecil, kemungkinan diblok atau JS-rendered")

soup = BeautifulSoup(res.text, "html.parser")

# =========================================================
# 1. Coba ambil artikel dari struktur modern (lebih akurat)
# =========================================================
articles = soup.select("article a[href]")

berita = []

for a in articles:
    href = a.get("href", "")
    title = a.get_text(" ", strip=True)

    if "berita" not in href:
        continue

    if len(title) < 10:
        continue

    berita.append({
        "title": title,
        "url": normalize_url(href)
    })


# =========================================================
# 2. Fallback kalau article kosong
# =========================================================
if not berita:
    print("Fallback parsing semua link...")

    links = soup.find_all("a", href=True)

    for a in links:
        href = a["href"]
        title = a.get_text(" ", strip=True)

        if "berita" not in href:
            continue

        if len(title) < 10:
            continue

        berita.append({
            "title": title,
            "url": normalize_url(href)
        })


# =========================================================
# 3. Hapus duplikat
# =========================================================
seen = set()
unique = []

for item in berita:
    if item["url"] not in seen:
        seen.add(item["url"])
        unique.append(item)

berita = unique[:12]

print("TOTAL:", len(berita))

if not berita:
    print("HTML snippet:")
    print(res.text[:1500])
    raise Exception("Tidak menemukan berita - kemungkinan struktur website berubah")


# =========================================================
# 4. Scrape detail artikel
# =========================================================
for item in berita:

    try:
        print("=" * 60)
        print("SCRAPE:", item["title"])

        res = session.get(item["url"], headers=HEADERS, timeout=60)

        soup = BeautifulSoup(res.text, "html.parser")

        # ambil artikel utama dulu
        container = soup.find("article") or soup

        paragraphs = container.find_all("p")

        isi_list = []

        for p in paragraphs:
            txt = p.get_text(" ", strip=True)
            if len(txt) > 40:
                isi_list.append(txt)

        isi = "\n\n".join(isi_list)

        if not isi:
            isi = "Isi artikel tidak ditemukan (struktur berubah)."

        slug = slugify(item["title"])

        markdown = f"""---
title: "{item['title']}"
date: "{time.strftime('%Y-%m-%d')}"
---

# {item['title']}

{isi}

Sumber resmi:

{item['url']}
"""

        filepath = f"{OUTPUT_DIR}/{slug}.md"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)

        print("SAVE:", slug)

        time.sleep(2 + time.random() * 2 if hasattr(time, "random") else 2)

    except Exception as e:
        print("ERROR:", repr(e))


print("SELESAI")
