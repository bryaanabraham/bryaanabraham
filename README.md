<h2 align="left">Hi!👋🏼 My name is Bryan</h2>
<h4 align="left">Originally from Mumbai, I am currently pursuing a Bachelor's degree in Technology as a Computer Science and Engineering student at SRM KTR Chennai.</h4>
<h3 align="left">💫 About Me:</h3>
<h4>Passionate, curious, and diligent, I thrive on exploring new ideas and pushing technological boundaries. I love visualizing concepts and gaining hands-on experience in my fields of interest. In addition to my tech pursuits, I engage in intense physical activities like football and cycling, which are key parts of my routine.</h4>
<br>

![](https://github-readme-streak-stats.herokuapp.com/?user=bryaanabraham&theme=dark&hide_border=false)<br/>

### 🐍 Watch my contribution snake:
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/bryaanabraham/bryaanabraham/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/bryaanabraham/bryaanabraham/output/github-contribution-grid-snake.svg">
  <img alt="github contribution grid snake animation" src="https://raw.githubusercontent.com/bryaanabraham/bryaanabraham/output/github-contribution-grid-snake.svg">
</picture>

### 👨‍💻 Expertise 

```python

class TechStack:
    def __init__(self, technologies):
        self.technologies = technologies

    def __str__(self):
        return ", ".join(self.technologies)


class Skill:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __str__(self):
        return f"{self.name} ({self.level})"


class Project:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description}"


class Education:
    def __init__(self, degree, institution, duration, score):
        self.degree = degree
        self.institution = institution
        self.duration = duration
        self.score = score

    def __str__(self):
        return f"{self.degree} at {self.institution} ({self.duration}) - {self.score}"


class Expertise:
    def __init__(self, name, tech_stack, skills, projects, education):
        self.name = name
        self.tech_stack = tech_stack
        self.skills = skills
        self.projects = projects
        self.education = education

    def __str__(self):
        tech_stack_str = str(self.tech_stack)
        skills_str = ", ".join(str(skill) for skill in self.skills)
        projects_str = "\n".join(str(project) for project in self.projects)
        education_str = "\n".join(str(edu) for edu in self.education)
        
        return (f"Name: {self.name}\n"
                f"Tech Stack: {tech_stack_str}\n"
                f"Skills: {skills_str}\n"
                f"Projects:\n{projects_str}\n"
                f"Education:\n{education_str}")


tech_stack = TechStack([
    "Python", "C++", "Dart", "Flutter", "GitHub", "Adobe Audition", "Blender", "Arduino", "Raspberry Pi",
    "Adobe After Effects", "Jupyter Notebook", "Google Colab"
])

skills = [
    Skill("Image Processing", "Intermediate"),
    Skill("Machine Learning", "Intermediate"),
    Skill("Large Language Models", "Beginner"),
    Skill("AWS Cloud", "Foundational"),
    Skill("Python", "Intermediate"),
    Skill("C++", "Intermediate"),
    Skill("Flutter", "Foundational"),
]

projects = [
    Project("Wander Guardian (Vision)", "Dementia care using AI and IOT."),
    Project("Beyond The Pixels", "Detecting Originality and Assessing Product Condition using Digital Image Processing Techniques."),
    Project("6G enabled On-Road Safety using Gen AI", "Nokia Ideathon."),
    Project("Deep Fake Reversion", "Dalhousie University")
]

education = [
    Education("Bachelor's Degree in Technology", "SRM KTR Chennai", "2022 - Present", "CGPA: 9.45"),
    Education("12th Board", "Khar Education Society's Junior College of Engineering", "2020 - 2021", "Percentage: 95%"),
    Education("10th Board", "V. C. W. Arya Vidya Mandir", "2018 - 2019", "Percentage: 92.67%"),
]

expertise = Expertise("Bryan Abraham", tech_stack, skills, projects, education)

print(expertise)
