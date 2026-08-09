import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from app.config import settings
from app.ingestion.chunker import Chunk

COLLECTION = "policies"
VECTOR_SIZE = 384


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def recreate_collection(client: QdrantClient) -> None:
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def upsert_chunks(
    client: QdrantClient, chunks: list[Chunk], vectors: list[list[float]]
) -> None:
    points = [
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id)),
            vector=vector,
            payload={
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source_file": chunk.source_file,
                "section_title": chunk.section_title,
                "chunk_index": chunk.chunk_index,
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=COLLECTION, points=points, wait=True)


def search(client: QdrantClient, query_vector: list[float], top_k: int = 5):
    return client.query_points(
        collection_name=COLLECTION, query=query_vector, limit=top_k
    ).points