# Bilgi Bankası PDF Yedekleyici (Knowledge Base Scraper)

Bu proje, bir yardım merkezi veya bilgi bankasındaki (Knowledge Base) tüm makaleleri kategorilerine göre klasörleyerek yerel diskinize PDF formatında yedeklemenizi sağlayan açık kaynaklı bir Python/Selenium aracıdır.

Özellikle modern, lazy-loading (tembel yükleme) ve JavaScript tabanlı çalışan bilgi bankaları referans alınarak geliştirilmiştir. CSS seçicileri değiştirilerek Zendesk, Freshdesk, Intercom gibi birçok farklı sisteme kolayca uyarlanabilir.

## Özellikler

- Kategorileri ve alt makaleleri **JSON ağacı** olarak çıkarır.
- **Sayfalandırma** (Pagination – `?page=2`) desteği vardır.
- Sitenin Print düğmesini tetikleyerek **Chrome CDP** üzerinden saniyeler içinde anında PDF oluşturur.
- **Lazy Load bypass:** Tüm sayfayı JS ile tarayarak resimlerin ve altta kalan içeriklerin tam yüklenmesini sağlar.
- **Akıllı Devam Etme:** İşlem yarıda kesilirse, zaten indirilmiş PDF'leri atlayarak kaldığı yerden devam eder.

## Gereksinimler

- Python 3.7 veya üzeri
- Google Chrome tarayıcı

Gerekli Python kütüphanesini kurmak için terminalinizde şu komutu çalıştırın:

```bash
pip install selenium
```

## Nasıl Kullanılır?

### Adım 1: Bağlantıları Haritalayın

Öncelikle sitenin haritasını çıkarmak için `generate_json.py` dosyasını açın ve dosyanın en üstündeki **KULLANICI AYARLARI** bölümüne kendi hedef URL'nizi girin.

Ayarlarınızı yaptıktan sonra terminalinizde (veya komut satırında) aşağıdaki komutu çalıştırarak link haritasını çıkarın:

```bash
python generate_json.py
```

> **Not:** Bu işlem sonucunda, proje klasörünüzde tüm kategori ve makale linklerini hiyerarşik olarak içeren `bilgibankasi_agaci.json` adlı bir dosya oluşacaktır.

### Adım 2: PDF'leri İndirin

Bağlantı haritası başarıyla oluşturulduktan sonra, indirme işlemini başlatmak için aynı terminalde aşağıdaki komutu çalıştırın:

```bash
python download_pdfs.py
```

> **Not:** Betik çalışmaya başladığında `BilgiBankasi_PDFleri` adında bir ana klasör oluşturacak ve tüm makaleleri kendi kategorilerine ait alt klasörlerin içine PDF formatında otomatik olarak kaydedecektir.
