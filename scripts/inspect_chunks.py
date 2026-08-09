import json
from pathlib import Path

from app.ingestion.chunker import chunk_directory

RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/processed/chunks.json")


def main() -> None:
    chunks = chunk_directory(RAW_DIR)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUT_PATH.write_text(
        json.dumps([c.__dict__ for c in chunks], indent=2),
        encoding="utf-8",
    )

    sizes = [c.token_estimate for c in chunks]
    print(f"files:  {len(list(RAW_DIR.glob('*.md')))}")
    print(f"chunks: {len(chunks)}")
    print(f"tokens: min={min(sizes)} max={max(sizes)} avg={sum(sizes)//len(sizes)}")
    print("\n--- 3 samples ---")
    for c in chunks[:3]:
        print(f"\n[{c.chunk_id}] ({c.token_estimate} tok) {c.section_title}")
        print(c.text[:200])


if __name__ == "__main__":
    main()