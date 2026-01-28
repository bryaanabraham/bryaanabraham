import os
import requests
import json
from datetime import datetime

USERNAME = "bryaanabraham"
TOKEN = os.getenv("GH_TOKEN")

headers = {"Authorization": f"Bearer {TOKEN}"}

# ---------------- REST: USER + REPOS ----------------
user = requests.get(f"https://api.github.com/users/{USERNAME}", headers=headers).json()
repos = requests.get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100", headers=headers).json()

total_stars = sum(r["stargazers_count"] for r in repos)
total_forks = sum(r["forks_count"] for r in repos)

# ---------------- LANGUAGES (BY BYTES) ----------------
language_bytes = {}
for repo in repos:
    langs = requests.get(repo["languages_url"], headers=headers).json()
    for lang, bytes_of_code in langs.items():
        language_bytes[lang] = language_bytes.get(lang, 0) + bytes_of_code

total_bytes = sum(language_bytes.values())
language_percent = {
    lang: round((count / total_bytes) * 100, 2)
    for lang, count in language_bytes.items()
} if total_bytes else {}

# ---------------- GRAPHQL: CONTRIBUTIONS ----------------
graphql_query = {
    "query": f"""
    {{
      user(login: "{USERNAME}") {{
        contributionsCollection {{
          contributionCalendar {{
            totalContributions
          }}
        }}
      }}
    }}
    """
}

gql = requests.post("https://api.github.com/graphql", json=graphql_query, headers=headers).json()
contributions = gql["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

# ---------------- TOP REPOS ----------------
top_repos = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:5]
top_repo_data = [
    {
        "name": r["name"],
        "stars": r["stargazers_count"],
        "forks": r["forks_count"],
        "language": r["language"],
    }
    for r in top_repos
]

# ---------------- BUILD JSON ----------------
data = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "profile": {
        "username": USERNAME,
        "followers": user["followers"],
        "public_repos": user["public_repos"],
        "stars_total": total_stars,
        "forks_total": total_forks,
        "contributions_last_year": contributions
    },
    "languages_percent": language_percent,
    "top_repositories": top_repo_data
}

with open("stats.json", "w") as f:
    json.dump(data, f, indent=2)

print("Stats JSON generated.")
