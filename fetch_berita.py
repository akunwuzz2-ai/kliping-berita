import requests
import os

def run():
    # Menggunakan jalur berita umum yang biasanya lebih terbuka (public)
    api_url = "https://www.atrbpn.go.id/items/berita?fields=id,judul,tgl_publikasi,gambar_utama,slug&sort=-tgl_publikasi&limit=15"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.atrbpn.go.id/berita"
    }

    folder_tujuan = "docs/posts"
    os.makedirs(folder_tujuan, exist_ok=True)

    print("Mencoba mengambil data dari jalur berita umum...")
    
    session = requests.Session()
    response = session.get(api_url, headers=headers)
    
    if response.status_code == 200:
        items = response.json().get('data', [])
        if not items:
            print("Koneksi berhasil, tapi tidak ada data yang ditemukan.")
            return

        for item in items:
            # Penyesuaian nama kolom (judul & tgl_publikasi)
            judul = item.get('judul', 'Tanpa Judul')
            slug = item.get('slug', 'no-slug')
            tanggal = item.get('tgl_publikasi', '2026-05-15').split('T')[0]
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
        print(f"Gagal lagi. Status Code: {response.status_code}")
        print(f"Pesan error: {response.text[:150]}")

if __name__ == "__main__":
    run()
