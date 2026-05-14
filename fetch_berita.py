import os
import re
import time
import requests
from bs4 import BeautifulSoup

# ======================================================
# CONFIG
# ======================================================

API_URL = "https://www.atrbpn.go.id/items/clipping_pages?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D&fields=id,name,date_created,primary_image,slug&sort=-date_created&meta=filter_count&page=1&limit=12"

POSTS_DIR = "docs/posts"

os.makedirs(POSTS_DIR, exist_ok=True)

# ======================================================
# SESSION + HEADERS
# ======================================================

session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.atrbpn.go.id/berita",
    "Connection": "keep-alive",
}

# ======================================================
# FUNCTION REQUEST DENGAN RETRY
# ======================================================

def safe_get(url, headers=None, retries=5):
    for i in range(retries):
        try:
            res = session.get(
                url,
                headers=headers,
                timeout=60
            )

            print(f"GET {url}")
            print("STATUS:", res.status_code)

            if res.status_code == 200:
                return res

        except Exception as e:
            print("ERROR:", e)

        wait = (i + 1) * 5
        print(f"Retry {wait} detik...")
        time.sleep(wait)

    return None

# ======================================================
# AMBIL LIST BERITA
# ======================================================

print("Mengambil berita...")

res = safe_get(API_URL, HEADERS)

if not res:
    raise Exception("Gagal ambil API berita")

data = res.json().get("data", [])

print("TOTAL:", len(data))

# ======================================================
# LOOP BERITA
# ======================================================

for item in data:

    print("=" * 60)

    title = item.get("name", "Tanpa Judul")
    slug = item.get("slug", "")
    date = item.get("date_created", "")[:10]
    berita_id = item.get("id")

    print("SCRAPE:", title)
    print("ID:", berita_id)

    # ==================================================
    # API KONTEN
    # ==================================================

    content_url = (
        "https://www.atrbpn.go.id/items/page_menu_components"
        f"?filter[id]={berita_id}"
        "&fields=components.id,components.code,content,setting,order"
    )

    content_res = safe_get(content_url, HEADERS)

    isi_artikel = ""

    if content_res:

        try:
            json_data = content_res.json()

            rows = json_data.get("data", [])

            print("COMPONENT TOTAL:", len(rows))

            for row in rows:

                html_content = row.get("content", "")

                if html_content:

                    soup = BeautifulSoup(html_content, "html.parser")

                    text = soup.get_text("\n")

                    text = re.sub(r"\n\s*\n", "\n\n", text)

                    isi_artikel += text.strip() + "\n\n"

        except Exception as e:
            print("GAGAL PARSE:", e)

    # ==================================================
    # FALLBACK
    # ==================================================

    if not isi_artikel.strip():
        isi_artikel = "Isi artikel gagal diambil."

    # ==================================================
    # LINK BERITA
    # ==================================================

    berita_url = f"https://www.atrbpn.go.id/berita/{slug}"

    # ==================================================
    # FORMAT MARKDOWN
    # ==================================================

    markdown = f"""---
title: "{title}"
date: {date}
---

# {title}

{isi_artikel}

---

Sumber resmi:

{berita_url}
"""

    # ==================================================
    # SAVE FILE
    # ==================================================

    filename = os.path.join(POSTS_DIR, f"{slug}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)

    print("SAVE:", slug)

    # delay biar tidak diblok server
    time.sleep(3)

print("SELESAI")
