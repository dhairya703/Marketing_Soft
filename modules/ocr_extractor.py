# import os
# import cv2
# import pytesseract
# import re

# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# class OCRExtractor:
#     def __init__(self, parent):
#         self.parent = parent

#     def extract_numbers(self, folder):
#         numbers = []
#         for filename in os.listdir(folder):
#             if filename.lower().endswith((".png", ".jpg", ".jpeg")):
#                 path = os.path.join(folder, filename)
#                 image = cv2.imread(path)
#                 gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#                 text = pytesseract.image_to_string(gray)
#                 pattern = r'\+\d{1,3}[\s\-]?\d{5}[\s\-]?\d{5}'
#                 matches = re.findall(pattern, text)
#                 cleaned = [re.sub(r'[+\s\-]', '', number) for number in matches]
#                 numbers.extend(cleaned)

#         numbers = list(set(numbers))
#         self.parent.numbers = numbers
#         self.parent.number_input.set_numbers(numbers)

#         self.parent.log(f"🔍 Extracted {len(numbers)} unique numbers from images.")
import os
import sys
import cv2
import pytesseract
import re

class OCRExtractor:
    def __init__(self, parent):
        self.parent = parent

    def extract_numbers(self, folder):
        # Determine the base path
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Set the path to tesseract.exe
        tesseract_path = os.path.join(base_path, 'Tesseract-OCR', 'tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        numbers = []
        for filename in os.listdir(folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(folder, filename)
                image = cv2.imread(path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)
                pattern = r'\+\d{1,3}[\s\-]?\d{5}[\s\-]?\d{5}'
                matches = re.findall(pattern, text)
                cleaned = [re.sub(r'[+\s\-]', '', number) for number in matches]
                numbers.extend(cleaned)

        numbers = list(set(numbers))
        self.parent.numbers = numbers
        self.parent.number_input.set_numbers(numbers)

        self.parent.log(f"🔍 Extracted {len(numbers)} unique numbers from images.")
