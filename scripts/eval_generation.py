import json
from pathlib import Path

import httpx

GOLDEN_SET = Path("data/eval/golden_set.jsonl")
API = "http://localhost:8000/query"


def main() -> None:
    cases = [
        json.loads(line)
        for line in GOLDEN_SET.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    correct_refusals = 0
    false_refusals = 0
    hallucinations = []

    for case in cases:
        r = httpx.post(API, json={"question": case["question"]}, timeout=90.0)
        answer = r.json()["answer"]
        refused = "INSUFFICIENT_CONTEXT" in answer

        if not case["answerable"]:
            if refused:
                correct_refusals += 1
            else:
                hallucinations.append((case["id"], case["question"], answer))
        elif refused:
            false_refusals += 1
            print(f"FALSE REFUSAL [{case['id']}] {case['question']}")

        print(f"[{case['id']}] refused={refused}")

    unanswerable = sum(1 for c in cases if not c["answerable"])
    print(f"\ncorrect refusals: {correct_refusals}/{unanswerable}")
    print(f"false refusals:   {false_refusals}")

    if hallucinations:
        print(f"\n--- {len(hallucinations)} HALLUCINATIONS ---")
        for cid, q, a in hallucinations:
            print(f"\n[{cid}] {q}\n{a}\n")


if __name__ == "__main__":
    main()