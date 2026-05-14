import requests
import os

def run():
    api_url = "https://www.atrbpn.go.id/items/clipping_pages?fields=id,name,date_created,primary_image,slug&sort=-date_created&limit=15"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.atrbpn.go.id/berita"
    }

    if not os.path.exists("docs/posts"):
        os.makedirs("docs/posts", exist_ok=True)

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        items = response.json().get('data', [])
        for item in items:
            judul = item['name']
            slug = item['slug']
            tanggal = item['date_created'].split('T')[0]
            link_asli = f"https://www.atrbpn.go.id/berita/{slug}"

            file_path = f"docs/posts/{slug}.md"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"---\ndate: {tanggal}\n---\n\n# {judul}\n\n")
                f.write(f"Arsip: [Situs Resmi ATR/BPN]({link_asli})\n")
        print("Selesai mengupdate berita.")

if __name__ == "__main__":
    run()
