import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time

class ShredderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Güvenli Dosya Öğütücü")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        self.selected_file_path = None
        
        self._build_ui()

    def _build_ui(self):
        # Üst Başlık
        title_label = tk.Label(self.root, text="Güvenli Dosya Öğütücü", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=15)

        # 1. Dosya Seçim Alanı
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, fill="x", padx=20)
        
        self.file_label = tk.Label(file_frame, text="Seçilen Dosya: Yok", fg="gray", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)
        
        select_btn = tk.Button(file_frame, text="Dosya Seç", command=self.select_file, width=10)
        select_btn.pack(side="right", padx=5)

        # 2. Silme Metodu Seçim Alanı
        method_frame = tk.Frame(self.root)
        method_frame.pack(pady=15, fill="x", padx=20)
        
        method_label = tk.Label(method_frame, text="Silme Metodu Seçin:", anchor="w")
        method_label.pack(side="left")
        
        self.method_combobox = ttk.Combobox(method_frame, state="readonly", width=30)
        self.method_combobox['values'] = ("Sıfırla Doldur (Hızlı)", "DoD 5220.22-M (3 Geçiş)", "Gutmann (35 Geçiş)")
        self.method_combobox.current(1) # Varsayılan olarak DoD seçili gelir
        self.method_combobox.pack(side="right", padx=5)

        # 3. İlerleme Çubuğu (Progress Bar)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=460, mode="determinate")
        self.progress_bar.pack(pady=15)
        
        self.status_label = tk.Label(self.root, text="Bekleniyor...", fg="blue")
        self.status_label.pack()

        # 4. Öğütme Butonu
        self.shred_btn = tk.Button(self.root, text="DOSYAYI ÖĞÜT", bg="#d9534f", fg="white", font=("Helvetica", 10, "bold"), command=self.start_shredding_thread)
        self.shred_btn.pack(pady=15)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Öğütülecek Dosyayı Seçin")
        if file_path:
            self.selected_file_path = file_path
            # Dosya yolunun sadece son kısmını (adını) göstermek için
            file_name = file_path.split("/")[-1] 
            self.file_label.config(text=f"Seçilen Dosya: {file_name}", fg="black")

    def start_shredding_thread(self):
        if not self.selected_file_path:
            messagebox.showwarning("Uyarı", "Lütfen önce bir dosya seçin!")
            return
            
        selected_method = self.method_combobox.get()
        
        # Kullanıcıdan son bir onay alalım
        confirm = messagebox.askyesno("Kritik Uyarı", f"Bu dosya {selected_method} metodu ile KALICI olarak silinecektir.\n\nEmin misiniz?")
        
        if confirm:
            # Arayüzün donmaması için işlemi arka planda (Thread) başlatıyoruz
            self.shred_btn.config(state="disabled")
            self.progress_bar["value"] = 0
            
            shred_thread = threading.Thread(target=self.run_shredder_backend, args=(selected_method,))
            shred_thread.start()

    def run_shredder_backend(self, method):
        """
        ARKA PLAN KODLARINI BURAYA BAĞLAYACAKSINIZ.
        Bu fonksiyon ayrı bir thread'de çalıştığı için GUI'yi dondurmaz.
        """
        self.status_label.config(text=f"İşlem başlatılıyor: {method}")
        
        try:
            # TODO: Arkadaşınızın yazacağı 'ogutucu' sınıfını burada çağıracaksınız.
            # Şimdilik backend yazılana kadar sahte bir ilerleme simülasyonu yapıyoruz:
            
            total_steps = 100
            for i in range(total_steps):
                time.sleep(0.05) # Öğütme işlemi sürüyormuş gibi bekletiyoruz
                
                # İlerleme çubuğunu güncelleme (Thread içinden GUI güncellerken dikkatli olunmalıdır, Tkinter'da .after() kullanmak daha güvenlidir ama basitlik için direkt güncelliyoruz)
                self.progress_bar["value"] = i + 1
                self.status_label.config(text=f"İşleniyor... %{i+1}")
                self.root.update_idletasks() 
            
            # İşlem bittiğinde
            self.status_label.config(text="Dosya başarıyla yok edildi!", fg="green")
            messagebox.showinfo("Başarılı", "Dosya kalıcı olarak öğütüldü.")
            
            # Arayüzü sıfırla
            self.selected_file_path = None
            self.file_label.config(text="Seçilen Dosya: Yok", fg="gray")
            
        except Exception as e:
            self.status_label.config(text="Bir hata oluştu!", fg="red")
            messagebox.showerror("Hata", f"Silme işlemi sırasında hata: {str(e)}")
            
        finally:
            self.shred_btn.config(state="normal")
            self.progress_bar["value"] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = ShredderApp(root)
    root.mainloop()