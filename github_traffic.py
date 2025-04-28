import requests
import json

# Replace with your GitHub personal access token
GITHUB_TOKEN = "<your_github_token>"
REPO_OWNER = "yavru421"
REPO_NAME = "groqee"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_traffic_views():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/traffic/views"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_traffic_clones():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/traffic/clones"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def main():
    print("Fetching repository traffic data...\n")

    # Get traffic views
    views_data = get_traffic_views()
    print("Views Data:")
    print(json.dumps(views_data, indent=4))

    # Get traffic clones
    clones_data = get_traffic_clones()
    print("\nClones Data:")
    print(json.dumps(clones_data, indent=4))

if __name__ == "__main__":
    main()