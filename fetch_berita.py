import requests
import os

API_URL = "https://www.atrbpn.go.id/items/clipping_pages"

OUTPUT_DIR = "docs/posts"

FILTER = '{"_and":[{"clipping":{"_eq":"a871228a-5532-4b97-b7c3-3d5922897d79"}},{"_and":[{"archived":{"_eq":"false"}},{"status":{"_eq":"published"}}]}]}'


def run():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        ),
        "Accept": "application/json",
        "Referer": "https://www.atrbpn.go.id/berita",
        "Origin": "https://www.atrbpn.go.id",
        "X-Requested-With": "XMLHttpRequest"
    }

    params = {
        "filter": FILTER,
        "fields": "id,name,date_created,primary_image,slug",
        "sort": "-date_created",
        "meta": "filter_count",
        "page": 1,
        "limit": 12
    }

    print("Mengambil berita...")

    response = requests.get(
        API_URL,
        headers=headers,
        params=params,
        timeout=30
    )

    print("STATUS:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return

    json_data = response.json()

    data = json_data.get("data", [])

    print("TOTAL:", len(data))

    homepage_links = []

    for item in data:

        judul = item.get("name")
        slug = item.get("slug")

        tanggal = (
            item.get("date_created", "")
            .split("T")[0]
        )

        if not judul or not slug:
            continue

        artikel_url = (
            "https://www.atrbpn.go.id/berita/"
            + slug
        )

        filepath = os.path.join(
            OUTPUT_DIR,
            f"{slug}.md"
        )

        markdown = f"""---
title: "{judul}"
date: {tanggal}
---

# {judul}

Dipublikasikan: {tanggal}

[Baca Artikel Resmi]({artikel_url})
"""

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(markdown)

        homepage_links.append(
            f"- [{judul}](posts/{slug}.md)"
        )

        print("SAVE:", judul)

    # generate homepage
    with open(
        "docs/index.md",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("# Kliping Berita ATR/BPN\n\n")
        f.write("Update otomatis dari situs resmi.\n\n")

        for link in homepage_links:
            f.write(link + "\n")

    print("SELESAI")


if __name__ == "__main__":
    run()
