# Retrieval-augmented generation (RAG) in under 60 lines: chunk, embed, search, answer with citations.
# pip install anthropic chromadb    (set ANTHROPIC_API_KEY)
# Chroma's built-in embedding model (~80 MB) downloads on first run, then works offline.
# More: https://github.com/askmohanty/build-ai-agents
import anthropic
import chromadb

DOCS = {
    "disk-full.md": "NodeDiskUsageHigh fires above 85% for 10 minutes and pages at 92%.\n\n"
                    "Logrotate keeps 7 days of logs in /var/log/app; older files can be deleted.",
    "db-timeouts.md": "Connection timeouts are usually caused by the nightly reporting-job export.\n\n"
                      "Cancel the query with SELECT pg_cancel_backend(<pid>); the job must use the read replica.",
}


def chunk(text: str, max_chars: int = 800) -> list[str]:
    chunks, current = [], ""
    for paragraph in text.split("\n\n"):
        if current and len(current) + len(paragraph) > max_chars:
            chunks.append(current)
            current = ""
        current = f"{current}\n\n{paragraph}".strip()
    return chunks + [current] if current else chunks


store = chromadb.Client().create_collection("docs")  # in memory; use PersistentClient(path=...) to keep it
for source, text in DOCS.items():
    pieces = chunk(text)
    store.add(
        ids=[f"{source}#{n}" for n in range(len(pieces))],
        documents=pieces,
        metadatas=[{"source": source}] * len(pieces),
    )


def answer(question: str, k: int = 3) -> str:
    hits = store.query(query_texts=[question], n_results=k)
    context = "\n\n".join(
        f"[{n}] ({meta['source']}) {doc}"
        for n, (doc, meta) in enumerate(zip(hits["documents"][0], hits["metadatas"][0]), 1)
    )
    response = anthropic.Anthropic().messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        system="Answer only from the sources and cite them like [1]. If they don't contain the answer, say you don't know.",
        messages=[{"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {question}"}],
    )
    return response.content[0].text


if __name__ == "__main__":
    print(answer("Payments are timing out. What should I do?"))
