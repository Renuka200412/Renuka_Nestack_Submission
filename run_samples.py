
import json
import os
import sys
from pathlib import Path

import requests

BASE_URL = os.getenv("EXTRACTOR_BASE_URL", "http://127.0.0.1:8000")
ROOT = Path(__file__).resolve().parent

def main():
    samples = json.loads((ROOT / "sample_inputs.json").read_text(encoding="utf-8"))
    outputs = []
    for sample in samples:
        response = requests.post(
            f"{BASE_URL.rstrip('/')}/extract",
            json={"text": sample["text"]},
            timeout=120,
        )
        response.raise_for_status()
        outputs.append({"label": sample["label"], "result": response.json()})
        print(f"Completed: {sample['label']}")
    (ROOT / "results.json").write_text(
        json.dumps(outputs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(outputs)} results to {ROOT / 'results.json'}")

if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)
