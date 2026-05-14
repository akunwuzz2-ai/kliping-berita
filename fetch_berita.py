import os
import re
import json
import time
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

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    )

    context = browser.new_context()

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
    # AMBIL API BERITA
    # ==================================================

    print("Mengambil API berita...")

    api_page = context.new_page()

    api_page.goto(
        API_URL,
        wait_until="networkidle",
        timeout=120000
    )

    body = api_page.locator("body").inner_text()

    data_json = json.loads(body)

    data = data_json.get("data", [])

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

        # ==============================================
        # API KONTEN
        # ==============================================

        component_url = (
            "https://www.atrbpn.go.id/items/page_menu_components"
            f"?filter[id]={berita_id}"
            "&fields=components.id,components.code,content,setting,order"
        )

        content_page = context.new_page()

        content_page.goto(
            component_url,
            wait_until="networkidle",
            timeout=120000
        )

        content_body = content_page.locator("body").inner_text()

        isi_artikel = ""

        try:

            component_json = json.loads(content_body)

            rows = component_json.get("data", [])

            print("COMPONENT:", len(rows))

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

        content_page.close()

        time.sleep(3)

    browser.close()

print("SELESAI")
