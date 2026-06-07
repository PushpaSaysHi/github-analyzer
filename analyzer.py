"""
GitHub Analyzer — Analyze any GitHub profile
"""

import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

BASE_URL = "https://api.github.com"


# ── API Functions ────────────────────────────────────────────

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


def get_languages(repos: list) -> dict:
    languages = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))


def get_top_repos(repos: list, n=3) -> list:
    return sorted(repos, key=lambda x: x["stargazers_count"], reverse=True)[:n]


# ── Score Functions ──────────────────────────────────────────

def calculate_profile_score(user: dict, repos: list, languages: dict, commit_data: dict) -> int:
    score = 0

    if user.get("bio"):             score += 10
    if user.get("avatar_url"):      score += 5
    if user.get("blog"):            score += 10
    if user.get("location"):        score += 5

    repos_count = user.get("public_repos", 0)
    if repos_count >= 10:           score += 15
    elif repos_count >= 5:          score += 10
    elif repos_count >= 2:          score += 5

    followers = user.get("followers", 0)
    if followers >= 50:             score += 10
    elif followers >= 10:           score += 7
    elif followers >= 1:            score += 3

    if len(languages) >= 4:         score += 10
    elif len(languages) >= 2:       score += 5

    total_stars = sum(r["stargazers_count"] for r in repos)
    if total_stars >= 20:           score += 15
    elif total_stars >= 5:          score += 10
    elif total_stars >= 1:          score += 5

    commits = commit_data.get("total_commits", 0)
    if commits >= 200:              score += 15
    elif commits >= 100:            score += 10
    elif commits >= 50:             score += 7
    elif commits >= 10:             score += 4

    if commit_data.get("active_repos", 0) >= 3:
        score += 5

    return min(score, 100)


def get_score_color(score: int) -> str:
    if score >= 80:   return "green"
    elif score >= 60: return "yellow"
    elif score >= 40: return "orange3"
    else:             return "red"


def get_score_label(score: int) -> str:
    if score >= 80:   return "Excellent"
    elif score >= 60: return "Good"
    elif score >= 40: return "Average"
    else:             return "Needs Work"


def _get_activity_rating(commits: int) -> str:
    if commits >= 200:   return "[green]🔥 Very Active — Keep it up![/green]"
    elif commits >= 100: return "[yellow]👍 Active — Good consistency![/yellow]"
    elif commits >= 50:  return "[orange3]📈 Moderate — Try to commit more often![/orange3]"
    elif commits >= 10:  return "[red]⚠️  Low Activity — Commit every day![/red]"
    else:                return "[red]😴 Inactive — Start building![/red]"


def _get_recommendations(user, repos, languages, commit_data) -> str:
    tips = []

    if user.get("public_repos", 0) < 5:
        tips.append("Build more projects — aim for at least 5 public repos")

    if not user.get("bio"):
        tips.append("Add a bio to your GitHub profile")

    if not user.get("blog"):
        tips.append("Add your portfolio website link")

    if not user.get("location"):
        tips.append("Add your location to your profile")

    if commit_data.get("total_commits", 0) < 50:
        tips.append("Commit more often — daily commits build great habits")

    if "JavaScript" not in languages and "TypeScript" not in languages:
        tips.append("Consider learning JavaScript to expand into web development")

    if len(languages) < 3:
        tips.append("Try learning more languages to diversify your skills")

    if not tips:
        tips.append("Great profile! Keep building and contributing!")

    return "\n".join(tips)


# ── PDF Export ───────────────────────────────────────────────

