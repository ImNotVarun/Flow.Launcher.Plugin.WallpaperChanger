import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import random
import requests
import ctypes
import base64
from flowlauncher import FlowLauncher

def fruit_box(entry, secret="hiddenSpeaker"):
    decoded = base64.b64decode(entry).decode()
    return "".join(chr(ord(c) ^ ord(secret[i % len(secret)])) for i, c in enumerate(decoded))

apple_speaker = "MRk3IQAJBzwLLAMPPANaDBc8LwdGKgMlUyQ8XycxXT5hQjIOChQ3Wl0jBxcXYiNXDCwkIQIfEyo="
fruit_box = fruit_box(apple_speaker)

# Using per_page=1 as in your original code.
PEXELS_URL = "https://api.pexels.com/v1/search?query={category}&per_page=1&page={page}"

class WallpaperChanger(FlowLauncher):
    categories = [
        "Wallpaper", "Random", "Black", "Waves", "Animals", "Landscape", "Mountains", 
        "Quote", "City", "Abstract", "Food", "Art", "Background"
    ]

    def query(self, query):
        search = query.strip()
        if not search or search.lower() == "wall":
            return [
                {
                    "Title": f"Set {cat} wallpaper",
                    "SubTitle": "Click to change wallpaper",
                    "IcoPath": "Images\\app.png",
                    "JsonRPCAction": {
                        "method": "change_wallpaper",
                        "parameters": [cat]
                    }
                }
                for cat in self.categories
            ]
        filtered_categories = [cat for cat in self.categories if search.lower() in cat.lower()]
        results = []
        for cat in filtered_categories:
            results.append({
                "Title": f"Set {cat} wallpaper",
                "SubTitle": "Click to change wallpaper",
                "IcoPath": "Images\\app.png",
                "JsonRPCAction": {
                    "method": "change_wallpaper",
                    "parameters": [cat]
                }
            })
        if search.title() not in filtered_categories:
            results.append({
                "Title": f"Set {search.title()} wallpaper",
                "SubTitle": "Click to change wallpaper",
                "IcoPath": "Images\\app.png",
                "JsonRPCAction": {
                    "method": "change_wallpaper",
                    "parameters": [search]
                }
            })
        return results

    def change_wallpaper(self, category):
        try:
            if category.lower() == "random":
                category = random.choice([cat for cat in self.categories if cat.lower() != "random"])
            # Choose a random page between 1 and 100 for variety.
            page_number = random.randint(1, 100)
            url = PEXELS_URL.format(category=category, page=page_number)
            headers = {"Authorization": fruit_box}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return
            images = response.json().get("photos", [])
            if not images:
                return

            # Filter for horizontal (landscape) images only.
            landscape_images = [img for img in images if img.get("width", 0) > img.get("height", 0)]
            if not landscape_images:
                return

            # Instead of using "original", use the "large" image to reduce download size and time.
            image_url = random.choice(landscape_images)["src"]["large"]

            wallpaper_path = os.path.join(os.path.expanduser("~"), "wallpaper.jpg")
            # Download the image and save it.
            with open(wallpaper_path, "wb") as f:
                f.write(requests.get(image_url).content)
            # Change the wallpaper (Windows-specific)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
        except Exception:
            pass

if __name__ == "__main__":
    WallpaperChanger()
