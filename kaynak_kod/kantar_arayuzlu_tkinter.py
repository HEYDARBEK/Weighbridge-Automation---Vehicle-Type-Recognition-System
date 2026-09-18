import sys
import time
import os
import queue
import threading
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ultralytics import YOLO
import cv2
import tkinter as tk
from tkinter import scrolledtext, messagebox

# --- AYARLAR ---
CONFIG_DOSYASI_ADI = "config.txt"
MODEL_DOSYASI_ADI = "model.pt"
UCRET_TARIFESI = {
    "KAMYON": "150 TL",
    "TIR": "250 TL",
    "KAMYONET": "75 TL",
    "TRAKTOR": "50 TL",
    "BOS": "Ücret Yok",
}


# --- YARDIMCI FONKSİYONLAR ---
def get_application_path():
    """Hem .py script'i hem de .exe olarak çalışırken doğru ana yolu bulur."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


APP_PATH = get_application_path()
SONUC_CSV = os.path.join(APP_PATH, "sonuclar.csv")
SISTEM_GUNLUGU = os.path.join(APP_PATH, "sistem_gunlugu.txt")


def log_sistem(mesaj, q):
    """Tüm teknik mesajları sistem günlüğüne, konsola ve arayüze gönderir."""
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S")
    log_mesaji = f"[{timestamp}] - {mesaj}"
    print(log_mesaji)
    if q:
        q.put(log_mesaji)
    try:
        with open(SISTEM_GUNLUGU, "a", encoding="utf-8") as f:
            f.write(log_mesaji + "\n")
    except Exception as e:
        print(f"SİSTEM GÜNLÜĞÜ YAZMA HATASI: {e}")


def log_sonuc(veri_paketi, q):
    """Tespit sonucunu arayüze ve CSV dosyasına yazar."""
    sinif_adi = veri_paketi["AracTipi"]
    if sinif_adi == "Araç Bulunamadı":
        arayuz_mesaji = f"==> SONUÇ: {sinif_adi}"
    else:
        guven = veri_paketi["GuvenSkoru"]
        ucret = veri_paketi["Ucret"]
        arayuz_mesaji = (
            f"==> SONUÇ: {sinif_adi} (Güven: %{int(guven * 100)}), ÜCRET: {ucret}"
        )

    print(arayuz_mesaji)
    if q:
        q.put(arayuz_mesaji)

    csv_basliklari = ["ZamanDamgasi", "DosyaAdi", "AracTipi", "GuvenSkoru", "Ucret"]
    dosya_yoktu = not os.path.exists(SONUC_CSV)

    try:
        with open(SONUC_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_basliklari)
            if dosya_yoktu:
                writer.writeheader()
            writer.writerow(veri_paketi)
    except Exception as e:
        log_sistem(f"HATA: CSV dosyasına yazarken: {e}", q)


# --- ARKA PLAN İŞLEMLERİ ---
class YeniFotoğrafAlgılayıcı(FileSystemEventHandler):
    def __init__(self, model, q, izlenecek_klasor):
        self.model = model
        self.queue = q
        self.izlenecek_klasor = izlenecek_klasor
        self.basarili_klasoru = os.path.join(izlenecek_klasor, "Basarili_Taramalar")
        self.hatali_klasoru = os.path.join(izlenecek_klasor, "Incelenecekler")

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith((".png", ".jpg", ".jpeg")):
            log_sistem(
                f"Yeni dosya olayı algılandı: {os.path.basename(event.src_path)}",
                self.queue,
            )
            self.wait_for_file(event.src_path)

    def wait_for_file(self, file_path):
        retries = 5
        last_size = -1
        for i in range(retries):
            try:
                if os.path.exists(file_path):
                    current_size = os.path.getsize(file_path)
                    if current_size > 0 and current_size == last_size:
                        log_sistem(
                            f"Dosya hazır, işleniyor: '{os.path.basename(file_path)}'",
                            self.queue,
                        )
                        self.process_image(file_path)
                        return
                    last_size = current_size
            except:
                pass
            time.sleep(1)
        log_sistem(
            f"UYARI: '{os.path.basename(file_path)}' dosyası zamanında hazır hale gelmedi.",
            self.queue,
        )

    def process_image(self, image_path):
        try:
            ham_resim = cv2.imread(image_path)
            if ham_resim is None:
                log_sistem(
                    f"HATA: {os.path.basename(image_path)} dosyası okunamadı.",
                    self.queue,
                )
                return

            yukseklik, genislik, _ = ham_resim.shape
            en_boy_orani = genislik / yukseklik
            resim_isleme = (
                ham_resim[0 : yukseklik // 2, :] if en_boy_orani < 1.2 else ham_resim
            )
            results = self.model(resim_isleme, conf=0.60)

            dosya_adi = os.path.basename(image_path)
            zaman_damgasi = time.strftime("%d-%m-%Y %H:%M:%S")
            hedef_klasor = self.hatali_klasoru

            veri_paketi = {
                "ZamanDamgasi": zaman_damgasi,
                "DosyaAdi": dosya_adi,
                "AracTipi": "Araç Bulunamadı",
                "GuvenSkoru": 0,
                "Ucret": "",
            }

            if len(results[0].boxes) > 0:
                box = results[0].boxes[0]
                veri_paketi["AracTipi"] = self.model.names[int(box.cls[0])]
                veri_paketi["GuvenSkoru"] = round(float(box.conf[0]), 2)
                veri_paketi["Ucret"] = UCRET_TARIFESI.get(
                    veri_paketi["AracTipi"], "Tanımsız"
                )
                hedef_klasor = self.basarili_klasoru

            log_sonuc(veri_paketi, self.queue)

            try:
                if not os.path.exists(hedef_klasor):
                    os.makedirs(hedef_klasor)

                base, ext = os.path.splitext(dosya_adi)
                yeni_yol = os.path.join(hedef_klasor, f"{base}{ext}")
                sayac = 1
                while os.path.exists(yeni_yol):
                    yeni_yol = os.path.join(hedef_klasor, f"{base}_{sayac}{ext}")
                    sayac += 1

                os.rename(image_path, yeni_yol)

                sinif_adi_log = veri_paketi["AracTipi"]
                log_sistem(
                    f"Dosya '{os.path.basename(yeni_yol)}' işlendi ({sinif_adi_log}) ve '{os.path.basename(hedef_klasor)}' klasörüne taşındı.",
                    self.queue,
                )

            except FileNotFoundError:
                pass
            except Exception as e:
                log_sistem(f"HATA: Dosya taşıma sırasında: {e}", self.queue)
        except Exception as e:
            log_sistem(f"HATA: Görüntü işlenirken: {e}", self.queue)


def start_watcher(q, izlenecek_klasor, model_yolu):
    log_sistem("Yapay zeka modeli yükleniyor...", q)
    model = YOLO(model_yolu)
    log_sistem("Model başarıyla yüklendi.", q)
    event_handler = YeniFotoğrafAlgılayıcı(model, q, izlenecek_klasor)
    observer = Observer()
    observer.schedule(event_handler, izlenecek_klasor, recursive=False)
    observer.start()
    log_sistem(f"'{izlenecek_klasor}' klasörü dinleniyor... Sistem aktif.", q)
    try:
        while True:
            time.sleep(5)
    except:
        observer.stop()
    observer.join()
    log_sistem("Gözlemci durduruldu.", q)


# --- ARAYÜZ KODU (ANA PROGRAM) ---
class App:
    def __init__(self, root, q):
        self.root = root
        self.root.title("Kantar Otomasyon Sistemi")
        self.root.geometry("700x500")

        self.status_label = tk.Label(
            root, text="Durum: Başlatılıyor...", fg="orange", font=("Helvetica", 12)
        )
        self.status_label.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(
            root,
            state="disabled",
            height=25,
            width=90,
            bg="black",
            fg="white",
            font=("Consolas", 10),
        )
        self.log_text.pack(padx=10, pady=5)

        self.quit_button = tk.Button(
            root,
            text="Programdan Çık",
            command=root.destroy,
            bg="#c42b1c",
            fg="white",
            font=("Helvetica", 12),
        )
        self.quit_button.pack(pady=10, fill=tk.X, padx=10)

        self.q = q
        self.check_queue()

    def check_queue(self):
        try:
            message = self.q.get_nowait()
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)

            if "dinleniyor" in message:
                self.status_label.config(
                    text="Durum: Aktif - Yeni Fotoğraf Bekleniyor", fg="green"
                )
            if "SONUÇ" in message:
                self.status_label.config(
                    text="Durum: Son Tespit Tamamlandı!", fg="cyan"
                )
            if "HATA" in message or "UYARI" in message:
                self.status_label.config(text="Durum: Hata/Uyarı Oluştu!", fg="red")
        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)


if __name__ == "__main__":
    app_path = get_application_path()
    config_path = os.path.join(app_path, CONFIG_DOSYASI_ADI)
    model_path = os.path.join(app_path, MODEL_DOSYASI_ADI)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            izlenecek_klasor = f.read().strip()
    except FileNotFoundError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Yapılandırma Hatası",
            f"HATA: '{config_path}' bulunamadı! Lütfen programın çalışacağı klasörde bu dosyayı oluşturun.",
        )
        exit()

    q = queue.Queue()
    threading.Thread(
        target=start_watcher, args=(q, izlenecek_klasor, model_path), daemon=True
    ).start()

    root = tk.Tk()
    app = App(root, q)
    root.mainloop()
