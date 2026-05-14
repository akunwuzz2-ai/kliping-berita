import requests
from bs4 import BeautifulSoup
import os

def run():
    # Kita langsung mengakses halaman berita utama, bukan API
    target_url = "https://www.atrbpn.go.id/berita"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    folder_tujuan = "docs/posts"
    os.makedirs(folder_tujuan, exist_ok=True)

    print("Sedang memindai halaman berita ATR/BPN...")
    
    response = requests.get(target_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Mencari link berita di halaman tersebut
        berita_links = soup.select('a[href^="/berita/"]')
        
        count = 0
        for link in berita_links[:10]: # Kita ambil 10 berita terbaru
            href = link.get('href')
            slug = href.split('/')[-1]
            judul = link.get_text(strip=True)
            
            if not judul or len(slug) < 3:
                continue

            link_asli = f"https://www.atrbpn.go.id{href}"
            file_path = os.path.join(folder_tujuan, f"{slug}.md")
            
            # Metadata statis karena tanggal sulit diambil tanpa API
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write("date: 2026-05-15\n")
                f.write("---\n\n")
                f.write(f"# {judul}\n\n")
                f.write(f"Kliping berita terbaru dari ATR/BPN.\n\n")
                f.write(f"Baca selengkapnya di situs resmi: [Klik di Sini]({link_asli})\n")
            count += 1
        
        print(f"Berhasil! {count} kliping berita telah dibuat.")
    else:
        print(f"Gagal mengakses halaman. Status: {response.status_code}")

if __name__ == "__main__":
    run()
