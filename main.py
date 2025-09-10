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
from PIL import Image, ImageTk  # Add this at the top if not already imported
import os
import subprocess
import sys



class WhatsAppMessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SendWise")
        self.root.geometry("1100x600")
        base_path = os.path.abspath(".")
        icon_path = os.path.abspath(os.path.join("assets", "logo1.ico"))
        print(icon_path)
        self.root.iconbitmap(icon_path)

        self.numbers = []
        self.raw_message = ""
        self.selected_image_path = None
        # Main horizontal layout
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar frame
        sidebar = tk.Frame(main_frame, bg="#075E54", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Inside your __init__ method where the sidebar is created
        logo_image = Image.open("assets\logo.png")
        logo_image = logo_image.resize((250, 200), Image.Resampling.LANCZOS)  # Resize as needed
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        tk.Label(sidebar, image=self.logo_photo, bg="#075E54").pack(pady=(20, 5))
        # Inside your WhatsAppMessengerApp __init__ method, in the sidebar creation section:
        tk.Button(sidebar, text="🌐 Create Shop Website", bg="#128C7E", fg="white",
                relief="flat", command=self.launch_website_dashboard).pack(pady=5, fill=tk.X, padx=10)

        # Feature buttons
        tk.Button(sidebar, text="📘 How to Use", bg="#128C7E", fg="white",
                relief="flat", command=self.show_how_to_use).pack(pady=5, fill=tk.X, padx=10)

        tk.Button(sidebar, text="📄 Terms & Conditions", bg="#128C7E", fg="white",
                relief="flat", command=self.show_terms).pack(pady=5, fill=tk.X, padx=10)

        tk.Button(sidebar, text="🛠️Troubleshoot / Contact Support", bg="#128C7E", fg="white",
                relief="flat", command=self.contact_support).pack(pady=5, fill=tk.X, padx=10)

        tk.Button(sidebar, text="📝 Feedback", bg="#128C7E", fg="white",
                relief="flat", command=self.give_feedback).pack(pady=5, fill=tk.X, padx=10)

        tk.Button(sidebar, text="⏱️ Reduce Time to Send", bg="#128C7E", fg="white",
                relief="flat", command=self.reduce_delay).pack(pady=5, fill=tk.X, padx=10)

        # Version and footer
        tk.Label(sidebar, text="v1.0.0", bg="#075E54", fg="white", font=("Arial", 10)).pack(side=tk.BOTTOM, pady=(0, 5))
        tk.Label(sidebar, text="By SendWise Technologies", bg="#075E54", fg="white", font=("Arial", 10)).pack(side=tk.BOTTOM, pady=(0, 10))



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
    def launch_website_dashboard(self):
        """
        Launch the website dashboard (dashboard.py) in a separate process.
        """
        try:
            python_executable = sys.executable  # Use the current Python interpreter
            dashboard_path = os.path.abspath(os.path.join("modules/Webseee", "dashboard.py"))  # Adjust path if needed

            if not os.path.exists(dashboard_path):
                self.log(f"❌ dashboard.py not found at {dashboard_path}")
                messagebox.showerror("Error", f"dashboard.py not found at:\n{dashboard_path}")
                return

            # Launch dashboard.py in a new process
            subprocess.Popen([python_executable, dashboard_path])
            self.log("🌐 Website Dashboard launched successfully!")
        except Exception as e:
            self.log(f"❌ Failed to launch Website Dashboard: {e}")
            messagebox.showerror("Error", f"Failed to launch Website Dashboard:\n{e}")

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
    def show_how_to_use(self):
        content = (
            "👋 Hey there! Here’s how to use the app:\n\n"
            "1️ First, add the phone numbers:\n"
            "   - You can type them manually.\n"
            "   - Or upload a .txt file (one number per line).\n"
            "   - Or upload a .csv file (make sure it has a column named 'number').\n"
            "   - Or upload WhatsApp group screenshots — we’ll pull out all the numbers for you using magic (a.k.a OCR 😉).\n\n"
            "📌 Make sure numbers have the country code but *don’t* use the + sign.\n"
            "   Example: 91xxxxxxxxxx\n\n"
            "2️ Now write your message:\n"
            "   - You can type it in directly.\n"
            "   - Or upload a text file with the message.\n"
            "   - If you uploaded a CSV, you can write personalized messages like:\n"
            "     ‘Hi {{name}}, your booking ID {{id}} is confirmed.’\n\n"
            "3️ (Optional) You can also attach an image — just hit the 'Select Image' button.\n\n"
            "4️ Hit 'Start Sending' when you’re ready. You can pause, resume, or stop anytime.\n\n"
            "📊 Progress and logs will show up at the bottom as it sends messages.\n\n"
            "⚠️ Just a heads-up:\n"
            "   - Use this tool responsibly. Sending bulk messages might lead to WhatsApp restrictions.\n"
            "   - Start small and see how it goes.\n\n"
            "💬 If you get stuck or need help, check the 'Troubleshoot / Contact Support' option.\n"
            "📢 And don’t forget to leave feedback. We’d love to hear from you!"
        )
        self.open_info_window("How to Use", content)




    def show_terms(self):
        content = (
            "📜 Terms & Conditions:\n\n"
            "By using this software, you agree to the following terms:\n\n"
            "✅ USAGE RESPONSIBILITY\n"
            "• You are solely responsible for the numbers and content you choose to send.\n"
            "• You must have prior consent or permission from the recipients to send them messages.\n"
            "• The app is designed for responsible use only. Any misuse is entirely the user's responsibility.\n\n"
            "🚫 PROHIBITED USAGE\n"
            "• Do not use this app for spamming, harassment, or spreading illegal, abusive, or misleading content.\n"
            "• Do not use this tool to impersonate others or conduct fraudulent activities.\n"
            "• Do not violate WhatsApp’s Terms of Service while using this tool.\n"
            "• Mass or unauthorized messaging can result in your WhatsApp number being restricted or banned.\n\n"
            "🔒 DATA & PRIVACY\n"
            "• This app does not collect, store, transmit, or share any of your personal data or recipient data.\n"
            "• All processing and actions are performed locally on your system.\n"
            "• We do not log or monitor any of your messages or activities.\n\n"
            "⚠️ DISCLAIMER\n"
            "• This tool is not affiliated with, endorsed by, or supported by WhatsApp or Meta Platforms, Inc.\n"
            "• We are not liable for any consequences (including bans, data loss, or legal issues) arising from your use of this app.\n"
            "• This software is provided 'as-is' without any warranties.\n"
            "• You use this software entirely at your own risk.\n\n"
            "💬 SUPPORT\n"
            "• We provide basic support for app-related issues (not WhatsApp-related ones).\n"
            "• Suggestions and feedback are welcome, but compliance and safe usage are your responsibility.\n\n"
            "By continuing to use this app, you confirm that you understand and agree to these terms."
        )
        self.open_info_window("Terms & Conditions", content)


    def contact_support(self):
        content = (
            "Troubleshooting & Support:\n\n"
            "• App not launching? Ensure Python dependencies are installed.\n"
            "• Image not sending? Check file type and size.\n"
            "• Still stuck?\n\n"
            "📧 Email: opensource703@gmail.com\n"
        )
        self.open_info_window("Troubleshoot / Contact Support", content)

    def give_feedback(self):
        content = (
            "We value your feedback!\n\n"
            "• What do you like?\n"
            "• What could be better?\n"
            "• Any bugs or feature suggestions?\n\n"
            "📧 Email us at: opensource703@gmail.com"
        )
        self.open_info_window("Feedback", content)


    def reduce_delay(self):
        content = (
            "Using WhatsApp API for Faster & Safer Messaging:\n\n"
            "This software uses WhatsApp Web for sending messages, which can be slower and may increase the risk of temporary bans if overused.\n\n"
            "If you want to:\n"
            "• Reduce the time between messages\n"
            "• Send messages more reliably and securely\n"
            "• Minimize the chances of being flagged or restricted by WhatsApp\n\n"
            "👉 We recommend using the official WhatsApp Business API.\n"
            "The API is designed for large-scale and compliant communication.\n\n"
            "📬 To explore this option or integrate API support into your setup, contact us at:\n"
            "**opensource703@gmail.com**\n\n"
            "We’ll help guide you through the process and see if it fits your needs!"
        )
        self.open_info_window("Reduce Time to Send (via API)", content)


    


    def open_info_window(self, title, content):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("400x400")
        window.configure(bg="white")

        tk.Label(window, text=title, font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 11), bg="white")
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)

        tk.Button(window, text="Close", command=window.destroy).pack(pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppMessengerApp(root)
    root.mainloop()
