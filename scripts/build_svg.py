import json
from pathlib import Path

with open("stats.json", "r", encoding="utf-8") as f:
    data = json.load(f)

profile = data.get("profile", {})
languages = data.get("languages_percent", {})
repos = data.get("top_repositories", [])

template_path = Path("assets/stats-template.svg")
output_path = Path("assets/stats.svg")
svg = template_path.read_text(encoding="utf-8")

replacements = {
    "{{followers}}": profile.get("followers", 0),
    "{{repos}}": profile.get("public_repos", 0),
    "{{stars}}": profile.get("stars_total", 0),
    "{{forks}}": profile.get("forks_total", 0),
    "{{contributions}}": profile.get("contributions_last_year", 0),
}

for placeholder, value in replacements.items():
    svg = svg.replace(placeholder, str(value))

def generate_language_bars(languages_dict, start_x=0, start_y=40, bar_width=420, gap=45):
    # Sort by percentage descending
    sorted_langs = sorted(languages_dict.items(), key=lambda x: x[1], reverse=True)

    svg_parts = []
    y = start_y

    for lang, percent in sorted_langs:
        if percent < 0.5:  # skip tiny noise languages
            continue

        width = int((percent / 100) * bar_width)

        svg_parts.append(f'''
        <text class="mono val" x="{start_x}" y="{y}">{lang}</text>
        <rect class="barbg" x="{start_x}" y="{y+10}" width="{bar_width}" height="14" rx="7"/>
        <rect fill="#60a5fa" x="{start_x}" y="{y+10}" width="{width}" height="14" rx="7"/>
        <text class="mono muted" x="{start_x + bar_width + 10}" y="{y+22}">{percent:.2f}%</text>
        ''')
        y += gap

    return "\n".join(svg_parts)

language_svg = generate_language_bars(languages)
svg = svg.replace("{{LANGUAGE_BARS}}", language_svg)

def generate_repo_section(repos_list, start_x=0, start_y=40, gap=80):
    svg_parts = []
    y = start_y

    for repo in repos_list:
        name = repo["name"]
        stars = repo["stars"]
        forks = repo["forks"]
        lang = repo["language"]

        svg_parts.append(f'''
        <text class="mono val" x="{start_x}" y="{y}">{name}</text>
        <text class="mono muted" x="{start_x}" y="{y+20}">{lang}</text>
        <text class="mono val" x="{start_x}" y="{y+40}">★ {stars}   ⑂ {forks}</text>
        ''')
        y += gap

    return "\n".join(svg_parts)

repo_svg = generate_repo_section(repos)
svg = svg.replace("{{TOP_REPOS}}", repo_svg)

output_path.write_text(svg, encoding="utf-8")

print("✅ SVG with dynamic languages and repos built!")
