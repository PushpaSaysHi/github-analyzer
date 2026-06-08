"""
main.py — Entry point for GitHub Analyzer
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from analyzer import analyze
from compare import compare_profiles
from search import search_by_language

console = Console()


def main():
    console.print(Panel(
        Text("🔍 GitHub Profile Analyzer", justify="center", style="bold cyan"),
        border_style="cyan"
    ))

    while True:
        console.print("\n  [bold]What do you want to do?[/bold]")
        console.print("  [yellow]1.[/yellow] Analyze a profile")
        console.print("  [yellow]2.[/yellow] Compare two profiles")
        console.print("  [yellow]3.[/yellow] Search by language")
        console.print("  [yellow]4.[/yellow] Quit")

        choice = input("\n  Enter choice (1-4): ").strip()

        if choice == "1":
            username = input("  Enter GitHub username: ").strip()
            if username:
                analyze(username)

        elif choice == "2":
            username1 = input("  Enter first username: ").strip()
            username2 = input("  Enter second username: ").strip()
            if username1 and username2:
                compare_profiles(username1, username2)

        elif choice == "3":
            language = input("  Enter language (e.g. Python, JavaScript): ").strip()
            if language:
                search_by_language(language)

        elif choice == "4":
            console.print("\n[cyan]👋 Goodbye![/cyan]\n")
            break

        else:
            console.print("[red]❌ Invalid choice.[/red]")


if __name__ == "__main__":
    main()
