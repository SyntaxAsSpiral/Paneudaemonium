import requests
import random
import os
import sys

# Pull token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable is not set.")
    sys.exit(1)

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

GITHUB_API_URL = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "status-rotator-script",
    "Content-Type": "application/json"
}

CHANGE_STATUS_MUTATION = """
mutation($emoji: String, $message: String, $limited: Boolean) {
  changeUserStatus(input: {emoji: $emoji, message: $message, limitedAvailability: $limited}) {
    status {
      emoji
      message
    }
  }
}
"""

def update_status():
    status = random.choice(STATUS_LIST)
    variables = {
        "emoji": status["emoji"],
        "message": status["message"],
        "limited": False
    }
    payload = {
        "query": CHANGE_STATUS_MUTATION,
        "variables": variables
    }
    response = requests.post(GITHUB_API_URL, headers=HEADERS, json=payload)
    if response.ok:
        print(f"✅ Status updated: {status['emoji']} {status['message']}")
    else:
        print(f"❌ Failed to update status: {response.status_code} {response.text}")

if __name__ == "__main__":
    update_status()

