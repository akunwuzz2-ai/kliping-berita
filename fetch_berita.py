import os
import re
import time
import requests

from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
    "Accept": "text/html,application/xhtml+xml",
    "Connection": "keep-alive"
}

# session retry
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


print("Mengambil halaman berita...")

try:

    res = session.get(
        BERITA_URL,
        headers=HEADERS,
        timeout=60
    )

    print("STATUS:", res.status_code)

    if res.status_code != 200:
        raise Exception("Gagal buka halaman berita")

except Exception as e:
    raise Exception(f"Gagal koneksi: {str(e)}")

soup = BeautifulSoup(res.text, "html.parser")

links = soup.find_all("a", href=True)

berita = []

for a in links:

    href = a["href"]

    if "/berita/" not in href:
        continue

    title = a.get_text(strip=True)

    if len(title) < 15:
        continue

    url = href

    if not url.startswith("http"):
        url = BASE_URL + href

    berita.append({
        "title": title,
        "url": url
    })

# hapus duplikat
seen = set()
final_berita = []

for item in berita:

    if item["url"] not in seen:
        seen.add(item["url"])
        final_berita.append(item)

berita = final_berita[:12]

print("TOTAL:", len(berita))

for item in berita:

    try:

        print("=" * 60)
        print("SCRAPE:", item["title"])

        res = session.get(
            item["url"],
            headers=HEADERS,
            timeout=60
        )

        print("DETAIL STATUS:", res.status_code)

        soup = BeautifulSoup(res.text, "html.parser")

        paragraphs = soup.find_all("p")

        isi_list = []

        for p in paragraphs:

            txt = p.get_text(" ", strip=True)

            if len(txt) > 40:
                isi_list.append(txt)

        isi = "\n\n".join(isi_list)

        if not isi:
            isi = "Isi artikel gagal diambil."

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

        time.sleep(2)

    except Exception as e:

        print("ERROR:", str(e))

print("SELESAI")
