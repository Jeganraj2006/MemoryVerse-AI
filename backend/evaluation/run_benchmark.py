"""Run a labeled retrieval benchmark and report Recall@K.

Usage:
  python -m evaluation.run_benchmark --user-id <uuid> --file evaluation/sample_benchmark.json --k 5
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from embeddings.embed_service import embed_query
from embeddings.vector_store import query_similar


async def run(user_id: str, benchmark_path: Path, k: int) -> dict:
    cases = json.loads(benchmark_path.read_text(encoding="utf-8"))
    correct = 0
    details = []
    for case in cases:
        hits = await query_similar(await embed_query(case["query"]), user_id=user_id, n_results=k)
        retrieved = {hit.get("title") for hit in hits}
        expected = set(case["expected_document_titles"])
        matched = bool(expected & retrieved)
        correct += int(matched)
        details.append({"query": case["query"], "expected": sorted(expected), "retrieved": sorted(retrieved), "matched": matched})
    return {"cases": len(cases), f"recall_at_{k}": round(correct / len(cases), 4) if cases else 0, "details": details}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--file", default="evaluation/sample_benchmark.json")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.user_id, Path(args.file), args.k)), indent=2))


if __name__ == "__main__":
    main()
