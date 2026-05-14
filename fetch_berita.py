from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

BASE_URL = "https://www.atrbpn.go.id"
URL = BASE_URL + "/berita"

def run():

    folder = "docs/posts"
    os.makedirs(folder, exist_ok=True)

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        print("Membuka website...")

        page.goto(
            URL,
            wait_until="networkidle",
            timeout=60000
        )

        # tunggu render JS
        page.wait_for_timeout(8000)

        html = page.content()

        # debug
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(html)

        soup = BeautifulSoup(html, "html.parser")

        links = soup.find_all("a", href=True)

        print("Total semua link:", len(links))

        hasil = []
        seen = set()

        for a in links:

            href = a.get("href", "").strip()

            if not href:
                continue

            full_url = urljoin(BASE_URL, href)

            # filter berita
            if "/berita/" not in full_url:
                continue

            judul = a.get_text(" ", strip=True)

            # fallback title
            if not judul:
                judul = a.get("title", "").strip()

            if len(judul) < 5:
                continue

            slug = full_url.rstrip("/").split("/")[-1]

            if slug in seen:
                continue

            seen.add(slug)

            hasil.append({
                "judul": judul,
                "url": full_url,
                "slug": slug
            })

        print("Ditemukan:", len(hasil))

        count = 0

        for item in hasil[:10]:

            filepath = os.path.join(
                folder,
                f"{item['slug']}.md"
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write("date: 2026-05-15\n")
                f.write("---\n\n")
                f.write(f"# {item['judul']}\n\n")
                f.write(
                    f"[Baca Selengkapnya]({item['url']})\n"
                )

            print("SAVE:", item["judul"])

            count += 1

        print("TOTAL:", count)

        browser.close()


if __name__ == "__main__":
    run()
