from datetime import date
import calendar

BIRTH_DATE = date(2003, 4, 25)


def calculate_age(birth_date: date) -> str:
    today = date.today()

    years = today.year - birth_date.year
    months = today.month - birth_date.month
    days = today.day - birth_date.day

    if days < 0:
        months -= 1
        prev_month = today.month - 1 or 12
        prev_year = today.year if today.month != 1 else today.year - 1
        days += calendar.monthrange(prev_year, prev_month)[1]

    if months < 0:
        years -= 1
        months += 12

    return f"{years} years, {months} months and {days} days"


def main():
    age_string = calculate_age(BIRTH_DATE)

    template_path = "assets/about-card-template.svg"
    output_path = "assets/about-card.svg"

    with open(template_path, "r", encoding="utf-8") as f:
        svg = f.read()

    svg = svg.replace("{{age}}", age_string)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Updated SVG with age: {age_string}")


if __name__ == "__main__":
    main()
