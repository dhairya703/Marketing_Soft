import tkinter as tk
from tkinter import filedialog, scrolledtext

class NumberInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent.root)
        self.parent = parent
        self.numbers_path = tk.StringVar()
        self.numbers = []

        # Main horizontal layout frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, padx=10, pady=10)

        # LEFT SIDE: Input controls
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(left_frame, text="Numbers File:",font=("Arial", 16)).pack(anchor="w")
        tk.Entry(left_frame, textvariable=self.numbers_path, width=80).pack(pady=5, ipadx=10, ipady=10)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📁 Browse File", bg="#075E54", fg="white",
                  activebackground="#1DA851", relief="flat",
                  command=self.load_numbers_file).pack(side=tk.LEFT, padx=5,ipadx=8,ipady=8)

        tk.Button(btn_frame, text="✍️ Enter Manually", bg="#075E54", fg="white",
                  activebackground="#1DA851", relief="flat",
                  command=self.manual_number_input).pack(side=tk.LEFT, padx=5,ipadx=8,ipady=8)

        tk.Button(btn_frame, text="🖼️ Extract from Images", bg="#075E54", fg="white",
                  activebackground="#1DA851", relief="flat",
                  command=self.extract_numbers_from_images).pack(side=tk.LEFT, padx=5,ipadx=8,ipady=8)


        # In WhatsAppMessengerApp
    def update_number_display(self):
        self.number_list.delete("1.0", tk.END)
        for number in self.numbers:
            self.number_list.insert(tk.END, number + "\n")


    def load_numbers_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text or CSV Files", "*.txt;*.csv")])
        if path:
            self.numbers_path.set(path)
            self.numbers.clear()
            with open(path, "r") as f:
                for line in f:
                    cleaned = line.strip().replace(" ", "").replace("+", "")
                    if cleaned:
                        self.numbers.append(cleaned)
            self.parent.numbers = self.numbers
            self.update_number_display()
            self.parent.log(f"✅ Loaded {len(self.numbers)} numbers from file.")

    def manual_number_input(self):
        win = tk.Toplevel(self.parent.root)
        win.title("Enter Numbers")
        self.manual_numbers_text = scrolledtext.ScrolledText(win, width=60, height=15)
        self.manual_numbers_text.pack()
        tk.Button(win, text="Save Numbers", command=lambda: [self.save_manual_numbers(), win.destroy()]).pack(pady=5)

    def save_manual_numbers(self):
        self.numbers.clear()
        content = self.manual_numbers_text.get("1.0", tk.END).splitlines()
        for line in content:
            cleaned = line.strip().replace(" ", "").replace("+", "")
            if cleaned:
                self.numbers.append(cleaned)
        self.parent.numbers = self.numbers
        self.parent.update_number_display()
        self.parent.log(f"✅ Saved {len(self.numbers)} manually entered numbers.")


    def set_numbers(self, number_list):
        self.numbers = list(set(number_list))  # remove duplicates  
        self.parent.numbers = number_list
        self.parent.update_number_display()


    def extract_numbers_from_images(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        extractor = self.parent.ocr_extractor if hasattr(self.parent, 'ocr_extractor') else None
        if extractor is None:
            from modules.ocr_extractor import OCRExtractor
            extractor = OCRExtractor(self.parent)
        extractor.extract_numbers(folder)
