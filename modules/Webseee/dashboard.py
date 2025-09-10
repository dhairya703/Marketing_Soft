
# from tkinter import messagebox
# import json
# import os
# import deploy  # Make sure deploy.py is in the same folder

# # File paths
# DATA_FILE = 'data.json'
# TEMPLATE_FILE = 'template.html'
# OUTPUT_FILE = 'index.html'

# # Default data
# default_data = {
#     "shop_name": "Chic & Unique",
#     "about_text": "Welcome to our store! Discover unique, high-quality products curated just for you.",
#     "contact_email": "info@chicshop.com",
#     "products": [
#         {"name": "Sample Product 1", "price": "29.99", "image": "https://placehold.co/200x200"},
#         {"name": "Sample Product 2", "price": "49.99", "image": "https://placehold.co/200x200"}
#     ]
# }

# # Load or create JSON data
# def load_data():
#     if not os.path.exists(DATA_FILE):
#         with open(DATA_FILE, 'w', encoding='utf-8') as f:
#             json.dump(default_data, f, indent=4, ensure_ascii=False)
#     with open(DATA_FILE, encoding='utf-8') as f:
#         return json.load(f)

# def save_data(data):
#     with open(DATA_FILE, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4, ensure_ascii=False)

# # Generate website HTML
# def generate_website(data):
#     if not os.path.exists(TEMPLATE_FILE):
#         messagebox.showerror("Error", f"Template file '{TEMPLATE_FILE}' not found!")
#         return

#     with open(TEMPLATE_FILE, encoding='utf-8') as f:
#         template = f.read()

#     product_cards = ""
#     for product in data['products']:
#         card = f"""
#         <div class="product-card bg-white rounded-xl shadow-lg overflow-hidden flex flex-col transition-all duration-300 hover:shadow-2xl hover:-translate-y-2">
#             <img src="{product['image']}" alt="{product['name']}" class="w-full h-64 object-cover">
#             <div class="p-5 text-center flex-grow flex flex-col">
#                 <h3 class="text-lg font-semibold text-gray-800">{product['name']}</h3>
#                 <p class="text-indigo-600 font-bold mt-2">Rs {product['price']}</p>
#             </div>
#         </div>
#         """
#         product_cards += card

#     html = template.replace("{{shop_name}}", data['shop_name'])\
#                 .replace("{{about_text}}", data['about_text'])\
#                 .replace("{{contact_email}}", data['contact_email'])\
#                 .replace("{{product_cards}}", product_cards)\
#                 .replace("{{hero_image}}", data.get('hero_image', 'https://placehold.co/1600x900'))\
#                 .replace("{{about_image}}", data.get('about_image', 'https://placehold.co/600x400'))

#     with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
#         f.write(html)

#     messagebox.showinfo("Success", "Website generated successfully!")

# # Tkinter Dashboard
# class ShopDashboard(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Shop Website Dashboard")
#         self.geometry('950x750')

#         self.data = load_data()
#         self.product_widgets = []  # Separate list for Entry widgets

#         # Deployment URL variable
#         self.deploy_url_var = tk.StringVar()

#         self.create_widgets()

#     def create_widgets(self):
#         # Shop info
#         tk.Label(self, text="Shop Name").pack()
#         self.shop_name = tk.Entry(self, width=80)
#         self.shop_name.insert(0, self.data['shop_name'])
#         self.shop_name.pack()

#         tk.Label(self, text="About Text").pack()
#         self.about_text = tk.Text(self, width=80, height=4)
#         self.about_text.insert('1.0', self.data['about_text'])
#         self.about_text.pack()

#         tk.Label(self, text="Contact Email").pack()
#         self.contact_email = tk.Entry(self, width=80)
#         self.contact_email.insert(0, self.data['contact_email'])
#         self.contact_email.pack()

#         tk.Label(self, text="Hero Image URL").pack()
#         self.hero_image = tk.Entry(self, width=80)
#         self.hero_image.insert(0, self.data.get('hero_image', ''))
#         self.hero_image.pack()

