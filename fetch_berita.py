import requests
import os

def run():
    # Jalur API publik untuk mendapatkan daftar berita
    # Kita ambil judul (name), slug, dan tanggal (date_created)
    api_url = "https://www.atrbpn.go.id/items/clipping_pages?fields=name,slug,date_created&sort=-date_created&limit=10"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.atrbpn.go.id/berita"
    }

    folder_tujuan = "docs/posts"
    os.makedirs(folder_tujuan, exist_ok=True)

    print("Mengambil data berita melalui jalur API...")

    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        print("STATUS:", response.status_code)

        if response.status_code == 200:
            data_berita = response.json().get('data', [])
            count = 0

            for berita in data_berita:
                judul = berita.get('name')
                slug = berita.get('slug')
                # Format tanggal: YYYY-MM-DD
                tanggal = berita.get('date_created', '2026-05-15').split('T')[0]
                
                if not judul or not slug:
                    continue

                full_url = f"https://www.atrbpn.go.id/berita/{slug}"
                file_path = os.path.join(folder_tujuan, f"{slug}.md")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("---\n")
                    f.write(f"date: {tanggal}\n")
                    f.write("---\n\n")
                    f.write(f"# {judul}\n\n")
                    f.write(f"Dipublikasikan pada: {tanggal}\n\n")
                    f.write(f"Sumber resmi ATR/BPN: [Baca Selengkapnya]({full_url})\n")

                print(f"SAVE: {judul}")
                count += 1

            print(f"Total berita tersimpan: {count}")
        else:
            print(f"Gagal mengambil data. Pesan: {response.text[:200]}")

    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    run()
