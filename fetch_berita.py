import requests
import os

BASE_URL = "https://www.atrbpn.go.id"

OUTPUT_DIR = "docs/posts"


def get_token(session):

    url = (
        f"{BASE_URL}/users"
        "?filter[domain]=www.atrbpn.go.id"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"{BASE_URL}/berita",
        "Origin": BASE_URL,
        "Accept": "application/json"
    }

    r = session.get(
        url,
        headers=headers,
        timeout=30
    )

    print("USER STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return None

    data = r.json()

    token = (
        data.get("data", {})
        .get("token")
    )

    return token


def fetch_berita(session, token):

    url = f"{BASE_URL}/items/clipping_pages"

    filter_query = (
        '{"_and":[{"clipping":{"_eq":"a871228a-5532-4b97-b7c3-3d5922897d79"}},'
        '{"_and":[{"archived":{"_eq":"false"}},'
        '{"status":{"_eq":"published"}}]}]}'
    )

    params = {
        "filter": filter_query,
        "fields": (
            "id,name,date_created,"
            "primary_image,slug"
        ),
        "sort": "-date_created",
        "meta": "filter_count",
        "page": 1,
        "limit": 12
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": f"{BASE_URL}/berita",
        "Origin": BASE_URL,
        "Authorization": f"Bearer {token}"
    }

    r = session.get(
        url,
        params=params,
        headers=headers,
        timeout=30
    )

    print("BERITA STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return []

    return r.json().get("data", [])


def save_markdown(items):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    homepage = []

    for item in items:

        judul = item.get("name")
        slug = item.get("slug")

        tanggal = (
            item.get("date_created", "")
            .split("T")[0]
        )

        if not judul or not slug:
            continue

        url = (
            f"{BASE_URL}/berita/{slug}"
        )

        filepath = os.path.join(
            OUTPUT_DIR,
            f"{slug}.md"
        )

        content = f"""---
title: "{judul}"
date: {tanggal}
---

# {judul}

Dipublikasikan: {tanggal}

[Baca Artikel Resmi]({url})
"""

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(content)

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

        for link in homepage:
            f.write(link + "\n")


def run():

    session = requests.Session()

    print("Mengambil token...")

    token = get_token(session)

    print("TOKEN:", token)

    if not token:
        print("Token gagal didapat")
        return

    print("Mengambil berita...")

    berita = fetch_berita(
        session,
        token
    )

    print("TOTAL:", len(berita))

    save_markdown(berita)

    print("SELESAI")


if __name__ == "__main__":
    run()
