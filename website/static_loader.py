import requests

STATIC = {
    "online_static/popper.min.js": "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js",
    "online_static/bootstrap.min.js": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js",
    "online_static/jquery.js": "https://code.jquery.com/jquery-3.5.1.js",
    "online_static/bootstrap.min.css": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
    "online_static/bootstrap-icons.css": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.3/font/bootstrap-icons.css",
}

def download_static_files():
    for local_path, url in STATIC.items():
        response = requests.get(url)
        if response.status_code == 200:
            full_path = f"website/static/{local_path}"
            # Create directories if they don't exist
            import os
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            # Write the file
            with open(full_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded {local_path}")
        else:
            print(f"Failed to download {local_path}")

if __name__ == "__main__":
    download_static_files()

