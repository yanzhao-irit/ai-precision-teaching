import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_step(title, command):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    result = subprocess.run(command, cwd=ROOT, shell=True)

    if result.returncode != 0:
        print(f"\nError during step: {title}")
        sys.exit(result.returncode)


def main():
    print("AI Teaching Prototype Demo")
    print("This script imports the graph and generates the diagnosis reports.")

    run_step(
        "Step 1 - Importing AI course knowledge graph into Neo4j",
        "python scripts/import_ai_demo.py"
    )

    run_step(
        "Step 2 - Running diagnosis and generating reports",
        "python scripts/diagnose_ai_demo.py"
    )

    print("\nDemo completed successfully.")
    print("Generated files:")
    print("- outputs/ai_diagnosis_results.csv")
    print("- outputs/reports/student_S001.md")
    print("- outputs/reports/class_summary.md")
    print("\nTo open the web demo, run:")
    print("python -m http.server 8000")
    print("Then open: http://localhost:8000/web/")


if __name__ == "__main__":
    main()