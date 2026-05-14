import os
import re
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ======================================================
# CONFIG
# ======================================================

POSTS_DIR = "docs/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

API_URL = (
    "https://www.atrbpn.go.id/items/clipping_pages"
    "?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D"
    "&fields=id,name,date_created,primary_image,slug"
    "&sort=-date_created"
    "&meta=filter_count"
    "&page=1"
    "&limit=12"
)

# ======================================================
# PLAYWRIGHT
# ======================================================

print("Menjalankan browser...")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    )

    page = context.new_page()

    # ==================================================
    # BUKA WEBSITE
    # ==================================================

    print("Buka homepage...")

    page.goto(
        "https://www.atrbpn.go.id/berita",
        wait_until="domcontentloaded",
        timeout=120000
    )

    time.sleep(10)

    # ==================================================
    # AMBIL COOKIES
    # ==================================================

    cookies = context.cookies()

    cookie_string = "; ".join(
        [f"{c['name']}={c['value']}" for c in cookies]
    )

    print("COOKIE DIDAPAT")

    # ==================================================
    # REQUEST SESSION
    # ==================================================

    session = requests.Session()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.atrbpn.go.id/berita",
        "Origin": "https://www.atrbpn.go.id",
        "Cookie": cookie_string
    }

    # ==================================================
    # GET LIST BERITA
    # ==================================================

    print("Mengambil berita API...")

    res = session.get(
        API_URL,
        headers=headers,
        timeout=120
    )

    print("STATUS:", res.status_code)

    if res.status_code != 200:
        raise Exception("Gagal ambil API")

    json_data = res.json()

    data = json_data.get("data", [])

    print("TOTAL:", len(data))

    # ==================================================
    # LOOP BERITA
    # ==================================================

    for item in data:

        print("=" * 60)

        title = item.get("name", "")
        slug = item.get("slug", "")
        berita_id = item.get("id", "")
        date = item.get("date_created", "")[:10]

        print("SCRAPE:", title)
        print("ID:", berita_id)

        # ==============================================
        # API KONTEN
        # ==============================================

        component_url = (
            "https://www.atrbpn.go.id/items/page_menu_components"
            f"?filter[id]={berita_id}"
            "&fields=components.id,components.code,content,setting,order"
        )

        component_res = session.get(
            component_url,
            headers=headers,
            timeout=120
        )

        print("COMPONENT STATUS:", component_res.status_code)

        isi_artikel = ""

        if component_res.status_code == 200:

            try:

                component_json = component_res.json()

                rows = component_json.get("data", [])

                print("COMPONENT TOTAL:", len(rows))

                for row in rows:

                    html = row.get("content", "")

                    if html:

                        soup = BeautifulSoup(html, "html.parser")

                        text = soup.get_text("\n")

                        text = re.sub(r"\n\s*\n", "\n\n", text)

                        isi_artikel += text.strip() + "\n\n"

            except Exception as e:
                print("ERROR PARSE:", e)

        # ==============================================
        # FALLBACK
        # ==============================================

        if not isi_artikel.strip():
            isi_artikel = "Isi artikel gagal diambil."

        berita_url = (
            f"https://www.atrbpn.go.id/berita/{slug}"
        )

        # ==============================================
        # MARKDOWN
        # ==============================================

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

        filename = f"{POSTS_DIR}/{slug}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown)

        print("SAVE:", filename)

        time.sleep(3)

    browser.close()

print("SELESAI")
