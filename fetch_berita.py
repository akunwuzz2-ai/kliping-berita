import os
import re
import json
import requests

from bs4 import BeautifulSoup

BASE_URL = "https://www.atrbpn.go.id"

TOKEN = "VahmNYvhYD7a8P744r8bVIPTHeWzCJRm"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*"
}

API_URL = "https://www.atrbpn.go.id/items/clipping_pages?filter=%7B%22_and%22:%5B%7B%22clipping%22:%7B%22_eq%22:%22a871228a-5532-4b97-b7c3-3d5922897d79%22%7D%7D,%7B%22_and%22:%5B%7B%22archived%22:%7B%22_eq%22:%22false%22%7D%7D,%7B%22status%22:%7B%22_eq%22:%22published%22%7D%7D%5D%7D%5D%7D&fields=id,name,date_created,primary_image,slug&sort=-date_created&meta=filter_count&page=1&limit=12"

os.makedirs("docs/posts", exist_ok=True)

print("Mengambil berita...")

res = requests.get(API_URL, headers=HEADERS)

print("STATUS:", res.status_code)

data = res.json()["data"]

print("TOTAL:", len(data))

for item in data:

    title = item["name"]
    slug = item["slug"]
    date = item["date_created"][:10]

    print("=" * 60)
    print("SCRAPE:", title)

    article_url = f"{BASE_URL}/berita/{slug}"

    try:
        html = requests.get(article_url, headers=HEADERS).text

    except Exception as e:
        print("GAGAL BUKA HTML:", e)
        continue

    # simpan debug
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    # cari UUID component/page_menu
    match = re.search(
        r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
        html
    )

    component_id = None

    if match:
        component_id = match.group(0)

    print("COMPONENT:", component_id)

    content_text = "Isi artikel gagal diambil."

    if component_id:

        component_url = (
            "https://www.atrbpn.go.id/items/page_menu_components"
            f"?filter[id]={component_id}"
            "&fields=components.id,components.code,content,setting,order"
        )

        try:

            comp_res = requests.get(component_url, headers=HEADERS)

            print("COMP STATUS:", comp_res.status_code)

            comp_json = comp_res.json()

            with open("debug_component.json", "w", encoding="utf-8") as f:
                json.dump(comp_json, f, indent=2, ensure_ascii=False)

            comp_data = comp_json.get("data", [])

            if len(comp_data) > 0:

                html_content = comp_data[0].get("content", "")

                soup = BeautifulSoup(html_content, "html.parser")

                content_text = soup.get_text("\n")

                content_text = re.sub(r'\n+', '\n\n', content_text)

        except Exception as e:
            print("GAGAL COMPONENT:", e)

    md = f"""---
title: "{title}"
date: {date}
---

# {title}

{content_text}

---

Sumber resmi:

{article_url}
"""

    filename = f"docs/posts/{slug}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)

    print("SAVE:", slug)

print("SELESAI")
