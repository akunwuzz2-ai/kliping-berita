from playwright.sync_api import sync_playwright
import requests
import os

OUTPUT_DIR = "docs/posts"

TOKEN = "VahmNYvhYD7a8P744r8bVIPTHeWzCJRm"

LIST_URL = (
    "https://www.atrbpn.go.id/items/clipping_pages"
    "?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D"
    "&fields=id,name,date_created,slug"
    "&sort=-date_created"
    "&page=1"
    "&limit=12"
)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Referer": "https://www.atrbpn.go.id/berita",
    "User-Agent": "Mozilla/5.0"
}


def ambil_detail(id_berita):

    url = f"https://www.atrbpn.go.id/items/clipping_pages/{id_berita}"

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    print("DETAIL STATUS:", r.status_code)

    if r.status_code != 200:
        return ""

    data = r.json().get("data", {})

    # coba beberapa field isi
    kemungkinan = [
        "content",
        "description",
        "body",
        "article",
        "isi",
        "news"
    ]

    for k in kemungkinan:

        isi = data.get(k)

        if isi and len(str(isi)) > 100:
            return str(isi)

    return str(data)


def run():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print("AMBIL LIST BERITA")

    r = requests.get(
        LIST_URL,
        headers=HEADERS,
        timeout=60
    )

    print("STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return

    data = r.json().get(
        "data",
        []
    )

    index = []

    for item in data:

        title = item["name"]

        slug = item["slug"]

        berita_id = item["id"]

        tanggal = (
            item["date_created"]
            .split("T")[0]
        )

        print("=" * 50)
        print("SCRAPE:", title)

        isi = ambil_detail(
            berita_id
        )

        article_url = (
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

{isi}

---

Sumber resmi:

{article_url}
"""

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(markdown)

        index.append(
            f"- [{title}](posts/{slug}.md)"
        )

        print("SAVE:", slug)

    with open(
        "docs/index.md",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("# Kliping Berita ATR/BPN\n\n")

        for x in index:
            f.write(x + "\n")

    print("SELESAI")


if __name__ == "__main__":
    run()
