import json
from collections import defaultdict
from pathlib import Path

from app.ingestion.embedder import embed_query
from app.retrieval.vector_store import get_client, search

GOLDEN_SET = Path("data/eval/golden_set.jsonl")
TOP_K = 5


def load_golden_set() -> list[dict]:
    lines = GOLDEN_SET.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def main() -> None:
    client = get_client()
    cases = load_golden_set()

    by_tag: dict[str, list[bool]] = defaultdict(list)

    answerable_top_scores: list[float] = []
    unanswerable_top_scores: list[float] = []

    failures: list[dict] = []

    for case in cases:
        results = search(
            client,
            embed_query(case["question"]),
            top_k=TOP_K,
        )

        retrieved = [
            (p.payload or {}).get("source_file")
            for p in results
        ]

        top_score = results[0].score if results else 0.0

        if case["answerable"]:
            # Record retrieval confidence for answerable questions.
            answerable_top_scores.append(top_score)

            expected = set(case["expected_sources"])
            retrieved_sources = set(retrieved)

            hit = expected.issubset(retrieved_sources)

            by_tag[case["tag"]].append(hit)

            if not hit:
                failures.append(
                    {
                        "id": case["id"],
                        "question": case["question"],
                        "expected": sorted(expected),
                        "retrieved": retrieved,
                        "missing": sorted(
                            expected - retrieved_sources
                        ),
                    }
                )

        else:
            # Unanswerable cases are not included in retrieval
            # hit-rate calculations.
            unanswerable_top_scores.append(top_score)

    print(f"\n{'tag':<14} {'hit rate':>10}   detail")
    print("-" * 50)

    overall: list[bool] = []

    for tag in sorted(by_tag):
        hits = by_tag[tag]
        overall.extend(hits)

        rate = sum(hits) / len(hits)

        print(
            f"{tag:<14} "
            f"{rate:>9.0%}   "
            f"{sum(hits)}/{len(hits)}"
        )

    print("-" * 50)

    print(
        f"{'OVERALL':<14} "
        f"{sum(overall) / len(overall):>9.0%}   "
        f"{sum(overall)}/{len(overall)}"
    )

    if answerable_top_scores:
        print("\nanswerable questions — top-1 similarity scores:")

        for score in sorted(answerable_top_scores):
            print(f"  {score:.4f}")

        print(
            f"  min={min(answerable_top_scores):.4f}"
        )

    if unanswerable_top_scores:
        print(
            "\nunanswerable questions — "
            "top-1 similarity scores:"
        )

        for score in sorted(
            unanswerable_top_scores,
            reverse=True,
        ):
            print(f"  {score:.4f}")

        print(
            f"  max={max(unanswerable_top_scores):.4f}"
        )

    if answerable_top_scores and unanswerable_top_scores:
        answerable_min = min(answerable_top_scores)
        unanswerable_max = max(unanswerable_top_scores)

        print("\n=== THRESHOLD ANALYSIS ===")
        print(
            f"answerable minimum:   "
            f"{answerable_min:.4f}"
        )
        print(
            f"unanswerable maximum: "
            f"{unanswerable_max:.4f}"
        )

        if answerable_min > unanswerable_max:
            print(
                "Result: clean separation exists."
            )
            print(
                f"A threshold between "
                f"{unanswerable_max:.4f} and "
                f"{answerable_min:.4f} "
                f"could separate these cases."
            )
        else:
            print(
                "Result: score distributions overlap."
            )
            print(
                "Similarity alone cannot cleanly "
                "separate answerable and unanswerable "
                "questions."
            )

    if failures:
        print(
            f"\n--- {len(failures)} retrieval misses ---"
        )

        for f in failures:
            print(
                f"\n[{f['id']}] {f['question']}"
            )
            print(
                f"  missing:   {f['missing']}"
            )
            print(
                f"  retrieved: {f['retrieved']}"
            )


if __name__ == "__main__":
    main()