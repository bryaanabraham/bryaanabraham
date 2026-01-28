import json
from pathlib import Path

JSON_PATH = Path("stats.json")
TEMPLATE_PATH = Path("assets/stats-template.svg")
OUTPUT_PATH = Path("assets/stats.svg")

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
profile = data["profile"]
contrib = data["contributions"]
languages = data["languages_percent"]
repos = data["top_repositories"]

svg = TEMPLATE_PATH.read_text(encoding="utf-8")
svg = svg.replace("{{username}}", profile["username"])

# ---------- PROFILE BLOCK ----------
profile_block = f"""
<text class="mono label" x="40" y="140">Followers</text>
<text class="mono dots" x="220" y="140">......................</text>
<text class="mono val" x="500" y="140">{profile['followers']}</text>

<text class="mono label" x="40" y="170">Public Repos</text>
<text class="mono dots" x="220" y="170">......................</text>
<text class="mono val" x="500" y="170">{profile['public_repos']}</text>

<text class="mono label" x="40" y="200">Stars</text>
<text class="mono dots" x="220" y="200">......................</text>
<text class="mono val" x="500" y="200">{profile['stars_total']}</text>

<text class="mono label" x="40" y="230">Forks</text>
<text class="mono dots" x="220" y="230">......................</text>
<text class="mono val" x="500" y="230">{profile['forks_total']}</text>
"""
svg = svg.replace("{{PROFILE_BLOCK}}", profile_block)

# ---------- CONTRIBUTIONS ----------
contrib_block = f"""
<text class="mono label" x="40" y="320">Last Year</text>
<text class="mono dots" x="220" y="320">......................</text>
<text class="mono val" x="500" y="320">{contrib['total_last_year']}</text>

<text class="mono label" x="40" y="350">Current Streak</text>
<text class="mono dots" x="220" y="350">......................</text>
<text class="mono val" x="500" y="350">{contrib['current_streak']}</text>

<text class="mono label" x="40" y="380">Longest Streak</text>
<text class="mono dots" x="220" y="380">......................</text>
<text class="mono val" x="500" y="380">{contrib['longest_streak']}</text>

<text class="mono label" x="40" y="410">Avg / Day</text>
<text class="mono dots" x="220" y="410">......................</text>
<text class="mono val" x="500" y="410">{contrib['average_per_day']}</text>
"""
svg = svg.replace("{{CONTRIB_BLOCK}}", contrib_block)

# ---------- LANGUAGE COLORS ----------
def lang_color(name):
    return {
        "Python": "#4ade80",
        "Jupyter Notebook": "#60a5fa",
        "Cython": "#a78bfa"
    }.get(name, "#64748b")

# ---------- LANGUAGE BARS ----------
y = 500
bars = []
for lang, pct in sorted(languages.items(), key=lambda x: x[1], reverse=True):
    if pct < 1:
        continue
    width = int(pct * 2.6)
    bars.append(f"""
<text class="mono label" x="40" y="{y}">{lang}</text>
<rect class="barbg" x="220" y="{y-12}" width="260" height="12" rx="6"/>
<rect fill="{lang_color(lang)}" x="220" y="{y-12}" width="{width}" height="12" rx="6"/>
<text class="mono val" x="500" y="{y}">{pct:.1f}%</text>
""")
    y += 30

svg = svg.replace("{{LANGUAGE_BARS}}", "\n".join(bars))

# ---------- TOP REPOS ----------
y = 135
repo_parts = []
for r in repos[:5]:
    repo_parts.append(f"""
<text class="mono label" x="620" y="{y}">{r['name']}</text>
<text class="mono muted" x="620" y="{y+20}">{r['language']}</text>
<text class="mono val" x="620" y="{y+40}">★ {r['stars']}   ⑂ {r['forks']}</text>
""")
    y += 75

svg = svg.replace("{{TOP_REPOS}}", "\n".join(repo_parts))

OUTPUT_PATH.write_text(svg, encoding="utf-8")
print("✅ Exact-layout SVG generated")
