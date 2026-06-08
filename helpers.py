"""
helpers.py — Score calculation, labels and recommendations
"""


def get_languages(repos: list) -> dict:
    """Count language usage across all repos."""
    languages = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))


def get_top_repos(repos: list, n=3) -> list:
    """Get top repos by stars."""
    return sorted(repos, key=lambda x: x["stargazers_count"], reverse=True)[:n]


def calculate_profile_score(user: dict, repos: list, languages: dict, commit_data: dict) -> int:
    """Calculate a profile score out of 100."""
    score = 0

    if user.get("bio"):         score += 10
    if user.get("avatar_url"):  score += 5
    if user.get("blog"):        score += 10
    if user.get("location"):    score += 5

    repos_count = user.get("public_repos", 0)
    if repos_count >= 10:       score += 15
    elif repos_count >= 5:      score += 10
    elif repos_count >= 2:      score += 5

    followers = user.get("followers", 0)
    if followers >= 50:         score += 10
    elif followers >= 10:       score += 7
    elif followers >= 1:        score += 3

    if len(languages) >= 4:     score += 10
    elif len(languages) >= 2:   score += 5

    total_stars = sum(r["stargazers_count"] for r in repos)
    if total_stars >= 20:       score += 15
    elif total_stars >= 5:      score += 10
    elif total_stars >= 1:      score += 5

    commits = commit_data.get("total_commits", 0)
    if commits >= 200:          score += 15
    elif commits >= 100:        score += 10
    elif commits >= 50:         score += 7
    elif commits >= 10:         score += 4

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


def get_activity_rating(commits: int) -> str:
    if commits >= 200:   return "[green]🔥 Very Active — Keep it up![/green]"
    elif commits >= 100: return "[yellow]👍 Active — Good consistency![/yellow]"
    elif commits >= 50:  return "[orange3]📈 Moderate — Try to commit more often![/orange3]"
    elif commits >= 10:  return "[red]⚠️  Low Activity — Commit every day![/red]"
    else:                return "[red]😴 Inactive — Start building![/red]"


def get_recommendations(user: dict, repos: list, languages: dict, commit_data: dict) -> str:
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
