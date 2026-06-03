import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.kg.import_ai_kg import import_ai_kg

if __name__ == "__main__":
    import_ai_kg(reset=True)
