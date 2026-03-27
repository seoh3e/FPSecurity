from __future__ import annotations

from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

try:
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    _CHROMA_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover
    chromadb = None
    DefaultEmbeddingFunction = None
    _CHROMA_IMPORT_ERROR = str(exc)


def _split_policy_sections(policy_text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title = "정책 문서"
    current_lines: list[str] = []

    for line in policy_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("###"):
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_title, body))
            current_title = stripped.lstrip("#").strip()
            current_lines = []
            continue
        if stripped:
            current_lines.append(stripped)

    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_title, body))

    return sections


def _build_or_update_collection(
    policy_path: Path,
    sections: list[tuple[str, str]],
    persist_dir: str | Path,
    collection_name: str,
) -> object:
    if chromadb is None or DefaultEmbeddingFunction is None:
        detail = _CHROMA_IMPORT_ERROR or "chromadb is not installed"
        raise RuntimeError(
            "ChromaDB를 사용할 수 없습니다. "
            "Python 3.14 환경에서는 호환 이슈가 있을 수 있으니 Python 3.11~3.13 환경을 권장합니다. "
            f"detail={detail}"
        )

    persist_path = Path(persist_dir)
    persist_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(persist_path))
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=DefaultEmbeddingFunction(),
        metadata={"source": "fpsecurity_policy"},
    )

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    base = policy_path.resolve().as_posix()

    for idx, (title, body) in enumerate(sections, start=1):
        doc = f"{title}\n{body}"
        doc_id = str(uuid5(NAMESPACE_URL, f"{base}:{idx}:{title}"))
        ids.append(doc_id)
        documents.append(doc)
        metadatas.append({"title": title, "section_index": idx, "source": str(policy_path)})

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return collection


def retrieve_policy_evidence(
    policy_path: str | Path,
    query: str,
    top_k: int = 3,
    persist_dir: str | Path = "artifacts/chroma_policy_db",
    collection_name: str = "policy_rules",
) -> list[dict]:
    path = Path(policy_path)
    if not path.exists():
        return []

    policy_text = path.read_text(encoding="utf-8")
    sections = _split_policy_sections(policy_text)
    if not sections:
        return []

    collection = _build_or_update_collection(
        policy_path=path,
        sections=sections,
        persist_dir=persist_dir,
        collection_name=collection_name,
    )

    result = collection.query(
        query_texts=[query],
        n_results=max(1, top_k),
        include=["documents", "metadatas", "distances"],
    )

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    if not documents:
        return []

    output: list[dict] = []
    for idx, doc in enumerate(documents):
        meta = metadatas[idx] if idx < len(metadatas) and metadatas[idx] else {}
        distance = distances[idx] if idx < len(distances) else None
        title = str(meta.get("title", "정책 조항"))
        excerpt = doc if len(doc) <= 220 else f"{doc[:220].rstrip()}..."
        score = None if distance is None else max(0.0, 1.0 - float(distance))
        output.append(
            {
                "title": title,
                "excerpt": excerpt,
                "distance": distance,
                "score": score,
            }
        )

    return output
