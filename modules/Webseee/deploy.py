# import os
# import hashlib
# import requests
# import json
# import argparse

# # Base URL for the Netlify API
# NETLIFY_API_BASE = "https://api.netlify.com/api/v1"

# def get_file_sha1(filepath):
#     """Calculates the SHA1 hash of a file."""
#     sha1 = hashlib.sha1()
#     with open(filepath, 'rb') as f:
#         while True:
#             data = f.read(65536)  # Read in 64k chunks
#             if not data:
#                 break
#             sha1.update(data)
#     return sha1.hexdigest()

# def deploy_to_netlify(site_id, access_token, file_path):
#     """
#     Deploys a single HTML file to a Netlify site.

#     Args:
#         site_id (str): The API ID of your Netlify site.
#         access_token (str): Your Netlify Personal Access Token.
#         file_path (str): The local path to the file you want to deploy (e.g., 'index.html').
#     """
#     if not os.path.exists(file_path):
#         print(f"Error: File not found at '{file_path}'")
#         return

#     print(f"Starting deployment of '{file_path}' to site '{site_id}'...")

#     # --- Step 1: Calculate file hash ---
#     file_name = os.path.basename(file_path)
#     file_digest = get_file_sha1(file_path)
#     print(f"  - Calculated SHA1 for {file_name}: {file_digest}")

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
    
#     create_deploy_url = f"{NETLIFY_API_BASE}/sites/{site_id}/deploys"
#     payload = {
#         "files": {
#             f"/{file_name}": file_digest
#         }
#     }

#     try:
#         print("  - Creating new deployment on Netlify...")
#         response = requests.post(create_deploy_url, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
#         deploy_data = response.json()
#         deploy_id = deploy_data.get("id")
#         required_files = deploy_data.get("required", [])
#         print(f"  - Successfully created deployment with ID: {deploy_id}")

#         # --- Step 3: Upload the actual file(s) that Netlify needs ---
#         # Netlify's response tells us which files it doesn't already have in its cache.
#         if file_digest in required_files:
#             print(f"  - Netlify requires '{file_name}'. Uploading now...")
#             upload_url = f"{NETLIFY_API_BASE}/deploys/{deploy_id}/files/{file_name}"
#             upload_headers = {
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/octet-stream"
#             }
#             with open(file_path, 'rb') as f:
#                 file_content = f.read()
            
#             upload_response = requests.put(upload_url, headers=upload_headers, data=file_content)
#             upload_response.raise_for_status()
#             print("  - File uploaded successfully.")
#         else:
#             print(f"  - Netlify already has a copy of '{file_name}'. No upload needed.")
            
#         print("\nDeployment is processing on Netlify's side.")
#         print("It may take a moment to become live.")
#         print(f"\nDeployment successful! Your site is live at:")
#         print(f"URL: {deploy_data.get('deploy_ssl_url')}")

#     except requests.exceptions.RequestException as e:
#         print("\nAn error occurred during deployment.")
#         print(f"Error: {e}")
#         if e.response is not None:
#             print(f"Response Body: {e.response.text}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Deploy a single HTML file to Netlify.")
#     parser.add_argument("--site-id", required=True, help="Your Netlify site's API ID.")
#     parser.add_argument("--token", required=True, help="Your Netlify Personal Access Token.")
#     parser.add_argument("--file", default="index.html", help="Path to the HTML file to deploy.")
    
#     args = parser.parse_args()
    
#     deploy_to_netlify(args.site_id, args.token, args.file)
import os
import hashlib
import requests
import json

# Base URL for the Netlify API
NETLIFY_API_BASE = "https://api.netlify.com/api/v1"

def get_file_sha1(filepath):
    """Calculates the SHA1 hash of a file."""
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)  # 64k chunks
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def deploy_to_netlify(site_id, access_token, file_path, log_func=None):
    """
    Deploys a single HTML file to a Netlify site and returns deployment info.

    Args:
        site_id (str): The API ID of your Netlify site.
        access_token (str): Your Netlify Personal Access Token.
        file_path (str): The local path to the file to deploy.
        log_func (callable, optional): A function to log messages (e.g., Tkinter log widget).
    
    Returns:
        dict: Deployment info including 'deploy_ssl_url'.
    """
    def log(message):
        if log_func:
            log_func(message)
        else:
            print(message)

    if not os.path.exists(file_path):
        log(f"Error: File not found at '{file_path}'")
        return None

    file_name = os.path.basename(file_path)
    file_digest = get_file_sha1(file_path)
    log(f"Starting deployment of '{file_name}' to site '{site_id}'...")
    log(f"  - Calculated SHA1 for {file_name}: {file_digest}")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    create_deploy_url = f"{NETLIFY_API_BASE}/sites/{site_id}/deploys"
    payload = {
        "files": {
            f"/{file_name}": file_digest
        }
    }

    try:
        log("  - Creating new deployment on Netlify...")
        response = requests.post(create_deploy_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        deploy_data = response.json()
        deploy_id = deploy_data.get("id")
        required_files = deploy_data.get("required", [])
        log(f"  - Successfully created deployment with ID: {deploy_id}")

        # Upload files Netlify requires
        if file_digest in required_files:
            log(f"  - Netlify requires '{file_name}'. Uploading now...")
            upload_url = f"{NETLIFY_API_BASE}/deploys/{deploy_id}/files/{file_name}"
            upload_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/octet-stream"
            }
            with open(file_path, 'rb') as f:
                file_content = f.read()
            upload_response = requests.put(upload_url, headers=upload_headers, data=file_content)
            upload_response.raise_for_status()
            log("  - File uploaded successfully.")
        else:
            log(f"  - Netlify already has a copy of '{file_name}'. No upload needed.")

        log("\nDeployment is processing on Netlify's side. It may take a moment to become live.")
        deploy_ssl_url = deploy_data.get("deploy_ssl_url")
        if deploy_ssl_url:
            log(f"\nDeployment successful! Your site is live at:\nURL: {deploy_ssl_url}")
        return deploy_data

    except requests.exceptions.RequestException as e:
        log("\nAn error occurred during deployment.")
        log(f"Error: {e}")
        if e.response is not None:
            log(f"Response Body: {e.response.text}")
        return None

# Allow running from CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deploy a single HTML file to Netlify.")
    parser.add_argument("--site-id", required=True, help="Your Netlify site's API ID.")
    parser.add_argument("--token", required=True, help="Your Netlify Personal Access Token.")
    parser.add_argument("--file", default="index.html", help="Path to the HTML file to deploy.")
    args = parser.parse_args()
    deploy_to_netlify(args.site_id, args.token, args.file)
