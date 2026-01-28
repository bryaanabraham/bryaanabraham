import os
import requests
from datetime import datetime

USERNAME = "BryanAbraham"
TOKEN = os.getenv("GH_TOKEN")

headers = {"Authorization": f"Bearer {TOKEN}"}

# Get user info
user_url = f"https://api.github.com/users/{USERNAME}"
repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

user_data = requests.get(user_url, headers=headers).json()
repos_data = requests.get(repos_url, headers=headers).json()

total_stars = sum(repo["stargazers_count"] for repo in repos_data)
total_forks = sum(repo["forks_count"] for repo in repos_data)

languages = {}
for repo in repos_data:
    if repo["language"]:
        languages[repo["language"]] = languages.get(repo["language"], 0) + 1

top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]

# Build custom markdown
content = f"""# 🚀 Bryan's Custom GitHub Stats

📅 Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## 👤 Profile
- **Followers:** {user_data['followers']}
- **Public Repos:** {user_data['public_repos']}
- **Total Stars Earned:** ⭐ {total_stars}
- **Total Forks:** 🍴 {total_forks}

## 🧠 Top Languages
"""

for lang, count in top_languages:
    content += f"- {lang}: {count} repos\n"

with open("stats.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Stats file generated!")
