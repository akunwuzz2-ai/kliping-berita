import requests
import os

def run():
    # URL API resmi ATR/BPN untuk mengambil berita terbaru
    api_url = "https://www.atrbpn.go.id/items/clipping_pages?fields=id,name,date_created,primary_image,slug&sort=-date_created&limit=15"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.atrbpn.go.id/berita"
    }

    # Pastikan folder penyimpanan berada di docs/posts agar terbaca oleh MkDocs
    folder_tujuan = "docs/posts"
    os.makedirs(folder_tujuan, exist_ok=True)

    print("Sedang mengambil data berita...")
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        items = response.json().get('data', [])
        for item in items:
            judul = item['name']
            slug = item['slug']
            # Ambil tanggal saja (YYYY-MM-DD)
            tanggal = item['date_created'].split('T')[0]
            link_asli = f"https://www.atrbpn.go.id/berita/{slug}"

            file_path = os.path.join(folder_tujuan, f"{slug}.md")
            
            # Menulis file dengan METADATA (---) agar tidak Error
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write(f"date: {tanggal}\n")
                f.write("---\n\n")
                f.write(f"# {judul}\n\n")
                f.write(f"Dipublikasikan pada: {tanggal}\n\n")
                f.write(f"Baca selengkapnya di situs resmi: [Klik di Sini]({link_asli})\n")
        
        print(f"Berhasil! {len(items)} berita telah disimpan di folder {folder_tujuan}.")
    else:
        print(f"Gagal mengambil data. Status Code: {response.status_code}")

if __name__ == "__main__":
    run()
