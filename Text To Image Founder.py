import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
from datetime import datetime

class TextToImageGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Metin-Görsel Dönüştürücü")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2E3440')
        
        # Unsplash API anahtarı (ücretsiz)
        self.api_key = "FiVdcaS4MM07tgqbzIWoSJkUCz69VIpejSdDYrfE47g"
        
        # Görsel geçmişi
        self.image_history = []
        
        self.create_gui()
        
    def create_gui(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Sol panel
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='both', padx=5, pady=5)
        
        # Metin girişi
        ttk.Label(left_panel, text="Aramak istediğiniz görseli tanımlayın:").pack(pady=5)
        self.text_input = scrolledtext.ScrolledText(left_panel, height=10, width=50)
        self.text_input.pack(pady=5)
        
        # Sonuç sayısı
        ttk.Label(left_panel, text="Gösterilecek sonuç sayısı:").pack(pady=5)
        self.result_var = tk.IntVar(value=4)
        result_scale = ttk.Scale(left_panel, from_=1, to=10, 
                               variable=self.result_var, orient='horizontal')
        result_scale.pack(fill='x', padx=5)
        
        # Sıralama seçenekleri
        sort_frame = ttk.LabelFrame(left_panel, text="Sıralama")
        sort_frame.pack(pady=10, fill='x')
        
        self.sort_var = tk.StringVar(value="relevant")
        sorts = [
            ("İlgililik", "relevant"),
            ("En Yeni", "latest"),
            ("Popüler", "popular")
        ]
        
        for text, value in sorts:
            ttk.Radiobutton(sort_frame, text=text, value=value, 
                          variable=self.sort_var).pack(anchor='w')
        
        # Oluştur butonu
        ttk.Button(left_panel, text="Görsel Ara", 
                  command=self.search_images).pack(pady=10)
        
        # Kaydet butonu
        ttk.Button(left_panel, text="Görseli Kaydet", 
                  command=self.save_image).pack(pady=5)
        
        # Sağ panel - Görsel önizleme
        self.right_panel = ttk.Frame(main_frame)
        self.right_panel.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Durum çubuğu
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var)
        self.status_bar.pack(side='bottom', fill='x')
        
    def search_images(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            self.status_var.set("Lütfen bir metin girin!")
            return
            
        try:
            self.status_var.set("Görseller aranıyor...")
            self.root.update()
            
            # API'ye sorgu gönder
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": text,
                "per_page": self.result_var.get(),
                "order_by": self.sort_var.get(),
                "client_id": self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                images = data.get('results', [])
                
                if not images:
                    self.status_var.set("Görsel bulunamadı!")
                    return
                
                # Mevcut görselleri temizle
                for widget in self.right_panel.winfo_children():
                    widget.destroy()
                
                # Grid için satır ve sütun sayısını hesapla
                num_results = len(images)
                cols = 2
                rows = (num_results + 1) // cols
                
                # Görselleri göster
                for i, img_data in enumerate(images):
                    try:
                        # Görseli indir
                        img_url = img_data['urls']['regular']
                        img_response = requests.get(img_url)
                        image = Image.open(BytesIO(img_response.content))
                        
                        # Görsel boyutunu ayarla
                        image.thumbnail((400, 400))
                        
                        # Görsel geçmişine ekle
                        self.image_history.append({
                            'image': image,
                            'prompt': text,
                            'timestamp': datetime.now(),
                            'photographer': img_data['user']['name'],
                            'url': img_data['links']['html']
                        })
                        
                        # Frame oluştur
                        img_frame = ttk.Frame(self.right_panel)
                        img_frame.grid(row=i//cols, column=i%cols, padx=5, pady=5)
                        
                        # Görseli göster
                        photo = ImageTk.PhotoImage(image)
                        label = ttk.Label(img_frame, image=photo)
                        label.image = photo
                        label.pack()
                        
                        # Fotoğrafçı bilgisi
                        credit_label = ttk.Label(img_frame, 
                                               text=f"Fotoğraf: {img_data['user']['name']}")
                        credit_label.pack()
                        
                    except Exception as e:
                        print(f"Görsel yükleme hatası: {str(e)}")
                        continue
                
                self.status_var.set(f"{num_results} görsel bulundu!")
                
            else:
                self.status_var.set(f"API Hatası: {response.status_code}")
                
        except Exception as e:
            self.status_var.set(f"Hata: {str(e)}")
    
    def save_image(self):
        if not self.image_history:
            self.status_var.set("Kaydedilecek görsel bulunamadı!")
            return
            
        # Son oluşturulan görseli kaydet
        latest_image = self.image_history[-1]
        
        # Klasör oluştur
        if not os.path.exists("downloaded_images"):
            os.makedirs("downloaded_images")
        
        # Dosya adı oluştur
        timestamp = latest_image['timestamp'].strftime("%Y%m%d_%H%M%S")
        filename = f"downloaded_images/image_{timestamp}.png"
        
        try:
            latest_image['image'].save(filename)
            
            # Kredi bilgisi dosyası
            credit_file = f"downloaded_images/image_{timestamp}_credits.txt"
            with open(credit_file, 'w', encoding='utf-8') as f:
                f.write(f"Fotoğraf: {latest_image['photographer']}\n")
                f.write(f"Kaynak: {latest_image['url']}\n")
            
            self.status_var.set(f"Görsel ve kredi bilgileri kaydedildi: {filename}")
        except Exception as e:
            self.status_var.set(f"Kaydetme hatası: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TextToImageGenerator()
    app.run()