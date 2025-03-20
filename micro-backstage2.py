import requests
import base64
import os

# GitHub Authentication Token (Use an environment variable for security)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Source Repository (where we fetch folders from)
SOURCE_OWNER = "source-org-or-user"
SOURCE_REPO = "source-repo"
SOURCE_BRANCH = "main"
SOURCE_DIRECTORY = "src"  # The folder to scan for top-level directories

# Destination Repository (where we create the same folders)
DEST_OWNER = "dest-org-or-user"
DEST_REPO = "dest-repo"
DEST_BRANCH = "main"
DEST_DIRECTORY = "services"  # The root folder where new folders will be created

# GitHub API Base URL
GITHUB_API_BASE = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Default content for catalog-config.yaml
CATALOG_CONFIG_CONTENT = """apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  description: Auto-generated catalog file
spec:
  type: service
  lifecycle: production
  owner: team-a
"""


def get_top_level_folders():
    """Fetch only top-level folders from the source GitHub repository."""
    url = f"{GITHUB_API_BASE}/repos/{SOURCE_OWNER}/{SOURCE_REPO}/contents/{SOURCE_DIRECTORY}?ref={SOURCE_BRANCH}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        items = response.json()
        folders = [item["name"] for item in items if item["type"] == "dir"]
        return folders
    else:
        print(f"❌ Error fetching folders: {response.json()}")
        return []


def folder_exists_in_destination(folder_name):
    """Check if the folder already exists in the destination repository."""
    url = f"{GITHUB_API_BASE}/repos/{DEST_OWNER}/{DEST_REPO}/contents/{DEST_DIRECTORY}/{folder_name}?ref={DEST_BRANCH}"
    response = requests.get(url, headers=HEADERS)
    
    return response.status_code == 200  # If the folder exists, the API returns 200


def create_catalog_file_in_github(folder_name):
    """Create a catalog-config.yaml file in the destination GitHub repository."""
    file_path = f"{DEST_DIRECTORY}/{folder_name}/catalog-config.yaml"
    commit_message = f"Create catalog-config.yaml for {folder_name}"
    file_content = base64.b64encode(CATALOG_CONFIG_CONTENT.encode()).decode()

    url = f"{GITHUB_API_BASE}/repos/{DEST_OWNER}/{DEST_REPO}/contents/{file_path}"
    data = {
        "message": commit_message,
        "content": file_content,
        "branch": DEST_BRANCH
    }

    response = requests.put(url, headers=HEADERS, json=data)
    if response.status_code in [201, 200]:
        print(f"✅ Created catalog-config.yaml in {folder_name}")
    else:
        print(f"❌ Failed to create catalog-config.yaml in {folder_name}: {response.json()}")


if __name__ == "__main__":
    folders = get_top_level_folders()
    if folders:
        print(f"🔍 Found folders: {folders}")
        for folder in folders:
            if folder_exists_in_destination(folder):
                print(f"⚠️ Skipping {folder}, as it already exists.")
            else:
                create_catalog_file_in_github(folder)
    else:
        print("❌ No folders found or an error occurred.")
