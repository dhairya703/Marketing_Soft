import tkinter as tk
from tkinter import filedialog, scrolledtext

class MessageInput(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent.root)
        self.parent = parent
        self.message_path = tk.StringVar()

        # Main horizontal layout frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, padx=10, pady=10)

        # LEFT SIDE: Input controls
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, anchor="n", padx=10)

        tk.Label(left_frame, text="Message File:", font=("Arial", 16)).pack(anchor="w")
        tk.Entry(left_frame, textvariable=self.message_path, width=80).pack(pady=5, ipadx=10, ipady=10)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📁 Browse File", bg="#075E54", fg="white",
                  activebackground="#1DA851", relief="flat",
                  command=self.load_message_file).pack(side=tk.LEFT, padx=5, ipadx=8, ipady=8)

        tk.Button(btn_frame, text="✍️ Write Manually", bg="#075E54", fg="white",
                  activebackground="#1DA851", relief="flat",
                  command=self.manual_message_input).pack(side=tk.LEFT, padx=5, ipadx=8, ipady=8)

        

    def load_message_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.message_path.set(path)
            with open(path, "r", encoding="utf8") as f:
                self.parent.raw_message = f.read()
            self.parent.update_message_display(self.parent.raw_message)
            self.parent.log("✅ Loaded message from file.")

    def manual_message_input(self):
        win = tk.Toplevel(self.parent.root)
        win.title("Write Message")
        self.manual_message_text = scrolledtext.ScrolledText(win, width=60, height=10)
        self.manual_message_text.pack()
        tk.Button(win, text="Save Message", command=lambda: [self.save_manual_message(), win.destroy()]).pack(pady=5)

    def save_manual_message(self):
        self.parent.raw_message = self.manual_message_text.get("1.0", tk.END).strip()
        self.parent.update_message_display(self.parent.raw_message)
        self.parent.log("✅ Message saved.")
