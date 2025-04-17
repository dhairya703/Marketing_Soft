import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
from modules.number_input import NumberInput
from modules.message_input import MessageInput
from modules.ocr_extractor import OCRExtractor
from modules.sender import WhatsAppSender
from tkinter import ttk
from modules.lifetime_tracker import load_lifetime_count, save_lifetime_count
from tkinter import filedialog



class WhatsAppMessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Bulk Messenger")
        self.root.geometry("1100x600")
        self.numbers = []
        self.raw_message = ""
        self.selected_image_path = None

        

        # Main horizontal layout
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar frame
        sidebar = tk.Frame(main_frame, bg="#075E54", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Logo
        tk.Label(sidebar, text="🚀", font=("Arial", 40), bg="#075E54", fg="white").pack(pady=20)
        tk.Label(sidebar, text="WAM Auto", font=("Arial", 14, "bold"), bg="#075E54", fg="white").pack()

        # Sidebar buttons
        tk.Button(sidebar, text="Create Group", bg="#128C7E", fg="white",
                  relief="flat", command=self.create_group).pack(pady=10, fill=tk.X, padx=10)
        tk.Button(sidebar, text="Save Contacts", bg="#128C7E", fg="white",
                  relief="flat", command=self.save_contacts).pack(pady=10, fill=tk.X, padx=10)
        tk.Button(sidebar, text="How to Use", bg="#128C7E", fg="white",
                  relief="flat", command=self.save_contacts).pack(pady=10, fill=tk.X, padx=10)

        # Version at bottom
        tk.Label(sidebar, text="v1.0.0", bg="#075E54", fg="white", font=("Arial", 10)).pack(side=tk.BOTTOM, pady=10)
        tk.Label(sidebar, text="By Cholle Kulche", bg="#075E54", fg="white", font=("Arial", 10)).pack(side=tk.BOTTOM, pady=10)


        # Main content frame
        content_frame = tk.Frame(main_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH,padx=40, expand=True)

        # Top-left: number and message input
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lifetime_sent = load_lifetime_count()
        self.lifetime_label = tk.Label(left_frame, text=f"📨 Lifetime Messages Sent: {self.lifetime_sent}", font=("Arial", 10, "bold"))
        self.lifetime_label.pack(anchor="ne", pady=(5, 0))

        self.number_input = NumberInput(self)
        self.number_input.pack(in_=left_frame, anchor="w")

        self.message_input = MessageInput(self)
        self.message_input.pack(in_=left_frame, anchor="w")
        tk.Label(left_frame, text="Attach Image:", font=("Arial", 16)).pack(anchor="w", padx=20, pady=(10, 0))

        tk.Button(left_frame, text="📷 Select Image",  bg="#075E54", fg="white", activebackground="#1DA851",
                relief="flat", font=("Arial", 12, ),command=self.select_image).pack(anchor="w",padx=20)

        # # Control buttons frame
        # control_frame = tk.Frame(left_frame)
        # control_frame.pack(pady=10)
        # tk.Button(left_frame, text="Start Sending", bg="#25D366", fg="white", activebackground="#1DA851",
        #           relief="flat", font=("Arial", 12, "bold"), command=self.start_sending).pack(pady=10, ipadx=10, ipady=10)
   # Control buttons frame
        # control_frame = tk.Frame(left_frame)
        # control_frame.pack(pady=10)

        # tk.Button(left_frame, text="Start Sending", bg="#25D366", fg="white", activebackground="#1DA851",
        #           relief="flat", font=("Arial", 12, "bold"), command=self.start_sending).pack(pady=10, ipadx=10, ipady=10)
        # tk.Button(control_frame, text="⏸️ Pause", command=self.pause_sending).pack(side=tk.LEFT, padx=5)
        # tk.Button(control_frame, text="▶️ Resume", command=self.resume_sending).pack(side=tk.LEFT, padx=5)
        # tk.Button(control_frame, text="⏹️ Stop", command=self.stop_sending).pack(side=tk.LEFT, padx=5)
        control_frame = tk.Frame(left_frame)
        control_frame.pack(pady=10)

        tk.Button(control_frame, text="Start Sending", bg="#25D366", fg="white", activebackground="#1DA851",
                relief="flat", font=("Arial", 12, "bold"), command=self.start_sending).pack(side=tk.LEFT, padx=5, ipadx=10, ipady=10)

        tk.Button(control_frame, text="⏸️ Pause", command=self.pause_sending).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="▶️ Resume", command=self.resume_sending).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="⏹️ Stop", command=self.stop_sending).pack(side=tk.LEFT, padx=5)



        # Progress bar

        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.ttk.Progressbar(left_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(5, 10),padx=10)
        

        self.log_area = scrolledtext.ScrolledText(left_frame, width=90, height=10)
        self.log_area.pack(fill=(tk.X),pady=10,padx=10)



        # # Right: number display
        # right_frame = tk.Frame(content_frame)
        # right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # tk.Label(right_frame, text="📋 Loaded Numbers:").pack(anchor="w")
        # self.number_list = scrolledtext.ScrolledText(right_frame, width=30, height=20, font=("Courier", 10))
        # self.number_list.pack(fill=tk.BOTH, expand=True)
        # Right: number display
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Display loaded numbers
        tk.Label(right_frame, text="📋 Loaded Numbers:").pack(anchor="w")
        self.number_list = scrolledtext.ScrolledText(right_frame, width=30, height=10, font=("Courier", 10))
        self.number_list.pack(fill=tk.BOTH, expand=True)
        tk.Label(right_frame, text="📜 Message to Send:").pack(anchor="w", pady=(10, 5))
        self.message_display = scrolledtext.ScrolledText(right_frame, width=30, height=10, font=("Courier", 10))
        self.message_display.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def update_number_display(self):
        self.number_list.delete("1.0", tk.END)
        for number in self.numbers:
            self.number_list.insert(tk.END, number + "\n")
    def update_message_display(self, message):
        self.message_display.delete("1.0", tk.END)
        self.message_display.insert(tk.END, message)
    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.selected_image_path = file_path
            self.log(f"🖼️ Selected image: {file_path}")
        else:
            self.selected_image_path = None
            self.log("❌ No image selected.")


    def extract_numbers_from_images(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        extractor = OCRExtractor(self)
        extractor.extract_numbers(folder)

    def start_sending(self):
        if not self.numbers:
            self.log("⚠️ No numbers to send messages to.")
            return

        message = getattr(self, 'raw_message', None)
        if not message:
            self.log("⚠️ No message to send.")
            return
        # Save sender instance for pause/resume to work
        self.sender = WhatsAppSender(self)
        self.sender.send_messages(self.numbers, message, self.selected_image_path)
        # sender = WhatsAppSender(self)
        # sender.send_messages(self.numbers, message)
    def pause_sending(self):
        if hasattr(self, 'sender'):
            self.sender.pause_sending()

    def resume_sending(self):
        if hasattr(self, 'sender'):
            self.sender.resume_sending()

    def stop_sending(self):
        if hasattr(self, 'sender'):
            self.sender.stop_sending()
    

    def create_group(self):
        self.log("🔧 Create group feature coming soon!")

    def save_contacts(self):
        self.log("💾 Save contacts feature coming soon!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppMessengerApp(root)
    root.mainloop()
