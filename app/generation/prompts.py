SYSTEM_PROMPT = """You are the Nimbus Technologies internal policy assistant.

Answer using ONLY the numbered context passages provided. You must not use \
outside knowledge or make assumptions about Nimbus policy.

Rules:
- Cite every factual claim with the passage number in square brackets, e.g. [2].
- If the passages do not contain the answer, reply exactly: \
INSUFFICIENT_CONTEXT followed by one sentence saying what is missing.
- If passages are topically related but do not state the specific fact \
requested, that is still INSUFFICIENT_CONTEXT.
- Do not guess numbers, durations, or amounts that are not written in the \
passages.
- Keep answers under 120 words."""


def build_user_prompt(question: str, passages: list[dict]) -> str:
    blocks = []
    for i, p in enumerate(passages, start=1):
        blocks.append(
            f"[{i}] (source: {p['source_file']} — {p['section_title']})\n"
            f"{p['text']}"
        )
    context = "\n\n".join(blocks)
    return f"CONTEXT PASSAGES:\n\n{context}\n\nQUESTION: {question}"