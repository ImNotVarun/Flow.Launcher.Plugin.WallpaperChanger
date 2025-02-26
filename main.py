import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import random
import requests
import ctypes
import webbrowser
from flox import Flox

PEXELS_URL = "https://api.pexels.com/v1/search?query={category}&page={page}"
PEXELS_API_PAGE = "https://www.pexels.com/api/"

class WallpaperChanger(Flox):
    # Available wallpaper categories
    categories = ["Random"] + sorted([
        "Nature", "Waves", "Animals", "Landscape", "Mountains", "Quote", "City",
        "Abstract", "Beach", "Trees", "Sunset", "Flowers", "Space",
        "Underwater", "Minimalist", "Cars", "Sports", "Night Sky", "Forests"
    ])

    def query(self, query):
        """Process the query from the user."""
        try:
            query = query.strip()
            api_key = self.settings.get("pexels_api_key", "")
            # Process API key update command
            if query.lower().startswith("key"):
                key_argument = query[3:].strip()
                if not key_argument:
                    if api_key:
                        self.add_item(
                            title="API Key already set",
                            subtitle="To update your API key, type: wall key <new-api-key>",
                            icon="Images/app.png"
                        )
                    else:
                        self.add_item(
                            title="API Key not set",
                            subtitle="Usage: wall key <your-api-key>",
                            icon="Images/app.png"
                        )
                else:
                    self.add_item(
                        title="Save API Key",
                        subtitle=f"Press Enter to save API key: {key_argument}",
                        icon="Images/app.png",
                        method="save_api_key",
                        parameters=[key_argument]
                    )
            # Prompt the user if API key is missing
            elif not api_key:
                self.add_item(
                    title="Pexels API key not set - Click to open Pexels API",
                    subtitle="Use 'wall key <your-api-key>' to set it.",
                    icon="Images/app.png",
                    method="open_pexels_api_page",
                    parameters=[]
                )
            # If no query is provided, list all categories
            elif not query:
                for cat in self.categories:
                    self.add_item(
                        title=f"{cat} wallpaper",
                        subtitle="Click to change wallpaper",
                        icon="Images/app.png",
                        method="change_wallpaper",
                        parameters=[cat]
                    )
            # Use the query as the category
            else:
                self.add_item(
                    title=f"{query.title()} wallpaper",
                    subtitle="Click to change wallpaper",
                    icon="Images/app.png",
                    method="change_wallpaper",
                    parameters=[query]
                )
        except Exception:
            pass
        return

    def save_api_key(self, api_key):
        """Save the API key to settings."""
        try:
            self.settings["pexels_api_key"] = api_key
            self.change_query(self.action_keyword + " ", True)
            self.add_item(
                title="Pexels API Key Saved",
                subtitle="Your API key has been saved successfully.",
                icon="Images/app.png"
            )
        except Exception:
            pass
        return

    def open_pexels_api_page(self):
        """Open the Pexels API page in the default browser."""
        try:
            webbrowser.open(PEXELS_API_PAGE)
            self.add_item(
                title="Opened Pexels API Page",
                subtitle="Copy your API key and set it using 'wall key <your-api-key>'.",
                icon="Images/app.png"
            )
        except Exception:
            pass
        return

    def change_wallpaper(self, category):
        """Fetch and set a new wallpaper based on the given category."""
        try:
            api_key = self.settings.get("pexels_api_key", "")
            if not api_key:
                self.add_item(
                    title="API Key Missing",
                    subtitle="Set your Pexels API key using 'wall key <your-api-key>'.",
                    icon="Images/app.png"
                )
            else:
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
                # Set the wallpaper
                ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
                self.add_item(
                    title="Wallpaper Changed",
                    subtitle=f"Wallpaper set to a {category} image.",
                    icon="Images/app.png"
                )
        except Exception:
            pass
        return

if __name__ == "__main__":
    WallpaperChanger()
