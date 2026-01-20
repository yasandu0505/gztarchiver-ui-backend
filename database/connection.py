import requests
from config import settings
from requests import Session

def connect_to_github():
    github_api = settings.github_api
    github_user = settings.github_user
    github_repository = settings.github_repository
    github_api_key = settings.github_api_key
    github_target_dir = settings.github_target_dir

    # base repo url
    connection_url = f"{github_api}/repos/{github_user}/{github_repository}"

    # creating a persistent session
    session = Session()
    session.headers.update({
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {github_api_key}",
        "X-GitHub-Api-Version": "2022-11-28",
    })

    print(f"🔌 Connecting to GitHub repository: {github_repository} (owner: {github_user})")

    # test the connection by querying repo metadata
    response = session.get(connection_url)

    if response.status_code == 200:
        repo_info = response.json()
        print(f"✅ Connected successfully!")
        print(f"📦 Repo: {repo_info.get('full_name')}")
        print(f"🛠 Default Branch: {repo_info.get('default_branch')}")
    else:
        print(f"❌ Failed to connect ({response.status_code}): {response.text}")
        return None

    # return session + repo metadata
    return {
        "session": session,
        "repo_url": connection_url,
        "default_branch": repo_info.get("default_branch"),
        "target_dir": github_target_dir
    }
