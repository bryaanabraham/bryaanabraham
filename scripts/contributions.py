import os
import json
import requests
from datetime import datetime, timedelta

GITHUB_TOKEN = os.getenv("GH_TOKEN")
USERNAME = "bryaanabraham"

# ---------- DATE RANGE (PAST 40 DAYS) ----------
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=30)

query = """
query($username:String!, $from:DateTime!, $to:DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
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
    "https://api.github.com/graphql",
    json={"query": query, "variables": variables},
    headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
)

data = response.json()

if "errors" in data:
    print("GraphQL Errors:", data["errors"])
    raise SystemExit(1)

weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

daily_data = []
for week in weeks:
    for day in week["contributionDays"]:
        d = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if start_date <= d <= end_date:
            daily_data.append({"date": day["date"], "count": day["contributionCount"]})

daily_data = sorted(daily_data, key=lambda x: x["date"])

with open("assets/contributions.json", "w", encoding="utf-8") as f:
    json.dump(daily_data, f, indent=2)

# ---------- GRAPH PREP ----------
# ---------- GENERATE WIDER TERMINAL-STYLE SVG ----------

values = [d["count"] for d in daily_data]
labels = [datetime.strptime(d["date"], "%Y-%m-%d").strftime("%d %b") for d in daily_data]

if not values:
    values = [0]
    labels = ["No Data"]

max_val = max(values) if max(values) > 0 else 1
pixels_per_commit = 9   # visual scale factor
chart_height = max(180, min(max_val * pixels_per_commit, 520))


bar_width = 22
gap = 10
chart_height = 260
left_pad = 70
bottom_pad = 140
top_pad = 120

svg_width = 1100
top_pad = 120
bottom_pad = 140
svg_height = top_pad + chart_height + bottom_pad
bars_svg = []

for i, val in enumerate(values):
    bar_height = (val / max_val) * chart_height
    x = left_pad + i * (bar_width + gap)
    y = svg_height - bottom_pad - bar_height

    # Bar
    bars_svg.append(
        f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" rx="5" fill="#38bdf8"/>'
    )

    # Value above bar
    bars_svg.append(
        f'<text x="{x + bar_width/2}" y="{y - 8}" text-anchor="middle" class="mono val" font-size="13">{val}</text>'
    )

    # Date label below bar (rotated slightly for spacing)
    bars_svg.append(
        f'<text x="{x + bar_width/2}" y="{svg_height - 95}" text-anchor="middle" class="mono muted" font-size="12" transform="rotate(-45 {x + bar_width/2},{svg_height - 95})">{labels[i]}</text>'
    )

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
    .muted {{ fill:#94a3b8; }}
    .val {{ fill:#e5e7eb; }}
    .axis {{ stroke:#334155; stroke-width:1; }}
  </style>

  <rect class="bg" width="100%" height="100%"/>

  <!-- HEADER -->
  <text class="mono header" x="40" y="55">bryaanabraham@contributions ------------------------------------------------</text>

  <!-- AXIS LINE -->
  <line x1="60" y1="{svg_height - bottom_pad}" x2="{svg_width - 40}" y2="{svg_height - bottom_pad}" class="axis"/>

  {''.join(bars_svg)}

  <!-- FOOTER -->
  <text class="mono muted" x="40" y="{svg_height - 25}">
    Auto-generated via GitHub Actions • Updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
  </text>
</svg>
"""

with open("assets/contributions.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("Wider terminal-style SVG generated")
