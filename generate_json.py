import json
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ==========================================
# KULLANICI AYARLARI (BURAYI KENDİNİZE GÖRE DÜZENLEYİN)
# ==========================================
BASE_URL = "[https://help.ornek-site.com](https://help.ornek-site.com)" # Sitenin kök URL'si
MAIN_PAGE_URL = "[https://help.ornek-site.com/bilgi-bankasi](https://help.ornek-site.com/bilgi-bankasi)" # Kazınacak ana kategori sayfası
JSON_FILENAME = "bilgibankasi_agaci.json" # Kaydedilecek JSON dosyasının adı

# CSS / XPATH Seçicileri (Farklı bir site kazınacaksa burası değiştirilmelidir)
ANA_KATEGORI_SECICI = ".ModuleItem__moduleTitle a" 
MAKALE_LINK_XPATH = "//a[contains(@href, '/articles/')]" 
# ==========================================

def main():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10) 
    agac_verisi = [] 

    try:
        print(f"[*] Ana sayfa yükleniyor: {MAIN_PAGE_URL}")
        driver.get(MAIN_PAGE_URL)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ANA_KATEGORI_SECICI)))
        
        ana_elementler = driver.find_elements(By.CSS_SELECTOR, ANA_KATEGORI_SECICI)
        ana_kategoriler = []
        
        for el in ana_elementler:
            baslik = el.text.strip()
            href = el.get_attribute("href")
            if href:
                ana_kategoriler.append({
                    "kategori_adi": baslik,
                    "kategori_url": urljoin(BASE_URL, href),
                    "alt_linkler": [] 
                })

        print(f"[+] Toplam {len(ana_kategoriler)} ana kategori bulundu. Sayfalar taranıyor...\n")

        for kategori in ana_kategoriler:
            print(f"\n📂 Kategori: {kategori['kategori_adi']}")
            kaydedilen_urller = set()
            sayfa_no = 1
            
            while True:
                sayfa_url = f"{kategori['kategori_url']}?page={sayfa_no}"
                print(f"  🔍 Taranıyor: Sayfa {sayfa_no}")
                driver.get(sayfa_url)
                
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, MAKALE_LINK_XPATH)))
                    alt_elementler = driver.find_elements(By.XPATH, MAKALE_LINK_XPATH)
                    yeni_makale_bulundu = False 
                    
                    for alt_el in alt_elementler:
                        alt_baslik = alt_el.text.strip()
                        alt_href = alt_el.get_attribute("href")
                        
                        if alt_href:
                            tam_alt_url = urljoin(BASE_URL, alt_href)
                            if tam_alt_url not in kaydedilen_urller and alt_baslik:
                                kategori["alt_linkler"].append({
                                    "baslik": alt_baslik,
                                    "url": tam_alt_url
                                })
                                kaydedilen_urller.add(tam_alt_url)
                                yeni_makale_bulundu = True
                                
                    if not yeni_makale_bulundu:
                        print("    ℹ️ Bu sayfada yeni makale bulunmadı, kategori tamamlandı.")
                        break 
                        
                    print(f"    ✅ Sayfa {sayfa_no} üzerinden {len(alt_elementler)} makale kontrol edildi.")
                    sayfa_no += 1
                    time.sleep(1) 
                    
                except TimeoutException:
                    print("    ℹ️ Başka sayfa kalmadı veya makale yok, kategori tamamlandı.")
                    break 
                except Exception as e:
                    print(f"    ⚠️ Beklenmeyen bir hata: {e}")
                    break

            agac_verisi.append(kategori)

        with open(JSON_FILENAME, "w", encoding="utf-8") as dosya:
            json.dump(agac_verisi, dosya, ensure_ascii=False, indent=4)
            
        print(f"\n[🚀] BİTTİ! Tüm sayfalar tarandı ve '{JSON_FILENAME}' dosyasına kaydedildi.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()