#         tk.Label(self, text="About Image URL").pack()
#         self.about_image = tk.Entry(self, width=80)
#         self.about_image.insert(0, self.data.get('about_image', ''))
#         self.about_image.pack()

#         # Products frame
#         self.products_frame = tk.Frame(self)
#         self.products_frame.pack(pady=10)
#         self.render_products()

#         tk.Button(self, text="Add New Product", command=self.add_product).pack(pady=5)
#         tk.Button(self, text="Generate & Deploy Website", bg="green", fg="white", command=self.save_generate_and_deploy).pack(pady=10)

#         # Deployment URL display
#         tk.Label(self, text="Live Site URL:").pack(pady=(10,0))
#         self.deploy_url_entry = tk.Entry(self, textvariable=self.deploy_url_var, width=80, state='readonly')
#         self.deploy_url_entry.pack()
#         tk.Button(self, text="Copy URL", command=self.copy_url_to_clipboard).pack(pady=5)

#     def render_products(self):
#         # Clear previous widgets
#         for widget in self.products_frame.winfo_children():
#             widget.destroy()
#         self.product_widgets.clear()

#         for i, prod in enumerate(self.data['products']):
#             frame = tk.Frame(self.products_frame, relief=tk.RIDGE, borderwidth=1, padx=5, pady=5)
#             frame.pack(pady=5, fill=tk.X)

#             tk.Label(frame, text=f"Product {i+1}").grid(row=0, column=0, padx=5)

#             name_entry = tk.Entry(frame, width=30)
#             name_entry.insert(0, prod['name'])
#             name_entry.grid(row=0, column=1, padx=5)

#             price_entry = tk.Entry(frame, width=10)
#             price_entry.insert(0, prod['price'])
#             price_entry.grid(row=0, column=2, padx=5)

#             image_entry = tk.Entry(frame, width=50)
#             image_entry.insert(0, prod['image'])
#             image_entry.grid(row=0, column=3, padx=5)

#             remove_btn = tk.Button(frame, text="Remove", fg="red", command=lambda idx=i: self.remove_product(idx))
#             remove_btn.grid(row=0, column=4, padx=5)

#             self.product_widgets.append({
#                 'name': name_entry,
#                 'price': price_entry,
#                 'image': image_entry
#             })

#     def add_product(self):
#         self.data['products'].append({"name": "", "price": "", "image": ""})
#         self.render_products()

#     def remove_product(self, index):
#         self.data['products'].pop(index)
#         self.render_products()

#     def copy_url_to_clipboard(self):
#         url = self.deploy_url_var.get()
#         if url:
#             self.clipboard_clear()
#             self.clipboard_append(url)
#             messagebox.showinfo("Copied", "URL copied to clipboard!")
#         else:
#             messagebox.showwarning("No URL", "No deployment URL available yet.")

#     def save_generate_and_deploy(self):
#         # Update shop info
#         self.data['shop_name'] = self.shop_name.get()
#         self.data['about_text'] = self.about_text.get('1.0', 'end').strip()
#         self.data['contact_email'] = self.contact_email.get()
#         self.data['hero_image'] = self.hero_image.get()
#         self.data['about_image'] = self.about_image.get()

#         # Update products from Entry widgets
#         for i, prod in enumerate(self.data['products']):
#             widgets = self.product_widgets[i]
#             prod['name'] = widgets['name'].get()
#             prod['price'] = widgets['price'].get()
#             prod['image'] = widgets['image'].get()

#         # Save JSON and generate website
#         save_data(self.data)
#         generate_website(self.data)

#         # --- Automatic deployment ---
#         NETLIFY_SITE_ID = "8d8f0d99-8ff9-40ce-8228-4122625b85c9"
#         NETLIFY_TOKEN = "nfp_7xKvfnUUB7WktQ9BCL5MmVRa277CXxyd8e27"

#         deploy_data = deploy.deploy_to_netlify(NETLIFY_SITE_ID, NETLIFY_TOKEN, OUTPUT_FILE)

#         # Update deployment URL in dashboard
#         if deploy_data and "deploy_ssl_url" in deploy_data:
#             self.deploy_url_var.set(deploy_data["deploy_ssl_url"])

