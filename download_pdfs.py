import json
import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ==========================================
# KULLANICI AYARLARI (BURAYI KENDİNİZE GÖRE DÜZENLEYİN)
# ==========================================
JSON_DOSYASI = "bilgibankasi_agaci.json" # İlk betiğin oluşturduğu dosya
ANA_KLASOR = "BilgiBankasi_PDFleri" # PDF'lerin kaydedileceği ana klasör

# CSS Seçicileri (Farklı siteler için güncellenmeli)
ICERIK_KAPSAYICI_ID = "articleContent" # Makalenin ana div ID'si
YAZDIR_BUTONU_SECICI = "div[data-id='articlePrint']" # Sitenin kendi Print butonu
# ==========================================

def get_safe_filename(filename):
    return "".join([c for c in filename if c not in '<>:"/\\|?*'])

def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.page_load_strategy = 'eager' 
    # chrome_options.add_argument("--headless=new") # Arka planda çalıştırmak için açın
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    wait = WebDriverWait(driver, 15)

    try:
        if not os.path.exists(JSON_DOSYASI):
            print(f"[!] Hata: {JSON_DOSYASI} bulunamadı. Lütfen önce generate_json.py betiğini çalıştırın.")
            return

        with open(JSON_DOSYASI, "r", encoding="utf-8") as f:
            agac_verisi = json.load(f)

        os.makedirs(ANA_KLASOR, exist_ok=True)

        for kategori in agac_verisi:
            kategori_adi = kategori.get("kategori_adi", "İsimsiz")
            guvenli_kategori_adi = kategori_adi.replace('/', '-').replace(':', '')
            kategori_klasoru = os.path.join(ANA_KLASOR, guvenli_kategori_adi)
            os.makedirs(kategori_klasoru, exist_ok=True)
            
            print(f"\n📂 Kategori: {kategori_adi}")
            
            for makale in kategori.get("alt_linkler", []):
                baslik = makale.get("baslik")
                url = makale.get("url")
                
                dosya_yolu = os.path.join(kategori_klasoru, f"{get_safe_filename(baslik)}.pdf")
                
                if os.path.exists(dosya_yolu):
                    print(f"  ⏭️ Zaten var, atlanıyor: {baslik}")
                    continue
                
                print(f"  📄 İşleniyor: {baslik}")
                
                try:
                    driver.get(url)
                except TimeoutException:
                    print(f"  ⚠️ Hata: {baslik} sayfası zaman aşımına uğradı. Atlanıyor...")
                    continue
                except Exception:
                    continue
                
                try:
                    wait.until(EC.presence_of_element_located((By.ID, ICERIK_KAPSAYICI_ID)))
                    time.sleep(1)
                    
                    # Sayfadaki tüm elementleri render et (Lazy Load koruması)
                    driver.execute_script(f"""
                        var elements = document.querySelectorAll('#{ICERIK_KAPSAYICI_ID} *');
                        for (var i = 0; i < elements.length; i++) {{
                            elements[i].scrollIntoView();
                        }}
                    """)
                    time.sleep(2) 
                    
                    ana_pencere = driver.current_window_handle
                    driver.execute_script("window.print = function() {};") # Tarayıcı yazdırma engeli
                    
                    print_dugmesi = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, YAZDIR_BUTONU_SECICI)))
                    print_dugmesi.click()
                    time.sleep(2) 
                    
                    if len(driver.window_handles) > 1:
                        for handle in driver.window_handles:
                            if handle != ana_pencere:
                                driver.switch_to.window(handle)
                                break
                                
                    pdf_verisi = driver.execute_cdp_cmd("Page.printToPDF", {
                        "printBackground": True,
                        "landscape": False,
                        "paperWidth": 8.27,
                        "paperHeight": 11.69
                    })
                    
                    with open(dosya_yolu, "wb") as f:
                        f.write(base64.b64decode(pdf_verisi['data']))
                        
                    print("  ✅ Tam sayfa PDF kaydedildi.")
                    
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(ana_pencere)
                        
                except Exception as e:
                    print(f"  ⚠️ Hata: {baslik} işlenemedi. ({e})")
                    
                time.sleep(1)

        print("\n[🚀] BİTTİ! Tüm işlemler tamamlandı.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()