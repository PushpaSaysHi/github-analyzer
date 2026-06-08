"""
analyzer.py — Analyze a single GitHub profile
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from api import get_user, get_repos, get_commit_activity
from helpers import (
    get_languages, get_top_repos, calculate_profile_score,
    get_score_color, get_score_label, get_activity_rating,
    get_recommendations
)
from pdf_export import export_pdf

console = Console()


def analyze(username: str):
    console.print(f"\n[dim]🔍 Analyzing [cyan]{username}[/cyan]... please wait[/dim]\n")

    user = get_user(username)
    if not user:
        console.print(f"[red]❌ User '{username}' not found![/red]")
        return

    repos       = get_repos(username)
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
        + get_activity_rating(commit_data['total_commits']),
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
        get_recommendations(user, repos, languages, commit_data),
        title="💡 Recommendations",
        border_style="yellow"
    ))

    # ── Export PDF ──
    export = input("\n💾 Export as PDF? (yes/no): ").strip().lower()
    if export == "yes":
        console.print("[dim]📄 Generating PDF...[/dim]")
        filename = export_pdf(username, user, repos, languages, commit_data, score)
        console.print(f"\n[green]✅ Report saved as [bold]{filename}[/bold][/green]\n")
