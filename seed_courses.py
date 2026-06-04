from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Bpa25072020!")

# Exemple : associe un contenu Markdown à chaque sous-chapitre
COURSES = {
    "Linear Equations": """
# Linear Equations

A **linear equation** is an equation of the form `ax + b = 0`.

## Example
Solve `2x + 4 = 0`:
- Subtract 4 → `2x = -4`
- Divide by 2 → `x = -2`

## Exercises
1. Solve `3x - 9 = 0`
2. Solve `5x + 10 = 0`
""",
    "Quadratic Equations": """
# Quadratic Equations

Form: `ax² + bx + c = 0`

## Discriminant
`Δ = b² - 4ac`
- Δ > 0 → two solutions
- Δ = 0 → one solution
- Δ < 0 → no real solution
""",
    # ... ajoute autant de sous-chapitres que tu veux
}


def add_course(tx, sub_name, content):
    tx.run(
        """
        MATCH (sc:SubChapter {name:$name})
        SET sc.content = $content
        """,
        name=sub_name, content=content,
    )


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        for sub, content in COURSES.items():
            session.execute_write(add_course, sub, content)
            print(f"✅ {sub}")
print("🎉 Courses added")
