import sys

from app.ingestion.embedder import embed_query
from app.retrieval.vector_store import get_client, search


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: python3 -m scripts.search "your question"')
        return

    question = " ".join(sys.argv[1:])
    results = search(get_client(), embed_query(question), top_k=5)

    print(f'\nquery: "{question}"\n')
    for rank, point in enumerate(results, start=1):
        payload = point.payload or {}
        print(f"{rank}. score={point.score:.4f}  {payload.get('chunk_id')}")
        print(f"   {payload.get('source_file')} :: {payload.get('section_title')}")
        print(f"   {payload.get('text', '')[:160]}...\n")


if __name__ == "__main__":
    main()