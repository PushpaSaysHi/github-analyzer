"""
api.py — All GitHub API calls
"""

import requests
from config import BASE_URL


def get_user(username: str) -> dict:
    """Fetch basic user profile."""
    response = requests.get(f"{BASE_URL}/users/{username}")
    if response.status_code == 404:
        return None
    return response.json()


def get_repos(username: str) -> list:
    """Fetch all public repos."""
    response = requests.get(f"{BASE_URL}/users/{username}/repos?per_page=100")
    return response.json()


def get_commit_activity(username: str, repos: list) -> dict:
    """Get commit count across all repos."""
    total_commits = 0
    active_repos  = 0

    for repo in repos[:10]:
        repo_name = repo["name"]
        response  = requests.get(
            f"{BASE_URL}/repos/{username}/{repo_name}/commits?per_page=100"
        )
        if response.status_code == 200:
            commits = response.json()
            if isinstance(commits, list) and len(commits) > 0:
                total_commits += len(commits)
                active_repos  += 1

    return {
        "total_commits": total_commits,
        "active_repos":  active_repos,
    }


def search_users_by_language(language: str) -> list:
    """Search GitHub users by language."""
    response = requests.get(
        f"https://api.github.com/search/users?q=language:{language}&sort=followers&per_page=10"
    )
    if response.status_code != 200:
        return []
    return response.json().get("items", [])
