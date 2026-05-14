import requests
from bs4 import BeautifulSoup
import os

def run():
    url = "https://www.atrbpn.go.id/berita"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    folder = "docs/posts"
    os.makedirs(folder, exist_ok=True)

    try:
        response = requests.get(url, headers=headers, timeout=20)

        print("STATUS:", response.status_code)

        html = response.text

        # DEBUG SIMPAN HTML
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(html)

        soup = BeautifulSoup(html, "html.parser")

        berita_links = []

        # cari semua link berita
        for a in soup.select("a[href]"):
            href = a.get("href", "")

            if "/berita/" in href:
                judul = a.get_text(strip=True)

                if len(judul) > 5:
                    berita_links.append((judul, href))

        print("Ditemukan:", len(berita_links))

        seen = set()
        count = 0

        for judul, href in berita_links:

            if href in seen:
                continue

            seen.add(href)

            slug = href.rstrip("/").split("/")[-1]

            if href.startswith("/"):
                full_url = "https://www.atrbpn.go.id" + href
            else:
                full_url = href

            filepath = os.path.join(folder, f"{slug}.md")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write("date: 2026-05-15\n")
                f.write("---\n\n")
                f.write(f"# {judul}\n\n")
                f.write(f"[Baca Selengkapnya]({full_url})\n")

            print("SAVE:", judul)

            count += 1

            if count >= 10:
                break

        print("TOTAL:", count)

    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    run()
