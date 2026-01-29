import os
import requests
from datetime import datetime

GITHUB_TOKEN = os.environ["GH_TOKEN"]
USERNAME = os.environ["GH_USERNAME"]

query = """
query($username:String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
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
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

# SVG layout settings
cell_size = 12
gap = 3
left_pad = 40
top_pad = 30

svg_width = left_pad + len(weeks) * (cell_size + gap)
svg_height = top_pad + 7 * (cell_size + gap)

def get_color(count):
    if count == 0: return "#161b22"
    if count < 3: return "#0e4429"
    if count < 6: return "#006d32"
    if count < 10: return "#26a641"
    return "#39d353"

svg = [
    f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
    '<rect width="100%" height="100%" fill="#0d1117"/>',
    f'<text x="10" y="20" fill="#58a6ff" font-size="14">Custom Contributions</text>'
]

for w, week in enumerate(weeks):
    for d, day in enumerate(week["contributionDays"]):
        x = left_pad + w * (cell_size + gap)
        y = top_pad + d * (cell_size + gap)
        color = get_color(day["contributionCount"])

        svg.append(
            f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2"/>'
        )

svg.append("</svg>")

with open("output/contributions.svg", "w") as f:
    f.write("\n".join(svg))

print("SVG generated successfully")
