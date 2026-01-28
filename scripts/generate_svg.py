import json

WIDTH = 800
HEIGHT = 420
BG = "#0d1117"
CARD = "#161b22"
TEXT = "#c9d1d9"
ACCENT = "#58a6ff"
BAR_BG = "#30363d"

with open("stats.json") as f:
    data = json.load(f)

profile = data["profile"]
languages = sorted(data["languages_percent"].items(), key=lambda x: x[1], reverse=True)[:5]
repos = data["top_repositories"]

svg = f'''<svg width="{WIDTH}" height="{HEIGHT}" xmlns="http://www.w3.org/2000/svg">
<style>
.title {{ font: bold 22px sans-serif; fill: {ACCENT}; }}
.text {{ font: 14px sans-serif; fill: {TEXT}; }}
.small {{ font: 12px sans-serif; fill: #8b949e; }}
</style>

<rect width="100%" height="100%" fill="{BG}" rx="15"/>

<!-- Title -->
<text x="30" y="40" class="title">Bryan's GitHub Dashboard</text>
<text x="30" y="65" class="small">Auto-generated stats</text>

<!-- Profile Stats -->
<text x="30" y="110" class="text">Followers: {profile['followers']}</text>
<text x="30" y="135" class="text">Public Repos: {profile['public_repos']}</text>
<text x="30" y="160" class="text">Stars Earned: ⭐ {profile['stars_total']}</text>
<text x="30" y="185" class="text">Forks: 🍴 {profile['forks_total']}</text>
<text x="30" y="210" class="text">Contributions (1y): 🔥 {profile['contributions_last_year']}</text>
'''

# Language Bars
y = 250
svg += f'<text x="30" y="{y}" class="title" font-size="18">Top Languages</text>'
y += 20

for lang, pct in languages:
    bar_width = pct * 3  # scale %
    y += 25
    svg += f'''
    <text x="30" y="{y}" class="text">{lang} ({pct}%)</text>
    <rect x="200" y="{y-12}" width="300" height="10" fill="{BAR_BG}" rx="5"/>
    <rect x="200" y="{y-12}" width="{bar_width}" height="10" fill="{ACCENT}" rx="5"/>
    '''

# Top Repos
y += 40
svg += f'<text x="30" y="{y}" class="title" font-size="18">Top Repositories</text>'
for repo in repos:
    y += 22
    svg += f'<text x="30" y="{y}" class="text">{repo["name"]} ⭐ {repo["stars"]} | 🍴 {repo["forks"]}</text>'

svg += "</svg>"

with open("stats.svg", "w") as f:
    f.write(svg)

print("SVG generated!")
