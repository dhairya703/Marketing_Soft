from urllib.parse import quote
import threading
import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pyautogui
import win32clipboard
from PIL import Image
import io
from string import Template
from modules.lifetime_tracker import load_lifetime_count, save_lifetime_count
import os

import pyautogui
# ⬇️ Add this outside any class
def copy_image_to_clipboard(image_path):
    image = Image.open(image_path)
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # skip BMP header
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

class WhatsAppSender:
    def __init__(self, parent):
        self.parent = parent
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()  # Not paused initially
        self.current_index = 0
        self.start_time = None
        self.total_sent = 0
        self.total_duration = 0


    def send_messages(self, numbers, message, image_path=None):
        self.stop_event.clear()
        self.pause_event.set()
        self.start_time = time.time()
        self.total_sent = 0
        self.total_duration = 0
        thread = threading.Thread(target=self._run, args=(numbers, message, image_path))
        thread.start()

    def pause_sending(self):
        self.pause_event.clear()
        self.parent.log("⏸️ Paused sending...")

    def resume_sending(self):
        self.pause_event.set()
        self.parent.log("▶️ Resumed sending...")

    def stop_sending(self):
        self.stop_event.set()
        self.pause_event.set()  # In case it's paused
        self.parent.log("⏹️ Stopped sending.")
    def render_message(self, template, data):
        try:
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                template = template.replace(placeholder, str(value))
            return template
        except Exception as e:
            self.parent.log(f"⚠️ Placeholder error: {e}")
            return template  # fallback




    def _run(self, numbers, message,image_path):
        try:


            options = Options()
            options.add_argument("--user-data-dir=D:/ChromeUserData")
            options.add_argument("--profile-directory=Default")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            # service = Service("D:/mission/whatsapp-bulk-messenger/chromedriver-win64/chromedriver.exe")
            # driver = webdriver.Chrome(service=service, options=options)
            # wait = WebDriverWait(driver, 20)
                    # Dynamically construct the path to chromedriver.exe
            base_dir = os.path.dirname(os.path.abspath(__file__))
            driver_path = os.path.join(base_dir, 'driver', 'chromedriver.exe')
            service = Service(driver_path)

            # Initialize the WebDriver
            driver = webdriver.Chrome(service=service, options=options)
            wait = WebDriverWait(driver, 20)

            total = len(numbers)
            for i in range(self.current_index, total):
                if self.stop_event.is_set():
                    break

                self.pause_event.wait() 
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                recipient = numbers[i]
                self.current_index = i

                if isinstance(recipient, dict):
                    number = recipient.get("number")
                    if not number:
                        self.parent.log(f"⚠️ Missing 'number' in row {i+1}, skipping...")
                        continue
                    rendered = self.render_message(message, recipient)
                else:
                    number = recipient
                    rendered = message

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                final_message = f"{rendered}\n\nSent at: {timestamp}"

                # final_message = f"{message}\n\nSent at: {timestamp}"
                encoded_message = quote(final_message) # This waits if paused, continues when resumed

                # number = numbers[i]
                # self.current_index = i


                self.parent.log(f"{i+1}/{total} → Sending to {number}")
                url = f"https://api.whatsapp.com/send?phone={number}&text={encoded_message}"
                driver.get(url)

                try:
                    continue_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Continue to Chat")))
                    continue_btn.click()
                    time.sleep(3)
               
                    if image_path:
                        try:
                            # Copy image to clipboard
                            copy_image_to_clipboard(image_path)
                            # Wait for chat to be ready (you can also check for message box element)
                            time.sleep(2)
                            # Paste and send
                            pyautogui.hotkey("ctrl", "v")
                            time.sleep(3)
                            # pyautogui.press("enter")
                            # time.sleep(2)
                        except Exception as e:
                            self.parent.log(f"❌ Image upload failed for {number}: {e}")

                    start_msg_time = time.time()
                    pyautogui.press("enter")
                    end_msg_time = time.time()
                    duration = end_msg_time - start_msg_time
                    self.total_sent += 1
                    self.total_duration += duration

                    avg_time = self.total_duration / self.total_sent if self.total_sent else 0
                    self.parent.log(f"✅ Sent to {number} in {duration:.2f}s")
                    self.total_sent += 1
                    self.total_duration += duration


                    # Lifetime update
                    self.parent.lifetime_sent += 1
                    save_lifetime_count(self.parent.lifetime_sent)
                    self.parent.lifetime_label.config(text=f"📨 Lifetime Messages Sent: {self.parent.lifetime_sent}")

                    # self.parent.log(f"✅ Message sent to {number}")
                except Exception as e:
                    self.parent.log(f"❌ Failed for {number}: {e}")

                progress = ((i + 1) / total) * 100
                self.parent.progress_var.set(progress)

                time.sleep(random.uniform(3, 8))

            self.parent.log("✅ All messages sent or stopped.")
        except Exception as e:
            self.parent.log(f"🚨 Error: {e}")
