import requests
import os
import re
from bs4 import BeautifulSoup

TOKEN = "VahmNYvhYD7a8P744r8bVIPTHeWzCJRm"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.atrbpn.go.id/berita",
    "Accept": "application/json, text/plain, */*"
}

API_BERITA = (
    "https://www.atrbpn.go.id/items/clipping_pages"
    "?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:"
    "%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:"
    "%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:"
    "%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D"
    "&fields=*"
    "&sort=-date_created"
    "&page=1"
    "&limit=12"
)

folder = "docs/posts"
os.makedirs(folder, exist_ok=True)


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n")

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def get_component_id(slug):
    url = f"https://www.atrbpn.go.id/berita/{slug}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)

        html = r.text

        # simpan debug
        with open("debug_article.html", "w", encoding="utf-8") as f:
            f.write(html)

        # cari UUID component
        match = re.search(
            r'page_menu_components\?filter\[id\]=([a-f0-9\-]{36})',
            html
        )

        if match:
            return match.group(1)

    except Exception as e:
        print("GAGAL buka artikel:", e)

    return None


def get_article_content(component_id):
    api = (
        "https://www.atrbpn.go.id/items/page_menu_components"
        f"?filter[id]={component_id}"
        "&fields=components.id,components.code,content,setting,order"
    )

    try:
        r = requests.get(api, headers=HEADERS, timeout=30)

        if r.status_code != 200:
            print("API component gagal:", r.status_code)
            return ""

        data = r.json().get("data", [])

        if not data:
            return ""

        html = data[0].get("content", "")

        return clean_html(html)

    except Exception as e:
        print("GAGAL ambil component:", e)

    return ""


def run():
    print("Mengambil berita...")

    r = requests.get(API_BERITA, headers=HEADERS, timeout=30)

    print("STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return

    data = r.json().get("data", [])

    print("TOTAL:", len(data))

    for item in data:

        title = item.get("name")
        slug = item.get("slug")
        date = item.get("date_created", "")[:10]

        print("=" * 60)
        print("SCRAPE:", title)

        component_id = get_component_id(slug)

        print("COMPONENT:", component_id)

        content = ""

        if component_id:
            content = get_article_content(component_id)

        if not content:
            content = "Isi artikel gagal diambil."

        filepath = os.path.join(folder, f"{slug}.md")

        article_url = f"https://www.atrbpn.go.id/berita/{slug}"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"title: {title}\n")
            f.write(f"date: {date}\n")
            f.write("---\n\n")

            f.write(f"# {title}\n\n")

            f.write(content)

            f.write("\n\n---\n\n")

            f.write("Sumber resmi:\n\n")

            f.write(article_url)

        print("SAVE:", slug)

    print("SELESAI")


if __name__ == "__main__":
    run()
