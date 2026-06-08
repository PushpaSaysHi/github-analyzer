"""
compare.py — Compare two GitHub profiles
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from api import get_user, get_repos, get_commit_activity
from helpers import (
    get_languages, calculate_profile_score,
    get_score_label
)

console = Console()


def compare_profiles(username1: str, username2: str):
    console.print(f"\n[dim]🔍 Comparing [cyan]{username1}[/cyan] vs [cyan]{username2}[/cyan]...[/dim]\n")

    user1 = get_user(username1)
    user2 = get_user(username2)

    if not user1:
        console.print(f"[red]❌ User '{username1}' not found![/red]")
        return
    if not user2:
        console.print(f"[red]❌ User '{username2}' not found![/red]")
        return

    repos1 = get_repos(username1)
    repos2 = get_repos(username2)

    console.print("[dim]📊 Fetching commit activity for both users...[/dim]")
    commit1    = get_commit_activity(username1, repos1)
    commit2    = get_commit_activity(username2, repos2)
    languages1 = get_languages(repos1)
    languages2 = get_languages(repos2)
    score1     = calculate_profile_score(user1, repos1, languages1, commit1)
    score2     = calculate_profile_score(user2, repos2, languages2, commit2)

    def winner(a, b, u1, u2):
        if a > b:   return f"🏆 {u1}"
        elif b > a: return f"🏆 {u2}"
        else:       return "🤝 Tie"

    # ── Comparison Table ──
    table = Table(title=f"⚔️  {username1}  vs  {username2}", style="cyan")
    table.add_column("Category",    style="bold yellow")
    table.add_column(username1,     justify="center", style="cyan")
    table.add_column(username2,     justify="center", style="green")
    table.add_column("Winner",      justify="center", style="bold")

    total_stars1 = sum(r["stargazers_count"] for r in repos1)
    total_stars2 = sum(r["stargazers_count"] for r in repos2)

    table.add_row(
        "Profile Score",
        f"{score1}/100", f"{score2}/100",
        winner(score1, score2, username1, username2)
    )
    table.add_row(
        "Public Repos",
        str(user1.get("public_repos", 0)),
        str(user2.get("public_repos", 0)),
        winner(user1.get("public_repos", 0), user2.get("public_repos", 0), username1, username2)
    )
    table.add_row(
        "Followers",
        str(user1.get("followers", 0)),
        str(user2.get("followers", 0)),
        winner(user1.get("followers", 0), user2.get("followers", 0), username1, username2)
    )
    table.add_row(
        "Total Commits",
        str(commit1["total_commits"]),
        str(commit2["total_commits"]),
        winner(commit1["total_commits"], commit2["total_commits"], username1, username2)
    )
    table.add_row(
        "Languages Used",
        str(len(languages1)),
        str(len(languages2)),
        winner(len(languages1), len(languages2), username1, username2)
    )
    table.add_row(
        "Total Stars",
        str(total_stars1),
        str(total_stars2),
        winner(total_stars1, total_stars2, username1, username2)
    )

    console.print(table)

    # ── Overall Winner ──
    if score1 > score2:
        console.print(Panel(
            f"[bold green]🏆 {username1} wins with {score1} vs {score2}![/bold green]",
            border_style="green"
        ))
    elif score2 > score1:
        console.print(Panel(
            f"[bold green]🏆 {username2} wins with {score2} vs {score1}![/bold green]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold yellow]🤝 It's a tie! Both scored {score1}/100[/bold yellow]",
            border_style="yellow"
        ))
