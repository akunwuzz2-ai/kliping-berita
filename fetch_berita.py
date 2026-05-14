import requests
from bs4 import BeautifulSoup
import re
import json
import os

URL = "https://www.atrbpn.go.id/berita"

OUTPUT_DIR = "docs/posts"


def run():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    print("STATUS:", response.status_code)

    html = response.text

    # debug
    with open(
        "debug.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    # cari data hydration Nuxt/JSON
    patterns = [
        r'__NUXT__=(.*?);</script>',
        r'window\.__NUXT__=(.*?);</script>',
        r'<script id="__NUXT_DATA__".*?>(.*?)</script>'
    ]

    json_text = None

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.DOTALL
        )

        if match:
            json_text = match.group(1)
            break

    if not json_text:
        print("Hydration JSON tidak ditemukan")
        return

    print("Hydration ditemukan")

    # simpan debug json
    with open(
        "debug.json",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(json_text)

    # brute force cari slug berita
    slug_pattern = re.findall(
        r'"slug":"(.*?)"',
        json_text
    )

    title_pattern = re.findall(
        r'"name":"(.*?)"',
        json_text
    )

    print("Slug ditemukan:", len(slug_pattern))
    print("Title ditemukan:", len(title_pattern))

    homepage = []

    total = min(
        len(slug_pattern),
        len(title_pattern),
        10
    )

    for i in range(total):

        slug = slug_pattern[i]
        judul = (
            title_pattern[i]
            .replace('\\"', '"')
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
title: "{judul}"
date: 2026-05-15
---

# {judul}

[Baca Artikel Resmi]({url})
"""

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(markdown)

        homepage.append(
            f"- [{judul}](posts/{slug}.md)"
        )

        print("SAVE:", judul)

    with open(
        "docs/index.md",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("# Kliping Berita ATR/BPN\n\n")

        for item in homepage:
            f.write(item + "\n")

    print("SELESAI")


if __name__ == "__main__":
    run()
