import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import random
import requests
import ctypes
import webbrowser
from flowlauncher import FlowLauncher

PEXELS_URL = "https://api.pexels.com/v1/search?query={category}&page={page}"
PEXELS_API_PAGE = "https://www.pexels.com/api/"

class WallpaperChanger(FlowLauncher):

    categories = ["Random"] + sorted([
        "Nature", "Waves", "Animals", "Landscape", "Mountains", "Quote", "City", 
        "Abstract", "Beach", "Trees", "Sunset", "Flowers", "Space", 
        "Underwater", "Minimalist", "Cars", "Sports", "Night Sky", "Forests"
    ])

    def query(self, query):
        query = query.strip()

        if query.lower().startswith("key "):
            api_key = query[4:].strip()
            if api_key:
                return [{
                    "Title": "Save API Key",
                    "SubTitle": f"Press Enter to save API key: {api_key}",
                    "IcoPath": "Images\\app.png",
                    "JsonRPCAction": {"method": "save_api_key", "parameters": [api_key]}
                }]
            else:
                return [{
                    "Title": "Invalid API Key",
                    "SubTitle": "Usage: wall key your-api-key",
                    "IcoPath": "Images\\app.png"
                }]

        # If no API key is set, instruct the user and offer to open the Pexels API page.
        if not self.get_user_api_key():
            return [{
                "Title": "Pexels API key not set Click to open Pexels API",
                "SubTitle": ("Use 'wall key <your-api-key>' to set it."),
                "IcoPath": "Images\\app.png",
                "JsonRPCAction": {"method": "open_pexels_api_page", "parameters": []}
            }]
        
        if not query:
            return [{
                "Title": f"{cat} wallpaper",
                "SubTitle": "Click to change wallpaper",
                "IcoPath": "Images\\app.png",
                "JsonRPCAction": {"method": "change_wallpaper", "parameters": [cat]}
            } for cat in self.categories]
        else:
            return [{
                "Title": f"{query.title()} wallpaper",
                "SubTitle": "Click to change wallpaper",
                "IcoPath": "Images\\app.png",
                "JsonRPCAction": {"method": "change_wallpaper", "parameters": [query]}
            }]

    def save_api_key(self, api_key):
        self.set_api_key(api_key)
        return [{
            "Title": "Pexels API Key Saved",
            "SubTitle": "Your API key has been saved successfully.",
            "IcoPath": "Images\\app.png"
        }]
    
    def open_pexels_api_page(self):
        webbrowser.open(PEXELS_API_PAGE)
        return [{
            "Title": "Opened Pexels API Page",
            "SubTitle": ("Please copy your API key from the opened page and set it "
                         "using 'wall key <your-api-key>'."),
            "IcoPath": "Images\\app.png"
        }]


    def change_wallpaper(self, category):
        try:
            api_key = self.get_user_api_key()
            if not api_key:
                return

            if category.lower() == "random":
                category = random.choice([cat for cat in self.categories if cat.lower() != "random"])
            url = PEXELS_URL.format(category=category, page=random.randint(1, 10))
            response = requests.get(url, headers={"Authorization": api_key})
            if response.status_code != 200:
                return

            images = [img for img in response.json().get("photos", [])
                      if img.get("width", 0) > img.get("height", 0)]
            if not images:
                return

            selected_image = random.choice(images)["src"]["original"]
            wallpaper_path = os.path.join(os.path.expanduser("~"), "wallpaper.jpg")
            with open(wallpaper_path, "wb") as f:
                f.write(requests.get(selected_image).content)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
        except Exception:
            pass

    def get_plugin_settings_directory(self):
        settings_dir = os.path.join(os.getenv("APPDATA"), "FlowLauncher", "Settings", "Plugins", "Wallpaper Changer")
        os.makedirs(settings_dir, exist_ok=True)
        return settings_dir

    def get_user_api_key(self):
        api_key_file = os.path.join(self.get_plugin_settings_directory(), "pexels_api_key.txt")
        if os.path.exists(api_key_file):
            with open(api_key_file, "r") as f:
                return f.read().strip()
        return None

    def set_api_key(self, api_key):
        api_key_file = os.path.join(self.get_plugin_settings_directory(), "pexels_api_key.txt")
        with open(api_key_file, "w") as f:
            f.write(api_key)

if __name__ == "__main__":
    WallpaperChanger()
