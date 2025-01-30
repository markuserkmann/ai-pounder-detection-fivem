from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import tkinter as tk
import keyboard
import pyautogui
from datetime import datetime
import os
import random
import string
import sys
import requests
import cv2

with open("labels.txt", "r") as f:
    class_names = f.readlines()

class Reader:
    def __init__(self):
        self.save_directory = "screenshots"
        os.makedirs(self.save_directory, exist_ok=True)
        
        self.root = tk.Tk()
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        self.window_width = 750
        self.window_height = 350
        self.border_thickness = 3
        
        self.x = (self.screen_width - self.window_width) // 2
        self.y = (self.screen_height - self.window_height) // 2
        
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        self.root.attributes('-transparentcolor', 'white')
        
        self.canvas = tk.Canvas(
            self.root,
            width=self.window_width,
            height=self.window_height,
            highlightthickness=0,
            bg='white'
        )
        self.canvas.pack(fill='both', expand=True)
        
        self.draw_border()
        
        keyboard.on_press_key('j', self.take_screenshot)
        keyboard.on_press_key('u', self.exit_program)

        self.root.mainloop()

    def exit_program(self, event=None):
        self.root.quit()
        sys.exit()
    
    def draw_border(self):
        self.canvas.create_rectangle(
            0, 0, self.window_width, self.border_thickness,
            fill='blue', outline='blue'
        )
        self.canvas.create_rectangle(
            0, self.window_height - self.border_thickness, self.window_width, self.window_height,
            fill='blue', outline='blue'
        )
        self.canvas.create_rectangle(
            0, 0, self.border_thickness, self.window_height,
            fill='blue', outline='blue'
        )
        self.canvas.create_rectangle(
            self.window_width - self.border_thickness, 0, self.window_width, self.window_height,
            fill='blue', outline='blue'
        )

    def send_image_to_discord(self, image_path, webhook_url, message=""):
        with open(image_path, 'rb') as image_file:
            files = {
                'file': (image_path, image_file, 'image/jpeg')
            }
            data = {
                'content': message
            }
            requests.post(webhook_url, data=data, files=files)

    def generate_random_name(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"screenshot_{timestamp}_{random_chars}.png"
    
    def take_screenshot(self, event):
        try:
            screenshot = pyautogui.screenshot(region=(self.x, self.y, self.window_width, self.window_height))
            image_array = np.array(screenshot)

            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

            image_resized = cv2.resize(image_array, (224, 224))
            normalized_image_array = (image_resized.astype(np.float32) / 127.5) - 1
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            data[0] = normalized_image_array

            prediction = model.predict(data)
            index = np.argmax(prediction)
            class_name = class_names[index].strip()
            confidence_score = prediction[0][index]

            print(f"Class: {class_name}, Confidence Score: {confidence_score}")

            if class_name == "0 Pounder":
                startX, startY, endX, endY = 50, 50, self.window_width - 50, self.window_height - 50
                cv2.rectangle(image_array, (startX, startY), (endX, endY), (0, 255, 0), 4)
                cv2.putText(image_array, f"{class_name} ({confidence_score:.2f})", (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                image_path = os.path.join(self.save_directory, self.generate_random_name())
                cv2.imwrite(image_path, image_array)

                webhook_url = "YOURWEBHOOKURL"
                self.send_image_to_discord(image_path, webhook_url, message="Found a pounder!")

        except Exception as e:
            print(f"Error taking screenshot: {e}")

if __name__ == "__main__":
    window = Reader()
