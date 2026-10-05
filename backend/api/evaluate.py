"""
evaluate.py
-----------
Runs the shared sample_queries.json through THIS project's recommend_engine
and writes a comparison-ready evaluation_results.json.

This script is intentionally identical across the Sentence-Transformer zip
and the BiLSTM zip (and, later, the BERT zip) - only recommend_engine.py
differs between them. That means the SAME script, run inside each project,
produces directly comparable output:

    query | model | top1 | top3 | top5 | inference_time_ms

which is exactly the row shape needed for the final 3-way comparison table.

NOTE: This is a lightweight demonstration harness, not a research-grade
evaluation framework. There is no ground-truth relevance labelling for the
77 standards, so this script reports WHAT each model recommends and HOW
FAST, not whether the recommendation is "correct". Any accuracy/precision/
recall claim would require manually labelled relevant-standard sets per
query, which this project does not have.

Usage (from backend/api/):
    python evaluate.py
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recommend_engine as engine  # noqa: E402


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "sample_queries.json"), "r", encoding="utf-8") as f:
        queries = json.load(f)

    # Warm up (loads / trains the model once so timing below reflects
    # steady-state inference, not one-time setup cost).
    engine.populate_database()

    results = []
    print(f"Model under test: {engine.MODEL_NAME}\n")

    for q in queries:
        start = time.perf_counter()
        recs = engine.recommend_standards(q["query"], n_results=5)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        top1 = recs[0]["is_code"] if recs else None
        top3 = [r["is_code"] for r in recs[:3]]
        top5 = [r["is_code"] for r in recs[:5]]

        results.append({
            "query_id": q["id"],
            "query": q["query"],
            "model": engine.MODEL_NAME,
            "top1": top1,
            "top3": top3,
            "top5": top5,
            "inference_time_ms": elapsed_ms,
            "recommendations": recs,
        })

        print(f"Query {q['id']}: {q['query']}")
        print(f"  Inference time: {elapsed_ms} ms")
        for r in recs:
            print(f"  Rank {r['rank']}: {r['is_code']}  (score={r['relevance_score']})  - {r['title']}")
        print()

    out_path = os.path.join(here, "evaluation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved comparison-ready results to: {out_path}")
    print("Run the same script inside the other model's project folder,")
    print("then merge both evaluation_results.json files to build the")
    print("Query | Model | Top-1 | Top-3 | Top-5 | Inference Time table.")


if __name__ == "__main__":
    main()
