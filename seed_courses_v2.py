"""
Enrichit Neo4j avec :
- Propriétés sur SubChapter (content, summary, difficulty, duration, video_url, keywords)
- Nœuds Resource liés via HAS_RESOURCE
"""
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Bpa25072020!")

COURSES = {
    "Linear Equations": {
        "summary": "Solve equations of the form ax + b = 0.",
        "difficulty": "easy",
        "duration": 15,
        "video_url": "https://www.youtube.com/embed/Cye_KZSn_TY",
        "keywords": ["equation", "linear", "algebra"],
        "content": r"""# Linear Equations

A **linear equation** has the form:

$$ ax + b = 0 $$

where $a \neq 0$.

## Method
1. Isolate the term with $x$
2. Divide by the coefficient of $x$

## Example
Solve $2x + 4 = 0$:
- Subtract 4 → $2x = -4$
- Divide by 2 → $\boxed{x = -2}$
""",
        "resources": [
            {"title": "Khan Academy", "url": "https://www.khanacademy.org/math/algebra", "type": "article"},
        ],
    },
    "Quadratic Equations": {
        "summary": "Master the discriminant method for ax² + bx + c = 0.",
        "difficulty": "medium",
        "duration": 25,
        "video_url": "https://www.youtube.com/embed/IlFFZPNoK1Y",
        "keywords": ["quadratic", "discriminant", "polynomial"],
        "content": r"""# Quadratic Equations

General form:

$$ ax^2 + bx + c = 0,\quad a \neq 0 $$

## Discriminant

$$ \Delta = b^2 - 4ac $$

| Value of $\Delta$ | Solutions |
|---|---|
| $\Delta > 0$ | Two distinct real roots |
| $\Delta = 0$ | One double real root |
| $\Delta < 0$ | No real roots |

## Roots formula

$$ x = \frac{-b \pm \sqrt{\Delta}}{2a} $$
""",
        "resources": [
            {"title": "Math is Fun", "url": "https://www.mathsisfun.com/algebra/quadratic-equation.html", "type": "article"},
        ],
    },
    "Triangles": {
        "summary": "Properties, similarity and Pythagoras theorem.",
        "difficulty": "easy",
        "duration": 20,
        "video_url": "https://www.youtube.com/embed/AA6RfgP-AHU",
        "keywords": ["triangle", "pythagoras", "geometry"],
        "content": r"""# Triangles

## Pythagoras theorem
In a right triangle with legs $a$, $b$ and hypotenuse $c$:

$$ a^2 + b^2 = c^2 $$

## Sum of angles
$$ \alpha + \beta + \gamma = 180° $$
""",
        "resources": [
            {"title": "Pythagoras — Math is Fun", "url": "https://www.mathsisfun.com/pythagoras.html", "type": "article"},
        ],
    },
    "Circles": {
        "summary": "Circumference, area and circle theorems.",
        "difficulty": "medium",
        "duration": 20,
        "video_url": "",
        "keywords": ["circle", "radius", "geometry"],
        "content": r"""# Circles

- Circumference: $C = 2\pi r$
- Area: $A = \pi r^2$
""",
        "resources": [],
    },
}


def seed(tx):
    for sub_name, data in COURSES.items():
        tx.run("""
            MATCH (sc:SubChapter {name: $name})
            SET sc.content    = $content,
                sc.summary    = $summary,
                sc.difficulty = $difficulty,
                sc.duration   = $duration,
                sc.video_url  = $video_url,
                sc.keywords   = $keywords
        """, name=sub_name, **data)

        # purge old resources
        tx.run("""
            MATCH (sc:SubChapter {name:$name})-[r:HAS_RESOURCE]->(res:Resource)
            DETACH DELETE res
        """, name=sub_name)

        for res in data["resources"]:
            tx.run("""
                MATCH (sc:SubChapter {name:$name})
                CREATE (r:Resource {title:$title, url:$url, type:$type})
                CREATE (sc)-[:HAS_RESOURCE]->(r)
            """, name=sub_name, **res)


if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.execute_write(seed)
    print("✅ Courses enriched in Neo4j")
