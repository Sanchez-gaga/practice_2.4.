import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO

API_KEY =  
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Погода")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        self.city_label = tk.Label(root, text="Город:", font=("Arial", 12))
        self.city_label.pack(pady=10)

        self.city_entry = tk.Entry(root, font=("Arial", 12), width=25)
        self.city_entry.pack(pady=5)

        self.get_weather_btn = tk.Button(
            root, text="Узнать погоду", command=self.get_weather, font=("Arial", 12)
        )
        self.get_weather_btn.pack(pady=10)

        self.info_frame = tk.Frame(root, bg="white")
        self.info_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.icon_label = tk.Label(self.info_frame, bg="white")
        self.icon_label.pack(pady=10)

        self.temp_label = tk.Label(
            self.info_frame, text="", font=("Arial", 24), bg="white"
        )
        self.temp_label.pack()

        self.desc_label = tk.Label(
            self.info_frame, text="", font=("Arial", 14), bg="white"
        )
        self.desc_label.pack()

        self.city_name_label = tk.Label(
            self.info_frame, text="", font=("Arial", 16, "bold"), bg="white"
        )
        self.city_name_label.pack(pady=5)

        self.status_label = tk.Label(
            root, text="Введите город и нажмите кнопку", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Ошибка", "Введите название города")
            return

        self.status_label.config(text="Загрузка...")
        self.root.update()

        try:
            
            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric",  
                "lang": "ru"        
            }
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if response.status_code != 200:
                error_msg = data.get("message", "Ошибка запроса")
                messagebox.showerror("Ошибка", f"Не удалось получить данные: {error_msg}")
                self.status_label.config(text="Готов")
                return

            
            city_name = data["name"]
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            icon_code = data["weather"][0]["icon"]

            
            self.city_name_label.config(text=city_name)
            self.temp_label.config(text=f"{temp:.1f}°C")
            self.desc_label.config(text=description.capitalize())

            
            self.load_icon(icon_code)

            self.status_label.config(text=f"Обновлено для города {city_name}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось соединиться с сервером: {e}")
            self.status_label.config(text="Ошибка соединения")
        except KeyError as e:
            messagebox.showerror("Ошибка данных", "Неожиданный ответ от сервера")
            self.status_label.config(text="Ошибка")

    def load_icon(self, icon_code):
        
        try:
            url = ICON_URL.format(icon=icon_code)
            response = requests.get(url, timeout=5)
            img_data = Image.open(BytesIO(response.content))
            img = img_data.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            self.icon_label.config(image=photo)
            self.icon_label.image = photo  
        except Exception as e:
            print(f"Ошибка загрузки иконки: {e}")
            self.icon_label.config(image="", text="[иконка не загружена]")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()