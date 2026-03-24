"""
generate.py — Unified SVG generator.

1. Fetches GitHub stats via REST + GraphQL (replaces fetch_stats.py)
2. Computes age from birth date (replaces get_age.py)
3. Fills all placeholders into assets/template.svg (replaces build_svg.py)
4. Writes result to assets/final.svg
"""

import os
import calendar
import requests
import json
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# ── Config ─────────────────────────────────────────────────────────────────

USERNAME   = "bryaanabraham"
TOKEN      = os.getenv("GH_TOKEN")
BIRTH_DATE = date(2003, 4, 25)

TEMPLATE_PATH = Path("assets/template.svg")
OUTPUT_PATH   = Path("assets/final.svg")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ── Age ─────────────────────────────────────────────────────────────────────

def _format_duration(years: int, months: int, days: int) -> str:
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if not parts:
        return "0 days"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def calculate_age(birth_date: date) -> str:
    today = date.today()
    years  = today.year  - birth_date.year
    months = today.month - birth_date.month
    days   = today.day   - birth_date.day

    if days < 0:
        months -= 1
        prev_month = today.month - 1 or 12
        prev_year  = today.year if today.month != 1 else today.year - 1
        days += calendar.monthrange(prev_year, prev_month)[1]

    if months < 0:
        years  -= 1
        months += 12

    return _format_duration(years, months, days)

# ── GitHub stats ─────────────────────────────────────────────────────────────

def fetch_github_stats():
    user  = requests.get(
        f"https://api.github.com/users/{USERNAME}",
        headers=HEADERS, timeout=10
    ).json()
    repos = requests.get(
        f"https://api.github.com/users/{USERNAME}/repos?per_page=100",
        headers=HEADERS, timeout=10
    ).json()

    total_stars = sum(r["stargazers_count"] for r in repos)
    total_forks = sum(r["forks_count"]      for r in repos)

    # Languages
    language_bytes: dict[str, int] = {}
    for repo in repos:
        langs = requests.get(repo["languages_url"], headers=HEADERS, timeout=10).json()
        for lang, nbytes in langs.items():
            language_bytes[lang] = language_bytes.get(lang, 0) + nbytes

    total_bytes = sum(language_bytes.values())
    language_percent = (
        {lang: round((cnt / total_bytes) * 100, 2) for lang, cnt in language_bytes.items()}
        if total_bytes else {}
    )

    # Contributions (GraphQL)
    gql_query = {
        "query": f"""
        {{
          user(login: "{USERNAME}") {{
            contributionsCollection {{
              contributionCalendar {{
                totalContributions
                weeks {{
                  contributionDays {{
                    date
                    contributionCount
                  }}
                }}
              }}
            }}
          }}
        }}
        """
    }
    gql = requests.post(
        "https://api.github.com/graphql",
        json=gql_query, headers=HEADERS, timeout=10
    ).json()

    calendar_data = (
        gql["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    )
    total_contributions = calendar_data["totalContributions"]

    days_list = [
        day["contributionCount"]
        for week in calendar_data["weeks"]
        for day in week["contributionDays"]
    ]

    # Streaks
    current_streak = longest_streak = temp_streak = 0
    for count in days_list:
        if count > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
    for count in reversed(days_list):
        if count > 0:
            current_streak += 1
        else:
            break

    avg_daily = round(total_contributions / len(days_list), 2) if days_list else 0

    # Top repos
    top_repos = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:5]

    return {
        "profile": {
            "username":     USERNAME,
            "followers":    user["followers"],
            "public_repos": user["public_repos"],
            "stars_total":  total_stars,
            "forks_total":  total_forks,
        },
        "contributions": {
            "total_last_year": total_contributions,
            "current_streak":  current_streak,
            "longest_streak":  longest_streak,
            "average_per_day": avg_daily,
        },
        "languages_percent": language_percent,
        "top_repositories": [
            {
                "name":     r["name"],
                "stars":    r["stargazers_count"],
                "forks":    r["forks_count"],
                "language": r["language"],
            }
            for r in top_repos
        ],
    }

# ── SVG helpers ───────────────────────────────────────────────────────────────

def lang_color(name: str) -> str:
    return {
        "Python":           "#4ade80",
        "Jupyter Notebook": "#60a5fa",
        "Cython":           "#a78bfa",
    }.get(name, "#64748b")


def build_language_bars(languages: dict[str, float]) -> str:
    y = 500
    bars = []
    for lang, pct in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        if pct < 1:
            continue
        width = int(pct * 2.6)
        bars.append(
            f'<text class="mono label" x="40" y="{y}">{lang}</text>\n'
            f'<rect class="barbg" x="220" y="{y-12}" width="260" height="12" rx="6"/>\n'
            f'<rect fill="{lang_color(lang)}" x="220" y="{y-12}" width="{width}" height="12" rx="6"/>\n'
            f'<text class="mono val" x="500" y="{y}">{pct:.1f}%</text>'
        )
        y += 30
    return "\n".join(bars)


def build_top_repos(repos: list[dict]) -> str:
    y = 135
    parts = []
    for r in repos[:5]:
        parts.append(
            f'<text class="mono label" x="620" y="{y}">{r["name"]}</text>\n'
            f'<text class="mono muted" x="620" y="{y+20}">{r["language"]}</text>\n'
            f'<text class="mono val"   x="620" y="{y+40}">★ {r["stars"]}   ⑂ {r["forks"]}</text>'
        )
        y += 75
    return "\n".join(parts)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching GitHub stats …")
    data = fetch_github_stats()

    profile = data["profile"]
    contrib  = data["contributions"]
    langs    = data["languages_percent"]
    repos    = data["top_repositories"]

    print(f"Computing age for birth date {BIRTH_DATE} …")
    age_str = calculate_age(BIRTH_DATE)

    print("Reading template …")
    svg = TEMPLATE_PATH.read_text(encoding="utf-8")

    # ── Replace all placeholders ──────────────────────────────────────────

    # About card
    svg = svg.replace("{{age}}", age_str)

    # Stats — profile
    svg = svg.replace("{{followers}}",    str(profile["followers"]))
    svg = svg.replace("{{public_repos}}", str(profile["public_repos"]))
    svg = svg.replace("{{stars}}",  str(profile["stars_total"]))
    svg = svg.replace("{{forks}}",  str(profile["forks_total"]))

    # Stats — contributions
    svg = svg.replace("{{total_last_year}}", str(contrib["total_last_year"]))
    svg = svg.replace("{{current_streak}}",  str(contrib["current_streak"]))
    svg = svg.replace("{{longest_streak}}",  str(contrib["longest_streak"]))
    svg = svg.replace("{{avg_per_day}}",     str(contrib["average_per_day"]))

    # Stats — language bars
    svg = svg.replace("{{language_bars}}", build_language_bars(langs))

    # Stats — top repos
    svg = svg.replace("{{top_repos}}", build_top_repos(repos))

    print("Writing final.svg …")
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"✅  Done — {OUTPUT_PATH} generated (age: {age_str})")


if __name__ == "__main__":
    main()
