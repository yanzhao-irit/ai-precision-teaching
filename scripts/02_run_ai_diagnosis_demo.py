import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.diagnosis.ai_root_cause_diagnosis import run_diagnosis, save_csv, OUTPUT_DIR

if __name__ == "__main__":
    rows = run_diagnosis()
    out_path = OUTPUT_DIR / "ai_root_cause_diagnosis_demo.csv"
    save_csv(rows, out_path)
    print(f"Saved diagnosis to: {out_path}")
