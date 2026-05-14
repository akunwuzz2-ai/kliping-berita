import requests
from bs4 import BeautifulSoup
import os
import re
import time

OUTPUT_DIR = "docs/posts"

TOKEN = "VahmNYvhYD7a8P744r8bVIPTHeWzCJRm"

LIST_URL = (
    "https://www.atrbpn.go.id/items/clipping_pages"
    "?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D"
    "&fields=id,name,date_created,slug"
    "&sort=-date_created"
    "&meta=filter_count"
    "&page=1"
    "&limit=12"
)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.atrbpn.go.id/berita",
    "Origin": "https://www.atrbpn.go.id",
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}


def ambil_component_id(slug):

    url = f"https://www.atrbpn.go.id/berita/{slug}"

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    print("DETAIL STATUS:", r.status_code)

    html = r.text

    with open(
        "debug_detail.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    pola = r'page_menu_components\?filter\[id\]=([a-z0-9\-]+)'

    hasil = re.findall(
        pola,
        html
    )

    if hasil:
        return hasil[0]

    return None


def ambil_konten(component_id):

    url = (
        "https://www.atrbpn.go.id/items/page_menu_components"
        f"?filter[id]={component_id}"
        "&fields=components.id,components.code,content,setting,order"
    )

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    print("CONTENT STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return ""

    data = r.json().get(
        "data",
        []
    )

    if not data:
        return ""

    html = data[0].get(
        "content",
        ""
    )

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    text = soup.get_text(
        "\n",
        strip=True
    )

    return text


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

    print("LIST STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return

    data = r.json().get(
        "data",
        []
    )

    print("TOTAL:", len(data))

    index_lines = []

    for item in data:

        try:

            title = item["name"]

            slug = item["slug"]

            tanggal = (
                item["date_created"]
                .split("T")[0]
            )

            print("=" * 60)
            print("SCRAPE:", title)

            component_id = ambil_component_id(
                slug
            )

            print("COMPONENT:", component_id)

            isi = ""

            if component_id:

                isi = ambil_konten(
                    component_id
                )

            if not isi:
                isi = "Isi artikel gagal diambil."

            article_url = (
                "https://www.atrbpn.go.id/berita/"
                + slug
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

            filepath = os.path.join(
                OUTPUT_DIR,
                f"{slug}.md"
            )

            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(markdown)

            index_lines.append(
                f"- [{title}](posts/{slug}.md)"
            )

            print("SAVE:", slug)

            time.sleep(3)

        except Exception as e:

            print("ERROR:", e)

    with open(
        "docs/index.md",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("# Kliping Berita ATR/BPN\n\n")

        for line in index_lines:
            f.write(line + "\n")

    print("SELESAI")


if __name__ == "__main__":
    run()
