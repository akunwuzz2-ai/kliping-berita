from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

OUTPUT_DIR = "docs/posts"

API_URL = (
    "https://www.atrbpn.go.id/items/clipping_pages"
    "?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D"
    "&fields=id,name,date_created,primary_image,slug"
    "&sort=-date_created"
    "&meta=filter_count"
    "&page=1"
    "&limit=12"
)

TOKEN = "VahmNYvhYD7a8P744r8bVIPTHeWzCJRm"


def ambil_isi_artikel(page, url):

    try:

        print("BUKA:", url)

        page.goto(
            url,
            wait_until="networkidle",
            timeout=120000
        )

        # tunggu render JS
        page.wait_for_timeout(5000)

        html = page.content()

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        paragraphs = []

        # ambil semua paragraf
        for p in soup.select("p"):

            text = p.get_text(
                " ",
                strip=True
            )

            # filter text kecil
            if len(text) > 80:

                low = text.lower()

                # hindari footer/menu
                if "copyright" in low:
                    continue

                if "kementerian agraria" in low:
                    continue

                if "atr/bpn" in low and len(text) < 120:
                    continue

                paragraphs.append(text)

        print("PARAGRAF:", len(paragraphs))

        isi = "\n\n".join(
            paragraphs[:40]
        )

        return isi

    except Exception as e:

        print("GAGAL ARTIKEL:", e)

        return ""


def run():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context()

        page = context.new_page()

        print("Membuka homepage...")

        page.goto(
            "https://www.atrbpn.go.id",
            wait_until="domcontentloaded",
            timeout=120000
        )

        print("Mengambil API...")

        response = context.request.get(
            API_URL,
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Accept": "application/json",
                "Referer": "https://www.atrbpn.go.id/berita"
            }
        )

        print("STATUS API:", response.status)

        if response.status != 200:

            print(response.text())

            return

        data = response.json().get(
            "data",
            []
        )

        print("TOTAL BERITA:", len(data))

        homepage = []

        for item in data:

            title = item["name"]

            slug = item["slug"]

            tanggal = (
                item["date_created"]
                .split("T")[0]
            )

            article_url = (
                "https://www.atrbpn.go.id/berita/"
                + slug
            )

            print("=" * 50)
            print("SCRAPE:", title)

            isi_artikel = ambil_isi_artikel(
                page,
                article_url
            )

            if not isi_artikel:
                isi_artikel = (
                    "Isi artikel gagal diambil otomatis."
                )

            filepath = os.path.join(
                OUTPUT_DIR,
                f"{slug}.md"
            )

            markdown = f"""---
title: "{title}"
date: {tanggal}
---

# {title}

{isi_artikel}

---

## Sumber Resmi

{article_url}
"""

            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(markdown)

            homepage.append(
                f"- [{title}](posts/{slug}.md)"
            )

            print("SAVE:", slug)

        with open(
            "docs/index.md",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "# Kliping Berita ATR/BPN\n\n"
            )

            for item in homepage:
                f.write(item + "\n")

        browser.close()

        print("SELESAI")


if __name__ == "__main__":
    run()
