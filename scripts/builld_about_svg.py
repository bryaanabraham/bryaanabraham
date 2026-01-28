import json

with open("stats.json") as f:
    data = json.load(f)

age = data["age"]

with open("assets/about-card.svg") as f:
    svg = f.read()

svg = svg.replace("{{age}}", str(age))

with open("assets/about-card.svg", "w") as f:
    f.write(svg)

print("SVG built from template!")
