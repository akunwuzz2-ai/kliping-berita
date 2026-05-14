import requests
from bs4 import BeautifulSoup
import os
import re

URL = "https://www.atrbpn.go.id/berita"

OUTPUT_DIR = "docs/posts"


def run():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        ),
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"
    }

    print("Mengambil halaman...")

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    print("STATUS:", response.status_code)

    html = response.text

    # simpan html debug
    with open(
        "debug.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    # simpan sebagian text debug
    with open(
        "debug.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html[:20000])

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    berita = []

    # cari semua href berita
    for a in soup.find_all("a", href=True):

        href = a.get("href", "").strip()

        if "/berita/" not in href:
            continue

        text = a.get_text(
            strip=True
        )

        if len(text) < 10:
            continue

        if href.startswith("/"):
            full_url = (
                "https://www.atrbpn.go.id"
                + href
            )
        else:
            full_url = href

        slug = (
            href.rstrip("/")
            .split("/")[-1]
        )

        berita.append({
            "judul": text,
            "slug": slug,
            "url": full_url
        })

    # fallback regex kalau HTML kosong
    if len(berita) == 0:

        print("Fallback regex parsing...")

        slugs = re.findall(
            r'"slug":"(.*?)"',
            html
        )

        names = re.findall(
            r'"name":"(.*?)"',
            html
        )

        total = min(
            len(slugs),
            len(names)
        )

        for i in range(total):

            berita.append({
                "judul": names[i],
                "slug": slugs[i],
                "url": (
                    "https://www.atrbpn.go.id/berita/"
                    + slugs[i]
                )
            })

    print("TOTAL BERITA:", len(berita))

    homepage = []

    used = set()

    for item in berita[:12]:

        slug = item["slug"]

        if slug in used:
            continue

        used.add(slug)

        judul = item["judul"]
        url = item["url"]

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

    # homepage
    with open(
        "docs/index.md",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("# Kliping Berita ATR/BPN\n\n")

        if len(homepage) == 0:
            f.write(
                "Belum ada berita ditemukan.\n"
            )
        else:
            for item in homepage:
                f.write(item + "\n")

    print("SELESAI")


if __name__ == "__main__":
    run()
