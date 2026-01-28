import json

with open("stats.json") as f:
    data = json.load(f)

profile = data["profile"]

with open("template.svg") as f:
    svg = f.read()

svg = svg.replace("{{followers}}", str(profile["followers"]))
svg = svg.replace("{{repos}}", str(profile["public_repos"]))
svg = svg.replace("{{stars}}", str(profile["stars_total"]))
svg = svg.replace("{{forks}}", str(profile["forks_total"]))
svg = svg.replace("{{contributions}}", str(profile["contributions_last_year"]))

with open("assets/stats.svg", "w") as f:
    f.write(svg)

print("SVG built from template!")
