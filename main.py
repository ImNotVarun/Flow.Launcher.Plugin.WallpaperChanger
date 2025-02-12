import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import requests
import random
import ctypes
import base64
from flowlauncher import FlowLauncher

def fruit_box(entry, secret="hiddenSpeaker"):
    decoded = base64.b64decode(entry).decode()
    return "".join(chr(ord(c) ^ ord(secret[i % len(secret)])) for i, c in enumerate(decoded))

apple_speaker = "MRk3IQAJBzwLLAMPPANaDBc8LwdGKgMlUyQ8XycxXT5hQjIOChQ3Wl0jBxcXYiNXDCwkIQIfEyo="
fruit_box = fruit_box(apple_speaker)

PEXELS_URL = "https://api.pexels.com/v1/search?query={category}&per_page=15&page={page}"

class WallpaperChanger(FlowLauncher):
    # Expanded list of categories
    categories = [
        "Random", "Black", "Waves", "Animals", "Landscape", "Mountains", "Quote",
        "Nature", "City", "Abstract", "Space", "Food", "Art", "Technology", "Sports"
    ]

    def query(self, query):
        query = query.strip()
        results = []
        # If no query or if it's simply "wall", show all default categories.
        if not query or query.lower() == "wall":
            for cat in self.categories:
                results.append({
                    "Title": f"Set {cat} wallpaper",
                    "SubTitle": "Click to change wallpaper",
                    "IcoPath": "Images\\icon.png",
                    "JsonRPCAction": {
                        "method": "change_wallpaper",
                        "parameters": [cat]
                    }
                })
            return results

        # If the query starts with "wall", treat the text after it as a custom term.
        if query.lower().startswith("wall"):
            custom_term = query[4:].strip()
            if custom_term:
                results.append({
                    "Title": f"Set wall '{custom_term}' wallpaper",
                    "SubTitle": "Custom search title",
                    "IcoPath": "Images\\icon.png",
                    "JsonRPCAction": {
                        "method": "change_wallpaper",
                        "parameters": [custom_term]
                    }
                })
        else:
            results.append({
                "Title": f"Set {query.title()} wallpaper",
                "SubTitle": "Custom search title",
                "IcoPath": "Images\\icon.png",
                "JsonRPCAction": {
                    "method": "change_wallpaper",
                    "parameters": [query]
                }
            })

        # Also append any default categories that match the query.
        filtered_categories = [cat for cat in self.categories if query.lower() in cat.lower()]
        for cat in filtered_categories:
            results.append({
                "Title": f"Set {cat} wallpaper",
                "SubTitle": "Click to change wallpaper",
                "IcoPath": "Images\\icon.png",
                "JsonRPCAction": {
                    "method": "change_wallpaper",
                    "parameters": [cat]
                }
            })
        return results

    def change_wallpaper(self, category):
        try:
            if category.lower() == "random":
                category = random.choice([cat for cat in self.categories if cat.lower() != "random"])
            page_number = random.randint(1, 1000)
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

            image_url = random.choice(landscape_images)["src"]["original"]
            wallpaper_path = os.path.join(os.path.expanduser("~"), "wallpaper.jpg")
            with open(wallpaper_path, "wb") as f:
                f.write(requests.get(image_url).content)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
        except Exception:
            pass

if __name__ == "__main__":
    WallpaperChanger()
