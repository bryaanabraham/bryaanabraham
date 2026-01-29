import os
import requests
from collections import defaultdict
from datetime import datetime

GITHUB_TOKEN = os.environ["GH_TOKEN"]
USERNAME = os.environ["GH_USERNAME"]

query = """
query($username:String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"username": USERNAME}},
    headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
)

data = response.json()

if "errors" in data:
    print("GraphQL Errors:", data["errors"])
    raise SystemExit(1)

weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

# -------- GROUP BY MONTH --------
monthly = defaultdict(int)

for week in weeks:
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        key = date.strftime("%b %Y")  # e.g. Jan 2026
        monthly[key] += day["contributionCount"]

months = list(monthly.keys())
values = list(monthly.values())

max_val = max(values) if values else 1

# -------- SVG BAR GRAPH SETTINGS --------
bar_width = 28
gap = 18
chart_height = 260
left_pad = 80
bottom_pad = 120
top_pad = 120

svg_width = left_pad + len(values) * (bar_width + gap) + 80
svg_height = 650

bars_svg = []

for i, val in enumerate(values):
    bar_height = (val / max_val) * chart_height
    x = left_pad + i * (bar_width + gap)
    y = svg_height - bottom_pad - bar_height

    bars_svg.append(f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" rx="6" fill="#38bdf8"/>')
    bars_svg.append(f'<text x="{x + bar_width/2}" y="{svg_height - 90}" text-anchor="middle" class="mono muted">{months[i]}</text>')
    bars_svg.append(f'<text x="{x + bar_width/2}" y="{y - 8}" text-anchor="middle" class="mono val">{val}</text>')

# -------- FULL SVG --------
svg = f"""<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0a0f1f"/>
      <stop offset="100%" stop-color="#0b1220"/>
    </linearGradient>
  </defs>

  <style>
    .bg {{ fill:url(#bgGrad); }}
    .mono {{ font-family: "JetBrains Mono","Fira Code","Cascadia Mono",Menlo,Consolas,monospace; }}
    .header {{ fill:#7dd3fc; font-size:22px; }}
    .section {{ fill:#38bdf8; font-size:18px; }}
    .muted {{ fill:#94a3b8; font-size:14px; }}
    .val {{ fill:#e5e7eb; font-size:14px; }}
  </style>

  <rect class="bg" width="100%" height="100%"/>

  <text class="mono header" x="40" y="60">{USERNAME}@github → contribution.analytics</text>
  <text class="mono section" x="40" y="100">Monthly Commit Activity</text>

  {''.join(bars_svg)}

  <text class="mono muted" x="40" y="{svg_height - 30}">
    Auto-generated via GitHub Actions • Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
  </text>
</svg>
"""

os.makedirs("output", exist_ok=True)
with open("assets/contributions.svg", "w") as f:
    f.write(svg)

print("Bar graph SVG generated")
