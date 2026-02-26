import os
import json
import requests
from datetime import datetime, timedelta

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
import os

GITHUB_TOKEN = os.getenv("GH_TOKEN")
USERNAME = "bryaanabraham"

GRAPHQL_URL = "https://api.github.com/graphql"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

# ---------------------------------------------------
# DATE RANGE
# ---------------------------------------------------

end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=30)

# ---------------------------------------------------
# FETCH DAILY CONTRIBUTIONS
# ---------------------------------------------------

calendar_query = """
query($username:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$username) {
    contributionsCollection(from:$from,to:$to) {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

variables = {
    "username": USERNAME,
    "from": start_date.isoformat() + "T00:00:00Z",
    "to": end_date.isoformat() + "T23:59:59Z",
}

response = requests.post(
    GRAPHQL_URL,
    json={"query": calendar_query, "variables": variables},
    headers=headers,
)

data = response.json()

if "errors" in data:
    print(data["errors"])
    raise SystemExit(1)

weeks = data["data"]["user"]["contributionsCollection"][
    "contributionCalendar"
]["weeks"]

daily_data = []

for week in weeks:
    for day in week["contributionDays"]:
        d = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if start_date <= d <= end_date:
            daily_data.append({
                "date": day["date"],
                "count": day["contributionCount"]
            })

daily_data = sorted(daily_data, key=lambda x: x["date"])

# save json cache
os.makedirs("assets", exist_ok=True)

with open("assets/contributions.json", "w") as f:
    json.dump(daily_data, f, indent=2)

# ---------------------------------------------------
# FETCH REPO-WISE COMMITS PER DAY
# ---------------------------------------------------

def get_daily_repo_commits(date):

    query = """
    query($username:String!, $from:DateTime!, $to:DateTime!) {
      user(login:$username) {
        contributionsCollection(from:$from,to:$to) {
          commitContributionsByRepository {
            repository { name }
            contributions(first:100) {
              totalCount
            }
          }
        }
      }
    }
    """

    variables = {
        "username": USERNAME,
        "from": f"{date}T00:00:00Z",
        "to": f"{date}T23:59:59Z",
    }

    r = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=headers,
    )

    data = r.json()

    repos = {}

    try:
        items = data["data"]["user"]["contributionsCollection"][
            "commitContributionsByRepository"
        ]

        for repo in items:
            name = repo["repository"]["name"]
            count = repo["contributions"]["totalCount"]

            if count > 0:
                repos[name] = count

    except Exception:
        pass

    return repos


# ---------------------------------------------------
# BUILD TERMINAL LINES
# ---------------------------------------------------

lines = []
y = 135
line_gap = 32

latest_days = list(reversed(daily_data[-7:]))

total_commits = 0
repo_activity = {}

for day in latest_days:

    date = day["date"]
    total = day["count"]

    if total == 0:
        continue

    total_commits += total

    repos = get_daily_repo_commits(date)

    lines.append(f"""
<text class="mono label" x="40" y="{y}">
&gt; scanning commits :: {date}
</text>

<text class="mono dots" x="340" y="{y}">
....................
</text>

<text class="mono ok" x="560" y="{y}">
{total} commits
</text>
""")

    y += line_gap

    for repo, cnt in sorted(repos.items(),
                            key=lambda x: x[1],
                            reverse=True):

        repo_activity[repo] = repo_activity.get(repo, 0) + cnt

        lines.append(
            f'<text class="mono muted" x="80" y="{y}">{repo:<24} : {cnt}</text>'
        )
        y += 24

    y += 20


# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------

most_active_repo = (
    max(repo_activity, key=repo_activity.get) # type: ignore
    if repo_activity else "None"
)

lines.append(f"""
<text class="mono section" x="40" y="{y}">
System.Summary
</text>
""")

y += 30

lines.append(
    f'<text class="mono muted" x="80" y="{y}">Last 7 Days Total      : {total_commits}</text>'
)

y += 25

lines.append(
    f'<text class="mono muted" x="80" y="{y}">Most Active Repo       : {most_active_repo}</text>'
)

y += 50

# ---------------------------------------------------
# SVG GENERATION
# ---------------------------------------------------

svg_height = y + 120
ist = datetime.utcnow() + timedelta(hours=5, minutes=30)

svg = f"""
<svg width="850" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">

<style>
.bg {{ fill:#0b1220; }}
.mono {{ font-family:"JetBrains Mono","Fira Code","Cascadia Mono",Menlo,Consolas,monospace; font-size:16px; }}
.header {{ fill:#93c5fd; }}
.label {{ fill:#f59e0b; }}
.dots {{ fill:#64748b; }}
.section {{ fill:#38bdf8; }}
.muted {{ fill:#94a3b8; font-size:15px; }}
.ok {{ fill:#4ade80; }}
</style>

<rect class="bg" width="100%" height="100%"/>

<text class="mono header" x="40" y="50">
bryaanabraham@commits --------------------------------
</text>

<text class="mono section" x="40" y="95">
System.GitActivity
</text>

{''.join(lines)}

<rect x="40" y="{y}" width="10" height="18" fill="#4ade80">
<animate attributeName="opacity"
values="1;0;1"
dur="1s"
repeatCount="indefinite"/>
</rect>

<text class="mono muted" x="60" y="{y+15}">
awaiting next push...
</text>

<text class="mono muted" x="40" y="{svg_height-30}">
Auto-generated via GitHub Actions • Updated:
{ist.strftime("%Y-%m-%d %H:%M IST")}
</text>

</svg>
"""

with open("assets/contributions.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("✅ Terminal GitHub SVG generated")