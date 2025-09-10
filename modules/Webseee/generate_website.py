import json
from bs4 import BeautifulSoup
import os

# --- CONFIGURATION ---
TEMPLATE_HTML_FILE = 'template.html'
CONFIG_FILE = 'config.json'
OUTPUT_HTML_FILE = 'your_website.html'

def update_colors(html_content, old_color, new_color):
    """Replaces all instances of the old color with the new one in Tailwind classes."""
    print(f"🎨 Updating color scheme from '{old_color}' to '{new_color}'...")
    # A list of common Tailwind shades to replace
    shades = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900']
    
    # Replace base color and shaded variants
    html_content = html_content.replace(f'-{old_color}-', f'-{new_color}-')
    for shade in shades:
        html_content = html_content.replace(f'{old_color}-{shade}', f'{new_color}-{shade}')
        
    return html_content

def generate_website():
    """
    Generates a new website HTML file based on the template and config.
    """
    print("🚀 Starting website generation...")

    # --- 1. Load Files ---
    try:
        with open(TEMPLATE_HTML_FILE, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
    except FileNotFoundError as e:
        print(f"❌ ERROR: File not found - {e}. Make sure '{TEMPLATE_HTML_FILE}' and '{CONFIG_FILE}' are in the same folder as the script.")
        return
    except json.JSONDecodeError:
        print(f"❌ ERROR: Could not read '{CONFIG_FILE}'. Please check if it's a valid JSON format.")
        return

    # --- 2. Update Basic Store Info ---
    print("Updating store information...")
    store_info = config.get('store_info', {})
    
    # Update Page Title
    if soup.title:
        soup.title.string = f"{store_info.get('name', 'My Shop')} - {store_info.get('tagline', 'Welcome')}"

    # Update Store Name in Header
    header_link = soup.select_one('header nav a.font-bold')
    if header_link:
        # Using .contents to preserve the <i> icon
        icon = header_link.find('i')
        header_link.clear()
        if icon:
            header_link.append(icon)
        header_link.append(f" {store_info.get('name', 'My Shop')}")

    # --- 3. Update Hero Section ---
    print("Updating hero section...")
    hero_section = config.get('sections', {}).get('hero', {})
    hero_h1 = soup.select_one('#home h1')
    if hero_h1:
        hero_h1.string = hero_section.get('title', 'Welcome to Our Store')
    hero_p = soup.select_one('#home p')
    if hero_p:
        hero_p.string = hero_section.get('subtitle', 'Find amazing products here.')
    hero_bg = soup.select_one('.hero-bg')
    if hero_bg and hero_section.get('background_image_url'):
        hero_bg['style'] = f"background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('{hero_section.get('background_image_url')}');"

    # --- 4. Update About Section ---
    print("Updating about section...")
    about_section = config.get('sections', {}).get('about', {})
    about_h2 = soup.select_one('#about h2')
    if about_h2:
        about_h2.string = about_section.get('title', 'About Us')
    
    about_paragraphs = soup.select('#about p')
    about_content = about_section.get('content', [])
    for i, p_tag in enumerate(about_paragraphs):
        if i < len(about_content):
            p_tag.string = about_content[i]
        else:
            p_tag.decompose() # Remove extra <p> tags if not needed
            
    about_image = soup.select_one('#about img')
    if about_image and about_section.get('image_url'):
        about_image['src'] = about_section.get('image_url')
        about_image['alt'] = "About our store"

    # --- 5. Update Footer ---
    print("Updating footer...")
    footer_config = config.get('footer', {})
    
    # Update copyright
    copyright_p = soup.select_one('footer p.text-gray-500')
    if copyright_p:
        copyright_p.string = f"© {footer_config.get('copyright_year', '2025')} {store_info.get('name', 'My Shop')}. All Rights Reserved."

    # Update social links
    social_links = footer_config.get('social_media', {})
    footer_social_container = soup.select_one('footer .flex.justify-center.space-x-6')
    if footer_social_container:
        # Clear existing links to rebuild them from config
        footer_social_container.clear()
        for platform, url in social_links.items():
            if url: # Only add the link if a URL is provided
                new_link = soup.new_tag('a', href=url, **{'class': 'text-gray-400 hover:text-white transition duration-300 transform hover:scale-110'})
                new_icon = soup.new_tag('i', **{'class': f'fab fa-{platform} text-2xl'})
                new_link.append(new_icon)
                footer_social_container.append(new_link)
            
    # --- 6. Update Products in JavaScript ---
    print("Updating product list...")
    products = config.get('products', [])
    # Convert Python list of dicts to a JSON string, which is valid JavaScript object notation
    products_js_array = json.dumps(products, indent=16)

    # Find the script tag and replace the products array
    script_tag = soup.find('script')
    if script_tag and script_tag.string:
        script_content = script_tag.string
        # Find the start and end of the products array in the script
        start_marker = 'const products = ['
        end_marker = '];'
        start_index = script_content.find(start_marker)
        end_index = script_content.find(end_marker, start_index)

        if start_index != -1 and end_index != -1:
            # Reconstruct the script content with the new product data
            new_script_content = (
                script_content[:start_index] +
                f'const products = {products_js_array}' +
                script_content[end_index + len(end_marker)-1:]
            )
            script_tag.string = new_script_content
        else:
            print("⚠️ Could not find the products array in the script tag to update it.")
    else:
        print("⚠️ Could not find the main script tag.")

    # --- 7. Save the final HTML and update colors ---
    # Convert soup to string first to handle color replacement
    final_html = str(soup)

    # Update color scheme
    color_scheme = config.get('style', {})
    original_color = color_scheme.get('original_theme_color', 'indigo')
    new_color = color_scheme.get('new_theme_color', 'indigo')
    if original_color != new_color:
        final_html = update_colors(final_html, original_color, new_color)

    with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"\n✅ Success! Your new website has been saved as '{OUTPUT_HTML_FILE}'")
    print(f"   You can now open this file in your browser to see your shop.")


if __name__ == '__main__':
    # This allows the script to be run directly from the command line
    generate_website()

