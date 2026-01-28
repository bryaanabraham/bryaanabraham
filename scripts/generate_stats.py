import os
import requests
from datetime import datetime

USERNAME = "BryanAbraham"
TOKEN = os.getenv("GH_TOKEN")

headers = {"Authorization": f"Bearer {TOKEN}"}

# ------------------ FETCH USER + REPOS ------------------
user = requests.get(f"https://api.github.com/users/{USERNAME}", headers=headers).json()
repos = requests.get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100", headers=headers).json()

total_stars = sum(r["stargazers_count"] for r in repos)
total_forks = sum(r["forks_count"] for r in repos)

# ------------------ LANGUAGE STATS (BY BYTES) ------------------
language_bytes = {}

for repo in repos:
    langs = requests.get(repo["languages_url"], headers=headers).json()
    for lang, bytes_of_code in langs.items():
        language_bytes[lang] = language_bytes.get(lang, 0) + bytes_of_code

total_bytes = sum(language_bytes.values())
language_percent = {
    lang: round((count / total_bytes) * 100, 1)
    for lang, count in language_bytes.items()
} if total_bytes else {}

top_languages = sorted(language_percent.items(), key=lambda x: x[1], reverse=True)[:5]

# ------------------ COMMIT ACTIVITY ------------------
total_commits = 0
most_active_repo = ("None", 0)

for repo in repos:
    commits_url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits?per_page=100"
    commits = requests.get(commits_url, headers=headers).json()
    if isinstance(commits, list):
        commit_count = len(commits)
        total_commits += commit_count
        if commit_count > most_active_repo[1]:
            most_active_repo = (repo["name"], commit_count)

# ------------------ TOP REPOS ------------------
top_repos = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:5]

# ------------------ BUILD OUTPUT ------------------
content = f"""# 🚀 Bryan's Custom GitHub Stats

📅 Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## 📦 Profile Stats
- **Repositories:** {user['public_repos']}
- **Stars:** ⭐ {total_stars}
- **Forks:** 🍴 {total_forks}
- **Followers:** 👥 {user['followers']}

## 🧠 Most Used Languages
"""

if top_languages:
    for lang, pct in top_languages:
        content += f"- {lang}: {pct}%\n"
else:
    content += "No language data available yet.\n"

content += f"""
## 📈 Activity Insights
- **Recent Commits (sampled):** 🧾 {total_commits}
- **Most Active Repo:** 🔥 {most_active_repo[0]} ({most_active_repo[1]} commits)

## 🌟 Top Repositories
"""

for repo in top_repos:
    content += f"- **{repo['name']}** — ⭐ {repo['stargazers_count']} | 🍴 {repo['forks_count']}\n"

with open("stats.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Stats generated successfully!")
