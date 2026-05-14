import requests
import os
import json
import re
from bs4 import BeautifulSoup

# =========================
# TOKEN
# =========================
TOKEN = "VahmNYvhYD7a8P744r8bVIPTHeWzCJRm"

# =========================
# HEADERS
# =========================
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.atrbpn.go.id/berita",
    "Accept": "application/json, text/plain, */*"
}

# =========================
# API BERITA
# =========================
API_BERITA = (
    "https://www.atrbpn.go.id/items/clipping_pages"
    "?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:"
    "%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:"
    "%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:"
    "%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D"
    "&fields=*.*.*"
    "&sort=-date_created"
    "&page=1"
    "&limit=12"
)

# =========================
# FOLDER OUTPUT
# =========================
folder = "docs/posts"
os.makedirs(folder, exist_ok=True)

# =========================
# CLEAN HTML
# =========================
def clean_html(html):

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n")

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

# =========================
# AMBIL CONTENT COMPONENT
# =========================
def get_component_content(component_id):

    api = (
        "https://www.atrbpn.go.id/items/page_menu_components"
        f"?filter[id]={component_id}"
        "&fields=components.id,components.code,content,setting,order"
    )

    try:

        r = requests.get(api, headers=HEADERS, timeout=30)

        print("COMPONENT STATUS:", r.status_code)

        if r.status_code != 200:
            return ""

        result = r.json()

        data = result.get("data", [])

        if not data:
            return ""

        html = data[0].get("content", "")

        return clean_html(html)

    except Exception as e:

        print("ERROR COMPONENT:", e)

    return ""

# =========================
# CARI UUID COMPONENT
# =========================
def find_component_id(obj):

    if isinstance(obj, dict):

        for k, v in obj.items():

            # cari key yg mengandung component
            if "component" in k.lower():

                if isinstance(v, list):

                    for item in v:

                        if isinstance(item, dict):

                            component_id = item.get("id")

                            if component_id:
                                return component_id

                elif isinstance(v, dict):

                    component_id = v.get("id")

                    if component_id:
                        return component_id

            result = find_component_id(v)

            if result:
                return result

    elif isinstance(obj, list):

        for item in obj:

            result = find_component_id(item)

            if result:
                return result

    return None

# =========================
# MAIN
# =========================
def run():

    print("Mengambil berita...")

    r = requests.get(API_BERITA, headers=HEADERS, timeout=30)

    print("STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return

    result = r.json()

    data = result.get("data", [])

    print("TOTAL:", len(data))

    # DEBUG FULL JSON
    with open("full.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # LOOP BERITA
    for item in data:

        title = item.get("name", "Tanpa Judul")

        slug = item.get("slug", "tanpa-slug")

        date = item.get("date_created", "")[:10]

        print("=" * 60)

        print("SCRAPE:", title)

        # =========================
        # CARI COMPONENT ID
        # =========================
        component_id = find_component_id(item)

        print("COMPONENT:", component_id)

        content = ""

        if component_id:

            content = get_component_content(component_id)

        if not content:

            content = "Isi artikel gagal diambil."

        # =========================
        # URL ARTIKEL
        # =========================
        article_url = f"https://www.atrbpn.go.id/berita/{slug}"

        # =========================
        # FILEPATH
        # =========================
        filepath = os.path.join(folder, f"{slug}.md")

        # =========================
        # SAVE MARKDOWN
        # =========================
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

            f.write("\n")

        print("SAVE:", slug)

    print("SELESAI")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run()
