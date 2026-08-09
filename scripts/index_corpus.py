from pathlib import Path

from app.ingestion.chunker import chunk_directory
from app.ingestion.embedder import embed_texts
from app.retrieval.vector_store import (
    get_client,
    recreate_collection,
    upsert_chunks,
)


def main() -> None:
    chunks = chunk_directory(Path("data/raw"))
    print(f"chunking done: {len(chunks)} chunks")

    vectors = embed_texts([c.text for c in chunks])
    print(f"embedding done: {len(vectors)} vectors of dim {len(vectors[0])}")

    client = get_client()
    recreate_collection(client)
    upsert_chunks(client, chunks, vectors)
    print(f"indexed into Qdrant: {len(chunks)} points")


if __name__ == "__main__":
    main()