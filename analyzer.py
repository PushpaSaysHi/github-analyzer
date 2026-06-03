"""
GitHub Analyzer — Analyze any GitHub profile
"""

import requests
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

BASE_URL = "https://api.github.com"


def get_user(username: str):
    response = requests.get(f"{BASE_URL}/users/{username}")
    if response.status_code == 404:
        console.print(f"[red]❌ User '{username}' not found![/red]")
        return None
    return response.json()


def get_repos(username: str):
    response = requests.get(f"{BASE_URL}/users/{username}/repos?per_page=100")
    return response.json()


def get_commit_activity(username: str, repos: list) -> dict:
    """Get commit count from last 12 months across all repos."""
    total_commits = 0
    active_repos  = 0

    for repo in repos[:10]:  # limit to 10 repos to avoid rate limiting
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


def get_languages(repos: list) -> dict:
    languages = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))


def get_top_repos(repos: list, n=3) -> list:
    return sorted(repos, key=lambda x: x["stargazers_count"], reverse=True)[:n]


def calculate_profile_score(user: dict, repos: list, languages: dict, commit_data: dict) -> int:
    """Calculate a profile score out of 100."""
    score = 0

    # Bio — 10 points
    if user.get("bio"):
        score += 10

    # Profile picture — 5 points
    if user.get("avatar_url"):
        score += 5

    # Website/portfolio — 10 points
    if user.get("blog"):
        score += 10

    # Location — 5 points
    if user.get("location"):
        score += 5

    # Number of repos — up to 15 points
    repos_count = user.get("public_repos", 0)
    if repos_count >= 10:
        score += 15
    elif repos_count >= 5:
        score += 10
    elif repos_count >= 2:
        score += 5

    # Followers — up to 10 points
    followers = user.get("followers", 0)
    if followers >= 50:
        score += 10
    elif followers >= 10:
        score += 7
    elif followers >= 1:
        score += 3

    # Languages diversity — up to 10 points
    if len(languages) >= 4:
        score += 10
    elif len(languages) >= 2:
        score += 5

    # Stars on repos — up to 15 points
    total_stars = sum(r["stargazers_count"] for r in repos)
    if total_stars >= 20:
        score += 15
    elif total_stars >= 5:
        score += 10
    elif total_stars >= 1:
        score += 5

    # Commit activity — up to 15 points
    commits = commit_data.get("total_commits", 0)
    if commits >= 200:
        score += 15
    elif commits >= 100:
        score += 10
    elif commits >= 50:
        score += 7
    elif commits >= 10:
        score += 4

    # Active repos — up to 5 points
    if commit_data.get("active_repos", 0) >= 3:
        score += 5

    return min(score, 100)


def get_score_color(score: int) -> str:
    if score >= 80:
        return "green"
    elif score >= 60:
        return "yellow"
    elif score >= 40:
        return "orange3"
    else:
        return "red"


def get_score_label(score: int) -> str:
    if score >= 80:
        return "🌟 Excellent"
    elif score >= 60:
        return "👍 Good"
    elif score >= 40:
        return "📈 Average"
    else:
        return "⚠️  Needs Work"


