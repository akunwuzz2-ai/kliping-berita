from playwright.sync_api import sync_playwright
import json
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


def run():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context()

        page = context.new_page()

        print("Buka homepage...")

        # buka homepage dulu agar dapat cookie
        page.goto(
            "https://www.atrbpn.go.id",
            wait_until="domcontentloaded",
            timeout=120000
        )

        print("Ambil API...")

        response = context.request.get(
            API_URL,
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Accept": "application/json",
                "Referer": "https://www.atrbpn.go.id/berita"
            }
        )

        print("STATUS:", response.status)

        text = response.text()

        with open(
            "debug.json",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(text)

        if response.status != 200:
            print(text)
            return

        data = response.json().get(
            "data",
            []
        )

        print("TOTAL:", len(data))

        homepage = []

        for item in data:

            title = item["name"]
            slug = item["slug"]

            tanggal = (
                item["date_created"]
                .split("T")[0]
            )

            url = (
                "https://www.atrbpn.go.id/berita/"
                + slug
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

[Baca Artikel Resmi]({url})
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

            print("SAVE:", title)

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
