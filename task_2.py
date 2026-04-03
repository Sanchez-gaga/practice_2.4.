import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import time

CAT_API_URL = "https://api.thecatapi.com/v1/images/search?limit=1"
CAT_FALLBACK_URL = "https://aws.random.cat/meow"   
DOG_API_URL = "https://dog.ceo/api/breeds/image/random"

class PetPhotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Случайные фото котов и собак")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        title_label = tk.Label(root, text="Генератор случайных фото", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.cat_btn = tk.Button(btn_frame, text="🐱 Получить кота", font=("Arial", 12),
                                 command=self.get_cat, width=20)
        self.cat_btn.pack(side=tk.LEFT, padx=10)

        self.dog_btn = tk.Button(btn_frame, text="🐶 Получить собаку", font=("Arial", 12),
                                 command=self.get_dog, width=20)
        self.dog_btn.pack(side=tk.LEFT, padx=10)

        self.image_label = tk.Label(root, bg="white", relief=tk.SUNKEN, width=500, height=500)
        self.image_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(root, text="Нажмите кнопку для получения фото", bd=1,
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.current_photo = None

    def get_cat(self):
        self._disable_buttons()
        self.status_label.config(text="Загрузка кота...")
        threading.Thread(target=self._fetch_cat, daemon=True).start()

    def get_dog(self):
        self._disable_buttons()
        self.status_label.config(text="Загрузка собаки...")
        threading.Thread(target=self._fetch_dog, daemon=True).start()

    def _fetch_cat(self):
        try:
            response = requests.get(CAT_API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and "url" in data[0]:
                    image_url = data[0]["url"]
                    self._load_image(image_url, "Кот")
                    return
            self._fetch_cat_fallback()
        except Exception:
            self._fetch_cat_fallback()

    def _fetch_cat_fallback(self):
        try:
            response = requests.get(CAT_FALLBACK_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "file" in data:
                    image_url = data["file"]
                    self._load_image(image_url, "Кот")
                    return
            self._show_error("Не удалось получить ссылку на фото кота (оба API недоступны)")
        except Exception as e:
            self._show_error(f"Ошибка при получении ссылки на кота: {e}")

    def _fetch_dog(self):
        try:
            response = requests.get(DOG_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success" and "message" in data:
                image_url = data["message"]
                self._load_image(image_url, "Собака")
            else:
                self._show_error("Не удалось получить ссылку на фото собаки")
        except Exception as e:
            self._show_error(f"Ошибка при получении ссылки: {e}")

    def _load_image(self, url, animal_type, retries=2):
        for attempt in range(retries + 1):
            try:
                img_response = requests.get(url, timeout=20)
                img_response.raise_for_status()
                img_data = Image.open(BytesIO(img_response.content))
                img_data.thumbnail((500, 500), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_data)
                self.root.after(0, self._update_image, photo, animal_type)
                return
            except requests.exceptions.Timeout:
                if attempt < retries:
                    time.sleep(1)
                    continue
                else:
                    self._show_error(f"Таймаут загрузки изображения {animal_type}. Повторите попытку позже.")
            except Exception as e:
                self._show_error(f"Ошибка загрузки изображения: {e}")
                return

    def _update_image(self, photo, animal_type):
        self.image_label.config(image=photo)
        self.current_photo = photo
        self.status_label.config(text=f"{animal_type} загружен")
        self._enable_buttons()

    def _show_error(self, message):
        self.root.after(0, lambda: messagebox.showerror("Ошибка", message))
        self.root.after(0, self._enable_buttons)
        self.root.after(0, lambda: self.status_label.config(text="Ошибка загрузки"))

    def _disable_buttons(self):
        self.cat_btn.config(state=tk.DISABLED)
        self.dog_btn.config(state=tk.DISABLED)

    def _enable_buttons(self):
        self.cat_btn.config(state=tk.NORMAL)
        self.dog_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PetPhotoApp(root)
    root.mainloop()