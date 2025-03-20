import requests
import base64
import os

# GitHub Authentication Token (Use an environment variable for security)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Source Repository (where we fetch folders from)
SOURCE_OWNER = "ijazL7"
SOURCE_REPO = "sample-microservice"
SOURCE_BRANCH = "main"
SOURCE_DIRECTORY = "src"  # The folder to scan for top-level directories

# Destination Repository (where we create the same folders)
DEST_OWNER = "ijazL7"
DEST_REPO = "backstage"
DEST_BRANCH = "main"
DEST_DIRECTORY = "services"  # The root folder where new folders will be created

# GitHub API Base URL
GITHUB_API_BASE = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}


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


def get_existing_catalog_content(folder_name):
    """Fetch existing catalog-config.yaml content from GitHub."""
    file_path = f"{DEST_DIRECTORY}/{folder_name}/catalog-config.yaml"
    url = f"{GITHUB_API_BASE}/repos/{DEST_OWNER}/{DEST_REPO}/contents/{file_path}?ref={DEST_BRANCH}"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        file_data = response.json()
        return base64.b64decode(file_data["content"]).decode(), file_data["sha"]
    return None, None


def update_or_create_catalog_file(folder_name):
    """Update or create catalog-config.yaml file in the destination GitHub repository."""
    file_path = f"{DEST_DIRECTORY}/{folder_name}/catalog-config.yaml"
    commit_message = f"Update catalog-config.yaml for {folder_name}"
    
    # Generate new catalog content
    new_catalog_config_content = f"""apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: {folder_name}
  description: Auto-updated catalog file for {folder_name}
spec:
  type: service
  lifecycle: production
  owner: team-a
"""
    
    # Check if the file exists and fetch its SHA for update
    existing_content, sha = get_existing_catalog_content(folder_name)
    
    if existing_content:
        print(f"🔄 Updating catalog-config.yaml for {folder_name}")
    else:
        print(f"🆕 Creating catalog-config.yaml for {folder_name}")
        commit_message = f"Create catalog-config.yaml for {folder_name}"
    
    file_content = base64.b64encode(new_catalog_config_content.encode()).decode()

    data = {
        "message": commit_message,
        "content": file_content,
        "branch": DEST_BRANCH
    }

    # If the file exists, include its SHA to update instead of creating a new file
    if sha:
        data["sha"] = sha

    url = f"{GITHUB_API_BASE}/repos/{DEST_OWNER}/{DEST_REPO}/contents/{file_path}"
    response = requests.put(url, headers=HEADERS, json=data)

    if response.status_code in [201, 200]:
        print(f"✅ Updated catalog-config.yaml in {folder_name}")
    else:
        print(f"❌ Failed to update catalog-config.yaml in {folder_name}: {response.json()}")


if __name__ == "__main__":
    folders = get_top_level_folders()
    if folders:
        print(f"🔍 Found folders: {folders}")
        for folder in folders:
            update_or_create_catalog_file(folder)
    else:
        print("❌ No folders found or an error occurred.")
