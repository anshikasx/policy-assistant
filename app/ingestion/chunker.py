import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source_file: str
    section_title: str | None
    chunk_index: int
    token_estimate: int = field(default=0)


def estimate_tokens(text: str) -> int:
    """Rough approximation: ~4 characters per token for English."""
    return len(text) // 4


def split_into_sections(markdown: str) -> list[tuple[str | None, str]]:
    """Split on '##' headings. Returns (section_title, body) pairs."""
    lines = markdown.splitlines()
    sections: list[tuple[str | None, str]] = []
    current_title: str | None = None
    buffer: list[str] = []

    for line in lines:
        if re.match(r"^##\s+", line):
            if buffer:
                sections.append((current_title, "\n".join(buffer).strip()))
                buffer = []
            current_title = line.lstrip("#").strip()
        else:
            buffer.append(line)

    if buffer:
        sections.append((current_title, "\n".join(buffer).strip()))

    return [(title, body) for title, body in sections if body]


def split_long_text(
    text: str, max_tokens: int = 350, overlap_tokens: int = 50
) -> list[str]:
    """Split oversized text on paragraph boundaries, with overlap."""
    if estimate_tokens(text) <= max_tokens:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    pieces: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        if current and current_tokens + para_tokens > max_tokens:
            pieces.append("\n\n".join(current))
            # carry the last paragraph forward as overlap
            if estimate_tokens(current[-1]) <= overlap_tokens:
                current = [current[-1], para]
                current_tokens = estimate_tokens(current[-1]) + para_tokens
            else:
                current = [para]
                current_tokens = para_tokens
        else:
            current.append(para)
            current_tokens += para_tokens

    if current:
        pieces.append("\n\n".join(current))

    return pieces


def chunk_file(path: Path) -> list[Chunk]:
    markdown = path.read_text(encoding="utf-8")
    chunks: list[Chunk] = []
    index = 0

    for title, body in split_into_sections(markdown):
        for piece in split_long_text(body):
            # prepend heading so the chunk is self-describing
            text = f"{title}\n\n{piece}" if title else piece
            chunks.append(
                Chunk(
                    chunk_id=f"{path.stem}::{index}",
                    text=text,
                    source_file=path.name,
                    section_title=title,
                    chunk_index=index,
                    token_estimate=estimate_tokens(text),
                )
            )
            index += 1

    return chunks


def chunk_directory(directory: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        chunks.extend(chunk_file(path))
    return chunks