# # Run dashboard
# if __name__ == '__main__':
#     app = ShopDashboard()
#     app.mainloop()
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import deploy  # Make sure deploy.py is in the same folder

# File paths
DATA_FILE = 'data.json'
TEMPLATE_FILE = 'template.html'
OUTPUT_FILE = 'index.html'

# Default data
default_data = {
    "shop_name": "Chic & Unique",
    "about_text": "Welcome to our store! Discover unique, high-quality products curated just for you.",
    "contact_email": "info@chicshop.com",
    "products": [
        {"name": "Sample Product 1", "price": "29.99", "image": "https://placehold.co/200x200"},
        {"name": "Sample Product 2", "price": "49.99", "image": "https://placehold.co/200x200"}
    ]
}

# Load or create JSON data
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
    with open(DATA_FILE, encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Generate website HTML
def generate_website(data):
    if not os.path.exists(TEMPLATE_FILE):
        messagebox.showerror("Error", f"Template file '{TEMPLATE_FILE}' not found!")
        return

    with open(TEMPLATE_FILE, encoding='utf-8') as f:
        template = f.read()

    product_cards = ""
    for product in data['products']:
        card = f"""
        <div class="product-card bg-white rounded-xl shadow-lg overflow-hidden flex flex-col transition-all duration-300 hover:shadow-2xl hover:-translate-y-2">
            <img src="{product['image']}" alt="{product['name']}" class="w-full h-64 object-cover">
            <div class="p-5 text-center flex-grow flex flex-col">
                <h3 class="text-lg font-semibold text-gray-800">{product['name']}</h3>
                <p class="text-indigo-600 font-bold mt-2">Rs {product['price']}</p>
            </div>
        </div>
        """
        product_cards += card

    html = template.replace("{{shop_name}}", data['shop_name'])\
                .replace("{{about_text}}", data['about_text'])\
                .replace("{{contact_email}}", data['contact_email'])\
                .replace("{{product_cards}}", product_cards)\
                .replace("{{hero_image}}", data.get('hero_image', 'https://placehold.co/1600x900'))\
                .replace("{{about_image}}", data.get('about_image', 'https://placehold.co/600x400'))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    messagebox.showinfo("Success", "Website generated successfully!")

# Tkinter Dashboard
class ShopDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Create your Own Website")
        self.geometry('1000x800')

        self.data = load_data()
        self.product_widgets = []

        # Deployment URL variable
        self.deploy_url_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Shop info
        tk.Label(self, text="Shop Name").pack()
        self.shop_name = tk.Entry(self, width=80)
        self.shop_name.insert(0, self.data['shop_name'])
        self.shop_name.pack()

        tk.Label(self, text="About Text").pack()
        self.about_text = tk.Text(self, width=80, height=4)
        self.about_text.insert('1.0', self.data['about_text'])
        self.about_text.pack()

        tk.Label(self, text="Contact Email").pack()
        self.contact_email = tk.Entry(self, width=80)
        self.contact_email.insert(0, self.data['contact_email'])
        self.contact_email.pack()

        tk.Label(self, text="Hero Image URL").pack()
        self.hero_image = tk.Entry(self, width=80)
        self.hero_image.insert(0, self.data.get('hero_image', ''))
        self.hero_image.pack()

        tk.Label(self, text="About Image URL").pack()
        self.about_image = tk.Entry(self, width=80)
        self.about_image.insert(0, self.data.get('about_image', ''))
        self.about_image.pack()

        # Products frame
        self.products_frame = tk.Frame(self)
        self.products_frame.pack(pady=10)
        self.render_products()

        tk.Button(self, text="Add New Product", command=self.add_product).pack(pady=5)
        tk.Button(self, text="Generate & Deploy Website", bg="green", fg="white", command=self.save_generate_and_deploy).pack(pady=10)

        # Deployment URL display
        tk.Label(self, text="Live Site URL:").pack(pady=(10,0))
        self.deploy_url_entry = tk.Entry(self, textvariable=self.deploy_url_var, width=80, state='readonly')
        self.deploy_url_entry.pack()
        tk.Button(self, text="Copy URL", command=self.copy_url_to_clipboard).pack(pady=5)

        # Deployment log
        tk.Label(self, text="Deployment Log:").pack(pady=(10,0))
        self.deploy_log = tk.Text(self, width=120, height=20, state='disabled', bg="#f0f0f0", wrap='word')
        self.deploy_log.pack(padx=10, pady=5)
        self.scrollbar = tk.Scrollbar(self.deploy_log, command=self.deploy_log.yview)
        self.deploy_log['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side='right', fill='y')

    def append_log(self, message):
        self.deploy_log.configure(state='normal')
        self.deploy_log.insert('end', message + "\n")
        self.deploy_log.see('end')
        self.deploy_log.configure(state='disabled')

    def render_products(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        self.product_widgets.clear()

        for i, prod in enumerate(self.data['products']):
            frame = tk.Frame(self.products_frame, relief=tk.RIDGE, borderwidth=1, padx=5, pady=5)
            frame.pack(pady=5, fill=tk.X)

            tk.Label(frame, text=f"Product {i+1}").grid(row=0, column=0, padx=5)

            name_entry = tk.Entry(frame, width=30)
            name_entry.insert(0, prod['name'])
            name_entry.grid(row=0, column=1, padx=5)

            price_entry = tk.Entry(frame, width=10)
            price_entry.insert(0, prod['price'])
            price_entry.grid(row=0, column=2, padx=5)

            image_entry = tk.Entry(frame, width=50)
            image_entry.insert(0, prod['image'])
            image_entry.grid(row=0, column=3, padx=5)

            remove_btn = tk.Button(frame, text="Remove", fg="red", command=lambda idx=i: self.remove_product(idx))
            remove_btn.grid(row=0, column=4, padx=5)

            self.product_widgets.append({
                'name': name_entry,
                'price': price_entry,
                'image': image_entry
            })

    def add_product(self):
        self.data['products'].append({"name": "", "price": "", "image": ""})
        self.render_products()

    def remove_product(self, index):
        self.data['products'].pop(index)
        self.render_products()

    def copy_url_to_clipboard(self):
        url = self.deploy_url_var.get()
        if url:
            self.clipboard_clear()
            self.clipboard_append(url)
            messagebox.showinfo("Copied", "URL copied to clipboard!")
        else:
            messagebox.showwarning("No URL", "No deployment URL available yet.")

    def save_generate_and_deploy(self):
        # Update shop info
        self.data['shop_name'] = self.shop_name.get()
        self.data['about_text'] = self.about_text.get('1.0', 'end').strip()
        self.data['contact_email'] = self.contact_email.get()
        self.data['hero_image'] = self.hero_image.get()
        self.data['about_image'] = self.about_image.get()

        # Update products
        for i, prod in enumerate(self.data['products']):
            widgets = self.product_widgets[i]
            prod['name'] = widgets['name'].get()
            prod['price'] = widgets['price'].get()
            prod['image'] = widgets['image'].get()

        # Save JSON and generate website
        save_data(self.data)
        generate_website(self.data)

        # Automatic deployment
        NETLIFY_SITE_ID = "8d8f0d99-8ff9-40ce-8228-4122625b85c9"
        NETLIFY_TOKEN = "nfp_7xKvfnUUB7WktQ9BCL5MmVRa277CXxyd8e27"

        self.append_log(f"Starting deployment of '{OUTPUT_FILE}'...")
        deploy_data = deploy.deploy_to_netlify(NETLIFY_SITE_ID, NETLIFY_TOKEN, OUTPUT_FILE, log_func=self.append_log)

        if deploy_data and "deploy_ssl_url" in deploy_data:
            self.deploy_url_var.set(deploy_data["deploy_ssl_url"])
            self.append_log(f"\nDeployment successful! Your site is live at:\nURL: {deploy_data['deploy_ssl_url']}")

if __name__ == '__main__':
    app = ShopDashboard()
    app.mainloop()
