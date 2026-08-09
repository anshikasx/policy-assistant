import numpy as np

from app.ingestion.embedder import embed_texts

SENTENCES = [
    "How do I reset my password?",
    "Steps for password recovery and MFA setup",
    "What is the annual leave carry-forward limit?",
    "Employees may carry forward up to 12 unused leave days",
    "The office cafeteria serves lunch until 3pm",
]


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    vectors = [np.array(v) for v in embed_texts(SENTENCES)]
    for i in range(len(SENTENCES)):
        for j in range(i + 1, len(SENTENCES)):
            score = cosine(vectors[i], vectors[j])
            print(f"{score:.3f}  [{i}] x [{j}]")


if __name__ == "__main__":
    main()