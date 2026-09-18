# Kantar Otomasyonu - Araç Tipi Tanıma Sistemi
**Versiyon: 1.0**
**Tarih: 07.10.2025**

---

## 🚀 Projenin Amacı

Bu proje, bir kantar üzerine gelen araçların (Tır, Kamyon, Traktör, Kamyonet ve Boş) kamera görüntülerinden otomatik olarak tespit edilmesi için geliştirilmiş bir yapay zeka sistemidir.

Sistemin temel hedefi, kantar tartım sürecini otomatize ederek, araç tipine göre farklı işlemlerin (ücretlendirme, sınıflandırma vb.) otomatik olarak yapılmasını sağlamaktır.
## ⚠️ Proje Kapsamı ve Sınırlamalar

Bu proje, belirli bir işletmenin mevcut kantar ve kamera sistemine yönelik olarak geliştirilmiştir. Model, bu sistemden elde edilen görüntüler kullanılarak eğitilmiş ve kamera konumu, görüntüleme açısı ve görüntü formatı gibi işletmeye özgü koşullar dikkate alınmıştır.

Bu nedenle model ve görüntü işleme adımları farklı kamera sistemleri veya farklı çalışma ortamlarında doğrudan aynı performansı göstermeyebilir. Farklı sistemlere uyarlanması durumunda veri setinin yeniden hazırlanması, modelin yeniden eğitilmesi veya görüntü işleme adımlarının değiştirilmesi gerekebilir.

## ✨ Temel Özellikler

- **Otomatik Tespit:** Belirlenen bir klasörü sürekli dinler ve yeni eklenen resimleri anında işler.
- **Arayüz:** Operatörün sistemin çalıştığını ve sonuçları anlık olarak görmesini sağlayan bir arayüze sahiptir.
- **Esnek Yapılandırma:** İzlenecek klasör yolu, `.exe`'nin yanına konulan basit bir `config.txt` dosyası üzerinden kolayca değiştirilebilir.
- **Akıllı Ön İşleme:** Gelen ham (dikey) veya kırpılmış (yatay) görüntülerin en-boy oranını analiz ederek en uygun işleme yöntemini otomatik olarak seçer.
- **Kalıcı Kayıt:** Hem operatörler için temiz bir sonuç dosyası (`sonuclar.csv`) hem de teknik takip için detaylı bir sistem günlüğü (`sistem_gunlugu.txt`) tutar.

## 🛠️ Kullanılan Teknolojiler

- **Python 3.10**
- **PyTorch & Ultralytics YOLO** (Nesne Tespiti Modeli)
- **OpenCV** (Görüntü İşleme)
- **Tkinter** (Arayüz)
- **Watchdog** (Klasör Gözlemleme)

## ⚙️ Kurulum ve Çalıştırma

1.  **Ortam Kurulumu:** Projenin ihtiyaç duyduğu tüm kütüphaneler `requirements.txt` dosyasında listelenmiştir. Yeni bir sanal ortam oluşturulduktan sonra, aşağıdaki komut ile tüm bağımlılıklar tek seferde kurulabilir:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Yapılandırma:** Programın çalışması için, programla aynı dizinde `model.pt` (eğitilmiş model) ve `config.txt` (ayar dosyası) bulunmalıdır. `config.txt` dosyasının içine, kamera görüntülerinin kaydedileceği klasörün tam yolu yazılmalıdır.

3.  **Çalıştırma (Test için):** Projenin ana dizinindeyken aşağıdaki komutla test edilebilir:
    ```bash
    python kaynak_kod/kantar_arayuzlu_tkinter.py
    ```

## 🧠 Model Bilgileri

Eğitilmiş yapay zeka modeli, ana dizinde bulunan **`model.pt`** dosyasıdır. Bu model, aşağıdaki 5 sınıfı tanıyacak şekilde eğitilmiştir. Modelin çıktısı olan sınıf ID'leri (0'dan başlayarak) bu sıralamaya göredir:

- `0: TRAKTOR`
- `1: TIR`
- `2: KAMYONET`
- `3: KAMYON`
- `4: BOS`

## ⚠️ **KRİTİK NOT: Ön İşleme (Pre-processing) Mantığı**

Bu model, dikey formatta gelen ham görüntülerin **sadece üst yarısı** kullanılarak eğitilmiştir. `kantar_arayuzlu_tkinter.py` script'i, gelen görüntülerin en-boy oranını (`genişlik / yükseklik`) kontrol eden ve buna göre otomatik kırpma işlemi uygulayan **akıllı bir mantık** içermektedir.

Modelin canlı sistemde doğru çalışması için, bu ön işleme mantığının, entegre edileceği son uygulamada da **birebir korunması kritik öneme sahiptir.** Örnek kod, bu mantığı `process_image` fonksiyonu içinde detaylı bir şekilde barındırmaktadır.
## AKILLI KIRPMA --> 
(yukseklik, genislik, _ = ham_resim.shape
en_boy_orani = genislik / yukseklik
resim_isleme = ham_resim[0:yukseklik//2, :] if en_boy_orani < 1.2 else ham_resim)
