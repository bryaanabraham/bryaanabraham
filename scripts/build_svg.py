import json
from pathlib import Path
from datetime import datetime

# ---------- Paths ----------
JSON_PATH = Path("stats.json")
TEMPLATE_PATH = Path("assets/stats-template.svg")
OUTPUT_PATH = Path("assets/stats.svg")

# ---------- Load Data ----------
with JSON_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)

profile = data["profile"]
contrib = data["contributions"]
languages = data["languages_percent"]
repos = data["top_repositories"]

# ---------- Load SVG Template ----------
svg = TEMPLATE_PATH.read_text(encoding="utf-8")

# =========================================================
# HEADER
# =========================================================
generated_date = data["generated_at"][:10]
svg = svg.replace("{{username}}", profile["username"])
svg = svg.replace("{{generated_date}}", generated_date)

# =========================================================
# PROFILE BLOCK
# =========================================================
profile_block = f"""
<text class="mono label" x="50" y="160">Followers</text>
<text class="mono val" x="250" y="160">{profile['followers']}</text>

<text class="mono label" x="50" y="185">Public Repos</text>
<text class="mono val" x="250" y="185">{profile['public_repos']}</text>

<text class="mono label" x="50" y="210">Stars</text>
<text class="mono val" x="250" y="210">{profile['stars_total']}</text>

<text class="mono label" x="50" y="235">Forks</text>
<text class="mono val" x="250" y="235">{profile['forks_total']}</text>
"""
svg = svg.replace("{{PROFILE_BLOCK}}", profile_block)

# =========================================================
# CONTRIBUTIONS BLOCK
# =========================================================
contrib_block = f"""
<text class="mono label" x="490" y="160">Last Year</text>
<text class="mono val" x="690" y="160">{contrib['total_last_year']}</text>

<text class="mono label" x="490" y="185">Current Streak</text>
<text class="mono val" x="690" y="185">{contrib['current_streak']}</text>

<text class="mono label" x="490" y="210">Longest Streak</text>
<text class="mono val" x="690" y="210">{contrib['longest_streak']}</text>

<text class="mono label" x="490" y="235">Avg / Day</text>
<text class="mono val" x="690" y="235">{contrib['average_per_day']}</text>
"""
svg = svg.replace("{{CONTRIB_BLOCK}}", contrib_block)

# =========================================================
# LANGUAGE COLORS (same theme as before)
# =========================================================
def language_color(lang):
    return {
        "Python": "#4ade80",            # green
        "Jupyter Notebook": "#60a5fa",  # blue
        "Cython": "#a78bfa",            # purple
    }.get(lang, "#64748b")              # fallback gray


# =========================================================
# LANGUAGE BARS
# =========================================================
def generate_language_bars(languages_dict):
    sorted_langs = sorted(languages_dict.items(), key=lambda x: x[1], reverse=True)
    y = 390
    parts = []

    for lang, pct in sorted_langs:
        if pct < 1:
            continue

        width = int(pct * 2.5)  # scale to fit card width
        color = language_color(lang)

        parts.append(f"""
<text class="mono val" x="50" y="{y}">{lang}</text>
<rect class="barbg" x="50" y="{y+8}" width="300" height="12" rx="6"/>
<rect fill="{color}" x="50" y="{y+8}" width="{width}" height="12" rx="6"/>
<text class="mono muted" x="360" y="{y+18}">{pct:.1f}%</text>
""")
        y += 35

    return "\n".join(parts)


svg = svg.replace("{{LANGUAGE_BARS}}", generate_language_bars(languages))

# =========================================================
# TOP REPOSITORIES
# =========================================================
def generate_repos(repo_list):
    y = 390
    parts = []

    for repo in repo_list[:4]:
        parts.append(f"""
<text class="mono val" x="490" y="{y}">{repo['name']}</text>
<text class="mono muted" x="490" y="{y+18}">{repo['language']}</text>
<text class="mono val" x="490" y="{y+36}">★ {repo['stars']}   ⑂ {repo['forks']}</text>
""")
        y += 55

    return "\n".join(parts)


svg = svg.replace("{{TOP_REPOS}}", generate_repos(repos))

# =========================================================
# SAVE OUTPUT
# =========================================================
OUTPUT_PATH.write_text(svg, encoding="utf-8")
print("✅ stats.svg generated successfully!")
