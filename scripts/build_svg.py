import json
from pathlib import Path

# ================= PATHS =================
JSON_PATH = Path("stats.json")
TEMPLATE_PATH = Path("assets/stats-template.svg")
OUTPUT_PATH = Path("assets/stats.svg")

# ================= LOAD DATA =================
with JSON_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

profile = data["profile"]
contrib = data["contributions"]
languages = data["languages_percent"]
repos = data["top_repositories"]

# ================= LOAD TEMPLATE =================
svg = TEMPLATE_PATH.read_text(encoding="utf-8")

# ================= HEADER =================
svg = svg.replace("{{username}}", profile["username"])

# ================= LANGUAGE COLOR SCHEME =================
def language_color(lang):
    return {
        "Python": "#4ade80",
        "Jupyter Notebook": "#60a5fa",
        "Cython": "#a78bfa",
    }.get(lang, "#64748b")


# ================= PROFILE BLOCK =================
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

# ================= CONTRIBUTIONS BLOCK =================
contrib_block = f"""
<text class="mono label" x="40" y="290">Last Year</text>
<text class="mono dots" x="220" y="290">......................</text>
<text class="mono val" x="500" y="290">{contrib['total_last_year']}</text>

<text class="mono label" x="40" y="320">Current Streak</text>
<text class="mono dots" x="220" y="320">......................</text>
<text class="mono val" x="500" y="320">{contrib['current_streak']}</text>

<text class="mono label" x="40" y="350">Longest Streak</text>
<text class="mono dots" x="220" y="350">......................</text>
<text class="mono val" x="500" y="350">{contrib['longest_streak']}</text>

<text class="mono label" x="40" y="380">Avg / Day</text>
<text class="mono dots" x="220" y="380">......................</text>
<text class="mono val" x="500" y="380">{contrib['average_per_day']}</text>
"""
svg = svg.replace("{{CONTRIB_BLOCK}}", contrib_block)

# ================= LANGUAGE BARS =================
def generate_language_bars(languages_dict):
    sorted_langs = sorted(languages_dict.items(), key=lambda x: x[1], reverse=True)
    y = 420
    parts = []

    for lang, pct in sorted_langs:
        if pct < 1:
            continue

        width = int(pct * 3)
        color = language_color(lang)

        parts.append(f"""
<text class="mono label" x="40" y="{y}">{lang}</text>
<rect class="barbg" x="220" y="{y-12}" width="260" height="12" rx="6"/>
<rect fill="{color}" x="220" y="{y-12}" width="{width}" height="12" rx="6"/>
<text class="mono val" x="500" y="{y}">{pct:.1f}%</text>
""")
        y += 30

    return "\n".join(parts)

svg = svg.replace("{{LANGUAGE_BARS}}", generate_language_bars(languages))

# ================= TOP REPOSITORIES =================
def generate_repos(repo_list):
    y = 140
    parts = []

    for repo in repo_list[:5]:
        parts.append(f"""
<text class="mono label" x="600" y="{y}">{repo['name']}</text>
<text class="mono muted" x="600" y="{y+20}">{repo['language']}</text>
<text class="mono val" x="600" y="{y+40}">★ {repo['stars']}   ⑂ {repo['forks']}</text>
""")
        y += 80

    return "\n".join(parts)

svg = svg.replace("{{TOP_REPOS}}", generate_repos(repos))

# ================= SAVE SVG =================
OUTPUT_PATH.write_text(svg, encoding="utf-8")
print("✅ Terminal-style stats SVG generated at assets/stats.svg")
