from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from datetime import datetime
import pyautogui
import threading
import time
import random

# class WhatsAppSender:
#     def __init__(self, parent):
#         self.parent = parent

#     def send_messages(self, numbers, message):
#         thread = threading.Thread(target=self._run, args=(numbers, message))
#         thread.start()

#     def _run(self, numbers, message):
#         try:
#             timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             final_message = f"{message}\n\nSent at: {timestamp}"
#             encoded_message = quote(final_message)

#             options = Options()
#             options.add_argument("--user-data-dir=D:/ChromeUserData")
#             options.add_argument("--profile-directory=Default")
#             options.add_experimental_option("excludeSwitches", ["enable-logging"])
#             service = Service("D:/mission/whatsapp-bulk-messenger/chromedriver-win64/chromedriver.exe")
#             driver = webdriver.Chrome(service=service, options=options)
#             driver.minimize_window()


#             wait = WebDriverWait(driver, 20)

#             for i, number in enumerate(numbers):
#                 self.parent.log(f"{i+1}/{len(numbers)} → Sending to {number}")
#                 url = f"https://api.whatsapp.com/send?phone={number}&text={encoded_message}"
#                 driver.get(url)

#                 try:
#                     continue_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Continue to Chat")))
#                     continue_btn.click()
#                     time.sleep(4)
#                     pyautogui.press("enter")
#                     self.parent.log(f"✅ Message sent to {number}")
#                     progress = ((i + 1) / len(numbers)) * 100
#                     self.parent.progress_var.set(progress)

#                 except Exception as e:
#                     self.parent.log(f"❌ Failed for {number}: {e}")

#                 time.sleep(random.uniform(3, 8))

#             self.parent.log("✅ All messages sent.")

#         except Exception as e:
#             self.parent.log(f"🚨 Error: {e}")
# class WhatsAppSender:
#     def __init__(self, parent):
#         self.parent = parent
#         self.paused = False
#         self.stopped = False
#         self.current_index = 0

#     def send_messages(self, numbers, message):
#         self.paused = False
#         self.stopped = False
#         thread = threading.Thread(target=self._run, args=(numbers, message))
#         thread.start()

#     def pause_sending(self):
#         self.paused = True
#         self.parent.log("⏸️ Paused sending...")

#     def resume_sending(self):
#         self.paused = False
#         self.parent.log("▶️ Resumed sending...")

#     def stop_sending(self):
#         self.stopped = True
#         self.parent.log("⏹️ Stopped sending.")

#     def _run(self, numbers, message):
#         try:
#             timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             final_message = f"{message}\n\nSent at: {timestamp}"
#             encoded_message = quote(final_message)

#             options = Options()
#             options.add_argument("--user-data-dir=D:/ChromeUserData")
#             options.add_argument("--profile-directory=Default")
#             options.add_experimental_option("excludeSwitches", ["enable-logging"])
#             service = Service("D:/mission/whatsapp-bulk-messenger/chromedriver-win64/chromedriver.exe")
#             driver = webdriver.Chrome(service=service, options=options)
#             wait = WebDriverWait(driver, 20)

#             for i in range(self.current_index, len(numbers)):
#                 if self.stopped:
#                     break

#                 while self.paused:
#                     time.sleep(1)

#                 number = numbers[i]
#                 self.current_index = i  # Save progress

#                 self.parent.log(f"{i+1}/{len(numbers)} → Sending to {number}")
#                 url = f"https://api.whatsapp.com/send?phone={number}&text={encoded_message}"
#                 driver.get(url)

#                 try:
#                     continue_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Continue to Chat")))
#                     continue_btn.click()
#                     time.sleep(4)
#                     pyautogui.press("enter")
#                     self.parent.log(f"✅ Message sent to {number}")
#                     progress = ((i + 1) / len(numbers)) * 100
#                     self.parent.progress_var.set(progress)
#                 except Exception as e:
#                     self.parent.log(f"❌ Failed for {number}: {e}")

#                 time.sleep(random.uniform(3, 8))

#             self.parent.log("✅ All messages sent or stopped.")

#         except Exception as e:
#             self.parent.log(f"🚨 Error: {e}")
import threading
import time
import random
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pyautogui

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


    def send_messages(self, numbers, message):
        self.stop_event.clear()
        self.pause_event.set()
        self.start_time = time.time()
        self.total_sent = 0
        self.total_duration = 0
        thread = threading.Thread(target=self._run, args=(numbers, message))
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

    def _run(self, numbers, message):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            final_message = f"{message}\n\nSent at: {timestamp}"
            encoded_message = quote(final_message)

            options = Options()
            options.add_argument("--user-data-dir=D:/ChromeUserData")
            options.add_argument("--profile-directory=Default")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            service = Service("D:/mission/whatsapp-bulk-messenger/chromedriver-win64/chromedriver.exe")
            driver = webdriver.Chrome(service=service, options=options)
            wait = WebDriverWait(driver, 20)

            total = len(numbers)
            for i in range(self.current_index, total):
                if self.stop_event.is_set():
                    break

                self.pause_event.wait()  # This waits if paused, continues when resumed

                number = numbers[i]
                self.current_index = i

                self.parent.log(f"{i+1}/{total} → Sending to {number}")
                url = f"https://api.whatsapp.com/send?phone={number}&text={encoded_message}"
                driver.get(url)

                try:
                    continue_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Continue to Chat")))
                    continue_btn.click()
                    time.sleep(4)
                    start_msg_time = time.time()
                    pyautogui.press("enter")
                    end_msg_time = time.time()
                    duration = end_msg_time - start_msg_time
                    self.total_sent += 1
                    self.total_duration += duration

                    avg_time = self.total_duration / self.total_sent if self.total_sent else 0
                    self.parent.log(f"✅ Sent to {number} in {duration:.2f}s | Avg: {avg_time:.2f}s")
                    # self.parent.log(f"✅ Message sent to {number}")
                except Exception as e:
                    self.parent.log(f"❌ Failed for {number}: {e}")

                progress = ((i + 1) / total) * 100
                self.parent.progress_var.set(progress)

                time.sleep(random.uniform(3, 8))

            self.parent.log("✅ All messages sent or stopped.")
        except Exception as e:
            self.parent.log(f"🚨 Error: {e}")