def export_pdf(username: str, user: dict, repos: list, languages: dict, commit_data: dict, score: int):
    pdf = FPDF()
    pdf.set_doc_option("core_fonts_encoding", "windows-1252")
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    NX = XPos.LMARGIN
    NY = YPos.NEXT

    # ── Header ──
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(0, 120, 200)
    pdf.cell(0, 12, "GitHub Profile Analysis Report", new_x=NX, new_y=NY, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x=NX, new_y=NY, align="C")
    pdf.ln(8)

    # ── Profile ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Profile", new_x=NX, new_y=NY)
    pdf.set_draw_color(0, 120, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, user.get("name") or username, new_x=NX, new_y=NY)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, user.get("bio") or "No bio", new_x=NX, new_y=NY)
    pdf.ln(4)

    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Location   : {user.get('location') or 'Not specified'}", new_x=NX, new_y=NY)
    pdf.cell(0, 7, f"Website    : {user.get('blog') or 'Not specified'}", new_x=NX, new_y=NY)
    pdf.cell(0, 7, f"Followers  : {user.get('followers', 0)}", new_x=NX, new_y=NY)
    pdf.cell(0, 7, f"Following  : {user.get('following', 0)}", new_x=NX, new_y=NY)
    pdf.cell(0, 7, f"Public Repos: {user.get('public_repos', 0)}", new_x=NX, new_y=NY)
    pdf.ln(8)

    # ── Score ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Profile Score", new_x=NX, new_y=NY)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 28)
    if score >= 80:        pdf.set_text_color(0, 150, 0)
    elif score >= 60:      pdf.set_text_color(200, 150, 0)
    else:                  pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 14, f"{score}/100  -  {get_score_label(score)}", new_x=NX, new_y=NY)
    pdf.ln(2)

    # score bar
    pdf.set_fill_color(220, 220, 220)
    pdf.rect(20, pdf.get_y(), 170, 8, "F")
    if score >= 80:        pdf.set_fill_color(0, 150, 0)
    elif score >= 60:      pdf.set_fill_color(200, 150, 0)
    else:                  pdf.set_fill_color(200, 0, 0)
    pdf.rect(20, pdf.get_y(), 170 * score / 100, 8, "F")
    pdf.ln(16)

    # ── Commit Activity ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Commit Activity", new_x=NX, new_y=NY)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Total Commits : {commit_data['total_commits']}", new_x=NX, new_y=NY)
    pdf.cell(0, 7, f"Active Repos  : {commit_data['active_repos']}", new_x=NX, new_y=NY)
    pdf.ln(8)

    # ── Languages ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Most Used Languages", new_x=NX, new_y=NY)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    total = sum(languages.values())
    for lang, count in list(languages.items())[:6]:
        percent = round((count / total) * 100)
        pdf.cell(0, 7, f"{lang}  -  {count} repos  ({percent}%)", new_x=NX, new_y=NY)
    pdf.ln(8)

    # ── Top Repos ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Top Repositories", new_x=NX, new_y=NY)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    top_repos = get_top_repos(repos)
    for repo in top_repos:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, repo["name"], new_x=NX, new_y=NY)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, f"  Stars: {repo['stargazers_count']}  Forks: {repo['forks_count']}  Language: {repo.get('language') or 'N/A'}", new_x=NX, new_y=NY)
        desc = (repo.get("description") or "No description")[:80]
        pdf.cell(0, 6, f"  {desc}", new_x=NX, new_y=NY)
        pdf.ln(2)
    pdf.ln(4)

    # ── Recommendations ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Recommendations", new_x=NX, new_y=NY)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    tips = _get_recommendations(user, repos, languages, commit_data)
    for tip in tips.split("\n"):
        pdf.cell(0, 7, f"- {tip.strip()}", new_x=NX, new_y=NY)

    # ── Footer ──
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Generated by GitHub Analyzer  |  github.com/PushpaSaysHi/github-analyzer", new_x=NX, new_y=NY, align="C")

    filename = f"{username}_github_report.pdf"
    pdf.output(filename)
    return filename


# ── Analyze ──────────────────────────────────────────────────

def analyze(username: str):
    console.print(f"\n[dim]🔍 Analyzing [cyan]{username}[/cyan]... please wait[/dim]\n")

    user  = get_user(username)
    if not user:
        return
    repos = get_repos(username)

    console.print("[dim]📊 Fetching commit activity...[/dim]")
    commit_data = get_commit_activity(username, repos)
    languages   = get_languages(repos)
    score       = calculate_profile_score(user, repos, languages, commit_data)
    score_color = get_score_color(score)
    score_label = get_score_label(score)

    # ── Profile ──
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

    # ── Score ──
    console.print(Panel(
        f"[bold {score_color}]{score}/100[/bold {score_color}]  {score_label}\n\n"
        f"[dim]{'█' * (score // 5)}{'░' * (20 - score // 5)}[/dim]  [{score_color}]{score}%[/{score_color}]",
        title="🏆 Profile Score",
        border_style=score_color
    ))

    # ── Commit Activity ──
    console.print(Panel(
        f"📝 Total commits: [cyan]{commit_data['total_commits']}[/cyan]\n"
        f"📁 Active repos : [green]{commit_data['active_repos']}[/green]\n\n"
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

    # ── Export PDF ──
    export = input("\n💾 Export as PDF? (yes/no): ").strip().lower()
    if export == "yes":
        console.print("[dim]📄 Generating PDF...[/dim]")
        filename = export_pdf(username, user, repos, languages, commit_data, score)
        console.print(f"\n[green]✅ Report saved as [bold]{filename}[/bold][/green]\n")


# ── Main ─────────────────────────────────────────────────────

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