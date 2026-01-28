import os
import requests
from datetime import datetime, timedelta

USERNAME = "BryanAbraham"
TOKEN = os.getenv("GH_TOKEN")

headers = {"Authorization": f"Bearer {TOKEN}"}

# ------------------ BASIC USER DATA ------------------
user_data = requests.get(f"https://api.github.com/users/{USERNAME}", headers=headers).json()
repos_data = requests.get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100", headers=headers).json()

total_stars = sum(r["stargazers_count"] for r in repos_data)
total_forks = sum(r["forks_count"] for r in repos_data)

# ------------------ TOP REPOS ------------------
top_repos = sorted(repos_data, key=lambda r: r["stargazers_count"], reverse=True)[:5]

# ------------------ LANGUAGE PERCENTAGES ------------------
language_bytes = {}

for repo in repos_data:
    langs_url = repo["languages_url"]
    langs = requests.get(langs_url, headers=headers).json()
    for lang, bytes_of_code in langs.items():
        language_bytes[lang] = language_bytes.get(lang, 0) + bytes_of_code

total_bytes = sum(language_bytes.values())
language_percent = {
    lang: round((count / total_bytes) * 100, 1)
    for lang, count in language_bytes.items()
}

top_languages = sorted(language_percent.items(), key=lambda x: x[1], reverse=True)[:5]

# ------------------ CONTRIBUTIONS VIA GRAPHQL ------------------
graphql_query = {
    "query": f"""
    {{
      user(login: "{USERNAME}") {{
        contributionsCollection {{
          contributionCalendar {{
            totalContributions
            weeks {{
              contributionDays {{
                date
                contributionCount
              }}
            }}
          }}
        }}
      }}
    }}
    """
}

gql_response = requests.post(
    "https://api.github.com/graphql",
    json=graphql_query,
    headers=headers
).json()

weeks = gql_response["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

daily_counts = []
for week in weeks:
    for day in week["contributionDays"]:
        daily_counts.append(day["contributionCount"])

total_contributions = sum(daily_counts)
avg_daily = round(total_contributions / len(daily_counts), 2)

# ---- Streak Calculation ----
current_streak = 0
longest_streak = 0
temp_streak = 0

for count in daily_counts:
    if count > 0:
        temp_streak += 1
        longest_streak = max(longest_streak, temp_streak)
    else:
        temp_streak = 0

# Current streak from end
for count in reversed(daily_counts):
    if count > 0:
        current_streak += 1
    else:
        break

# ------------------ BUILD OUTPUT ------------------
content = f"""# 🚀 Bryan's Custom GitHub Stats

📅 Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## 📦 Profile Stats
- **Repositories:** {user_data['public_repos']}
- **Stars:** ⭐ {total_stars}
- **Forks:** 🍴 {total_forks}
- **Followers:** 👥 {user_data['followers']}

## 🧠 Most Used Languages
"""

for lang, pct in top_languages:
    content += f"- {lang}: {pct}%\n"

content += f"""
## 📈 Contributions
- **Total Contributions:** {total_contributions}
- **Current Streak:** 🔥 {current_streak} days
- **Longest Streak:** 🏆 {longest_streak} days
- **Average Daily:** 📊 {avg_daily}

## 🌟 Top Repositories
"""

for repo in top_repos:
    content += f"- **{repo['name']}** — ⭐ {repo['stargazers_count']} | 🍴 {repo['forks_count']}\n"

with open("stats.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Advanced stats generated!")