def analyze(username: str):
    console.print(f"\n[dim]🔍 Analyzing [cyan]{username}[/cyan]... please wait[/dim]\n")

    user  = get_user(username)
    if not user:
        return
    repos = get_repos(username)

    console.print("[dim]📊 Fetching commit activity...[/dim]")
    commit_data = get_commit_activity(username, repos)
    languages   = get_languages(repos)

    # calculate score
    score       = calculate_profile_score(user, repos, languages, commit_data)
    score_color = get_score_color(score)
    score_label = get_score_label(score)

    # ── Profile Panel ──
    console.print(Panel(
        f"[bold cyan]{user.get('name') or username}[/bold cyan]\n"
        f"[dim]{user.get('bio') or 'No bio'}[/dim]\n\n"
        f"📍 {user.get('location') or 'Unknown'}\n"
        f"🔗 {user.get('blog') or 'No website'}\n"
        f"👥 [green]{user.get('followers')}[/green] followers  "
        f"· [yellow]{user.get('following')}[/yellow] following\n"
        f"📦 [cyan]{user.get('public_repos')}[/cyan] public repos",
        title="👤 Profile",
        border_style="cyan"
    ))

    # ── Profile Score ──
    console.print(Panel(
        f"[bold {score_color}]{score}/100[/bold {score_color}]  {score_label}\n\n"
        f"[dim]{'█' * (score // 5)}{'░' * (20 - score // 5)}[/dim]  [{score_color}]{score}%[/{score_color}]",
        title="🏆 Profile Score",
        border_style=score_color
    ))

    # ── Commit Activity ──
    console.print(Panel(
        f"📝 Total commits (last 100 per repo): [cyan]{commit_data['total_commits']}[/cyan]\n"
        f"📁 Active repositories: [green]{commit_data['active_repos']}[/green]\n\n"
        + _get_activity_rating(commit_data['total_commits']),
        title="📈 Commit Activity",
        border_style="green"
    ))

    # ── Languages ──
    if languages:
        lang_table = Table(title="🧑‍💻 Most Used Languages", style="cyan")
        lang_table.add_column("Language", style="bold yellow")
        lang_table.add_column("Repos",    justify="right", style="green")

        total = sum(languages.values())
        for lang, count in list(languages.items())[:6]:
            percent = round((count / total) * 100)
            lang_table.add_row(lang, f"{count} ({percent}%)")

        console.print(lang_table)

    # ── Top Repos ──
    top_repos = get_top_repos(repos)
    if top_repos:
        repo_table = Table(title="⭐ Top Repositories", style="cyan")
        repo_table.add_column("Repo",        style="bold white")
        repo_table.add_column("Stars",       justify="right", style="yellow")
        repo_table.add_column("Forks",       justify="right", style="green")
        repo_table.add_column("Language",    style="cyan")
        repo_table.add_column("Description", style="dim")

        for repo in top_repos:
            repo_table.add_row(
                repo["name"],
                str(repo["stargazers_count"]),
                str(repo["forks_count"]),
                repo.get("language") or "N/A",
                (repo.get("description") or "No description")[:50]
            )

        console.print(repo_table)

    # ── Recommendations ──
    console.print(Panel(
        _get_recommendations(user, repos, languages, commit_data),
        title="💡 Recommendations",
        border_style="yellow"
    ))


def _get_activity_rating(commits: int) -> str:
    if commits >= 200:
        return "[green]🔥 Very Active — Keep it up![/green]"
    elif commits >= 100:
        return "[yellow]👍 Active — Good consistency![/yellow]"
    elif commits >= 50:
        return "[orange3]📈 Moderate — Try to commit more often![/orange3]"
    elif commits >= 10:
        return "[red]⚠️  Low Activity — Commit every day![/red]"
    else:
        return "[red]😴 Inactive — Start building![/red]"


def _get_recommendations(user, repos, languages, commit_data) -> str:
    tips = []

    if user.get("public_repos", 0) < 5:
        tips.append("📦 Build more projects — aim for at least 5 public repos")

    if not user.get("bio"):
        tips.append("✍️  Add a bio to your GitHub profile")

    if not user.get("blog"):
        tips.append("🔗 Add your portfolio website link")

    if not user.get("location"):
        tips.append("📍 Add your location to your profile")

    if commit_data.get("total_commits", 0) < 50:
        tips.append("📝 Commit more often — daily commits build great habits")

    if "JavaScript" not in languages and "TypeScript" not in languages:
        tips.append("🌐 Consider learning JavaScript to expand into web development")

    if len(languages) < 3:
        tips.append("🧑‍💻 Try learning more languages to diversify your skills")

    if not tips:
        tips.append("✅ Great profile! Keep building and contributing!")

    return "\n".join(tips)


def main():
    console.print(Panel(
        Text("🔍 GitHub Profile Analyzer", justify="center", style="bold cyan"),
        border_style="cyan"
    ))

    while True:
        username = input("\nEnter GitHub username (or 'quit' to exit): ").strip()
        if username.lower() == "quit":
            console.print("\n[cyan]👋 Goodbye![/cyan]\n")
            break
        if not username:
            console.print("[red]❌ Please enter a username.[/red]")
            continue
        analyze(username)


if __name__ == "__main__":
    main()