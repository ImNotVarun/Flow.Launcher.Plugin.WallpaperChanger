import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import random
import requests
import ctypes
from flowlauncher import FlowLauncher

# Updated Pexels API endpoint: removed 'per_page' to only rely on the default page results
PEXELS_URL = "https://api.pexels.com/v1/search?query={category}&page={page}"

class WallpaperChanger(FlowLauncher):
    # Expanded wallpaper categories with 'Random' always at the top
    categories = ["Random"] + sorted([
        "Nature", "Waves", "Animals", "Landscape", "Mountains", "Quote", "City", 
        "Abstract", "Beach", "Trees", "Sunset", "Flowers", "Space", 
        "Underwater", "Minimalist", "Cars", "Sports", "Night Sky", "Forests"
    ])

    def query(self, query):
        """Handles user input and provides options."""
        query = query.strip()

        # Handle API key setting
        if query.lower().startswith("key "):
            api_key = query[4:].strip()
            if api_key:
                self.set_api_key(api_key)
                return [{
                    "Title": "Pexels API Key Set",
                    "SubTitle": "API key saved successfully.",
                    "IcoPath": "Images\\app.png"
                }]
            return [{
                "Title": "Enter your Pexels API Key",
                "SubTitle": "Usage: wall key your-api-key",
                "IcoPath": "Images\\app.png"
            }]

        # Ensure an API key is set before proceeding
        if not self.get_user_api_key():
            return [{
                "Title": "Enter your Pexels API Key",
                "SubTitle": "Usage: wall key your-api-key",
                "IcoPath": "Images\\app.png"
            }]

        # If no query is given, return all available categories
        if not query:
            return [{
                "Title": f"{cat} wallpaper",
                "SubTitle": "Click to change wallpaper",
                "IcoPath": "Images\\app.png",
                "JsonRPCAction": {"method": "change_wallpaper", "parameters": [cat]}
            } for cat in self.categories]

        # When a query is provided, always include "Random wallpaper" as the first option.
        options = [{
            "Title": "Random wallpaper",
            "SubTitle": "Click to change wallpaper",
            "IcoPath": "Images\\app.png",
            "JsonRPCAction": {"method": "change_wallpaper", "parameters": ["Random"]}
        }]

        # If the query isn't "random", add the query wallpaper option after "Random"
        if query.lower() != "random":
            options.append({
                "Title": f"{query.title()} wallpaper",
                "SubTitle": "Click to change wallpaper",
                "IcoPath": "Images\\app.png",
                "JsonRPCAction": {"method": "change_wallpaper", "parameters": [query]}
            })

        return options

    def change_wallpaper(self, category):
        """Fetches a wallpaper from Pexels and sets it as the desktop background."""
        try:
            api_key = self.get_user_api_key()
            if not api_key:
                return

            # If 'Random' is chosen, pick a random category (excluding "Random")
            if category.lower() == "random":
                category = random.choice([cat for cat in self.categories if cat.lower() != "random"])
            
            # Fetch images from Pexels API using the updated URL without 'per_page'
            url = PEXELS_URL.format(category=category, page=random.randint(1, 10))
            response = requests.get(url, headers={"Authorization": api_key})
            if response.status_code != 200:
                return

            # Filter for landscape images (wider than taller)
            images = [img for img in response.json().get("photos", [])
                      if img.get("width", 0) > img.get("height", 0)]
            if not images:
                return

            # Select a random image from the returned page and download it
            selected_image = random.choice(images)["src"]["original"]
            wallpaper_path = os.path.join(os.path.expanduser("~"), "wallpaper.jpg")
            with open(wallpaper_path, "wb") as f:
                f.write(requests.get(selected_image).content)
            
            # Set the downloaded image as the wallpaper
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
        except Exception:
            pass

    def get_user_api_key(self):
        """Retrieves the stored Pexels API key from a file."""
        api_key_file = os.path.join(os.path.dirname(__file__), "pexels_api_key.txt")
        if os.path.exists(api_key_file):
            with open(api_key_file, "r") as f:
                return f.read().strip()
        return None

    def set_api_key(self, api_key):
        """Saves the Pexels API key to a file."""
        api_key_file = os.path.join(os.path.dirname(__file__), "pexels_api_key.txt")
        with open(api_key_file, "w") as f:
            f.write(api_key)

if __name__ == "__main__":
    WallpaperChanger()
