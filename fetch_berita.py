import requests
from bs4 import BeautifulSoup
import os

def run():
    target_url = "https://www.atrbpn.go.id/berita"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    folder_tujuan = "docs/posts"
    os.makedirs(folder_tujuan, exist_ok=True)

    print("Sedang memindai halaman berita ATR/BPN...")
    response = requests.get(target_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Taktik baru: cari semua link yang mengandung kata '/berita/'
        links = soup.find_all('a', href=True)
        
        count = 0
        for link in links:
            href = link['href']
            if "/berita/" in href and len(href) > 10:
                slug = href.split('/')[-1]
                judul = link.get_text(strip=True)
                
                if not judul or len(judul) < 5: continue

                link_asli = f"https://www.atrbpn.go.id{href}" if href.startswith('/') else href
                file_path = os.path.join(folder_tujuan, f"{slug}.md")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("---\ndate: 2026-05-15\n---\n\n")
                    f.write(f"# {judul}\n\n")
                    f.write(f"Kliping berita ATR/BPN.\n\n")
                    f.write(f"Baca selengkapnya: [Klik di Sini]({link_asli})\n")
                count += 1
                if count >= 10: break # Ambil 10 saja
        
        print(f"Berhasil! {count} kliping berita telah dibuat.")
    else:
        print(f"Gagal. Status: {response.status_code}")

if __name__ == "__main__":
    run()
