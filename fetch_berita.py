import requests
import os

def run():
    api_url = "https://www.atrbpn.go.id/items/clipping_pages?fields=id,name,date_created,primary_image,slug&sort=-date_created&limit=15"
    
    # Headers yang lebih lengkap agar tidak dianggap robot (menghindari error 403)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.atrbpn.go.id",
        "Referer": "https://www.atrbpn.go.id/berita"
    }

    folder_tujuan = "docs/posts"
    os.makedirs(folder_tujuan, exist_ok=True)

    print("Sedang mengambil data berita...")
    
    # Menggunakan sesi agar lebih stabil
    session = requests.Session()
    response = session.get(api_url, headers=headers)
    
    if response.status_code == 200:
        items = response.json().get('data', [])
        for item in items:
            judul = item['name']
            slug = item['slug']
            tanggal = item['date_created'].split('T')[0]
            link_asli = f"https://www.atrbpn.go.id/berita/{slug}"

            file_path = os.path.join(folder_tujuan, f"{slug}.md")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write(f"date: {tanggal}\n")
                f.write("---\n\n")
                f.write(f"# {judul}\n\n")
                f.write(f"Dipublikasikan pada: {tanggal}\n\n")
                f.write(f"Baca selengkapnya di situs resmi: [Klik di Sini]({link_asli})\n")
        
        print(f"Berhasil! {len(items)} berita telah disimpan.")
    else:
        print(f"Gagal mengambil data. Status Code: {response.status_code}")
        # Jika masih 403, cetak sedikit isi errornya untuk analisa
        print(f"Pesan error: {response.text[:100]}")

if __name__ == "__main__":
    run()
