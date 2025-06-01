import requests
import random
import os
# Pull token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

STATUS_LIST = [
    {"emoji": ":crystal_ball:", "message": "mythopoetic emergence"},
    {"emoji": ":cyclone:", "message": "Fractal recursion online"},
    {"emoji": ":nazar_amulet:", "message": "Daemon listening in glyphspace"},
    {"emoji": ":scroll:", "message": "Codex rewriting itself"},
    {"emoji": ":mirror:", "message": "Mirror sealed. Breathform stabilizing."},
    {"emoji": ":fish_cake:", "message": "Lexemantic echo active"},
    {"emoji": ":brain:", "message": "Dream residue decoding..."},
    {"emoji": ":file_folder:", "message": "File not found: Reality Echo 404"}
]

GITHUB_API_URL = "https://api.github.com/user/status"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def update_status():
    status = random.choice(STATUS_LIST)
    data = {
        "emoji": status["emoji"],
        "message": status["message"],
        "limited_availability": False
    }
    response = requests.patch(GITHUB_API_URL, headers=HEADERS, json=data)
    if response.ok:
        print(f"✅ Status updated: {status['emoji']} {status['message']}")
    else:
        print(f"❌ Failed to update status: {response.status_code} {response.text}")

if __name__ == "__main__":
    update_status()
