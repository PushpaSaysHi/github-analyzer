"""
search.py — Search GitHub users by language
"""

from rich.console import Console
from rich.table import Table

from api import search_users_by_language

console = Console()


def search_by_language(language: str):
    console.print(f"\n[dim]🔍 Searching top [cyan]{language}[/cyan] developers on GitHub...[/dim]\n")

    users = search_users_by_language(language)

    if not users:
        console.print(f"[red]❌ No users found for language: {language}[/red]")
        return

    table = Table(title=f"🔍 Top {language} Developers on GitHub", style="cyan")
    table.add_column("No.",      style="dim",       justify="center")
    table.add_column("Username", style="bold cyan")
    table.add_column("Profile",  style="dim")

    for i, user in enumerate(users, 1):
        table.add_row(
            str(i),
            user["login"],
            f"github.com/{user['login']}"
        )

    console.print(table)
    console.print("[dim]💡 Tip: Copy a username and use option 1 to analyze their profile![/dim]\n")
