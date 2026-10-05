# Procurement Standards Recommendation System - Model 1 (Sentence Transformer)

This is one of three planned implementations of the same academic project.
All three share the same frontend, the same Django REST API contract, and
the same 77-standard dataset and 6 demo queries - only the recommendation
mechanism inside `backend/api/recommend_engine.py` changes.

| Variant | Mechanism |
|---|---|
| **Model 1 (this zip)** | Sentence Transformer + vector similarity search |
| Model 2 | BiLSTM + Attention |
| Model 3 (future) | BERT-based cross-encoder |

---

## 1. Overall system architecture

```
React frontend (Vite)
        |  POST /api/recommend/  { "tender_text": "..." }
        v
Django REST API  (backend/api/views.py)
        |
        v
recommend_engine.py   <-- the ONLY file that differs between model variants
        |
        v
bis_data.json  (77 Indian Standards - shared, identical across all 3 variants)
        |
        v
{ status, query, model, inference_time_ms, recommendations: [...] }
```

The frontend, `views.py`, `urls.py`, `bis_data.json`, and `sample_queries.json`
are intentionally identical to the other model variants so that comparisons
are apples-to-apples.

## 2. How the 77 standards are used

`backend/api/bis_data.json` holds 77 Indian Standards, each with:
`is_code, title, scope, allied_standards, test_methods, mandatory_cert, scheme, status`.

For every standard, a single **context-rich text** string is built:

```
"Title: {title}. Scope: {scope}."
```

This is the text that gets embedded and indexed. It is a *retrieval/knowledge
base*, not labelled training data - there is no "correct standard for query X"
ground truth attached to it.

## 3. Model 1 recommendation flow (Sentence Transformer)

```
User Query
    |
Sentence Transformer (all-MiniLM-L6-v2)   <- PRETRAINED, frozen
    |  encodes query into a 384-dim dense embedding
    v
Vector similarity search (ChromaDB HNSW index)
    |  compares query embedding against the 77 pre-computed standard embeddings
    v
Ranked standards -> Top-5 recommendations
```

The 77 standard embeddings are computed **once** (on first run) using the
exact same pretrained `all-MiniLM-L6-v2` model, and stored in a persistent
ChromaDB collection at `backend/api/bis_vector_db/`. Every later query is
embedded with the same frozen model and compared against those stored
vectors - no training happens at request time.

### What is pretrained vs. trained here

- **Pretrained (frozen, unmodified):** `all-MiniLM-L6-v2` sentence embedding
  model. It was trained by its original authors on large public
  sentence-similarity corpora - **not** on these 77 standards.
- **Trained here:** nothing. This model performs **zero-shot semantic
  retrieval** - the 77 standards are only ever embedded and indexed, never
  used to update the model's weights.

### A naming note on "FAISS"

This implementation uses **ChromaDB's** built-in HNSW-based vector index,
not a literal `faiss.IndexFlatIP` index. The retrieval *concept* is
identical (embed -> nearest-neighbour search -> rank), and Chroma is a
common, simpler drop-in for exactly this kind of small-scale semantic
search - but if your evaluation/viva specifically requires the literal
FAISS library, that would need a separate `faiss-cpu` based index built
over the same embeddings (not implemented in this zip, to avoid silently
rewriting a working, tested component).

## 4. Output format (shared contract across all model variants)

```json
{
  "status": "success",
  "query": "We need 100W LED street lights for municipal roads.",
  "model": "Sentence Transformer (all-MiniLM-L6-v2) + Vector Similarity Search (ChromaDB)",
  "inference_time_ms": 8.42,
  "recommendations": [
    {
      "is_code": "IS 10322 (Part 5/Sec 3):2012",
      "title": "Luminaires - Particular Requirements: Street Lighting Luminaires",
      "allied_standards": ["..."],
      "test_methods": ["..."],
      "mandatory_cert": true,
      "scheme": "Compulsory Registration Scheme (CRS)",
      "status": "Active",
      "relevance_score": 71.35,
      "rank": 1
    }
  ]
}
```

## 5. Making the 3-way comparison easy

`backend/api/evaluate.py` runs the shared `sample_queries.json` (the 6 demo
queries) through this project's `recommend_engine.py` and writes
`backend/api/evaluation_results.json` with, per query: `top1, top3, top5,
inference_time_ms`, plus the full ranked list. This script is byte-identical
across all three model zips - run it in each project folder, then merge the
three `evaluation_results.json` files into your final comparison table:

| Query | Model | Top-1 | Top-3 | Top-5 | Inference Time |
|---|---|---|---|---|---|

This is a lightweight demonstration harness, **not** a research-grade
evaluation framework - see Limitations below.

## 6. Limitations

- **No ground-truth relevance labels.** There is no manually verified
  "correct standards for query X" mapping for the 77 standards, so nothing
  here is an accuracy/precision/recall/F1 benchmark. Any cross-model
  comparison is a *qualitative* demonstration of "same problem, same data,
  different architecture" - not a validated benchmark.
- **No requirement-extraction step.** The raw query text is passed directly
  to the embedding model; there is no separate NLP step that pulls out
  structured fields (wattage, material, quantity, etc.) from the query.
- **77-standard dataset is a curated academic sample**, compiled and
  cross-checked against public BIS records for this project. It is not an
  exhaustive or officially issued BIS catalogue - verify against
  https://www.services.bis.gov.in before using it beyond this demo.
- **ChromaDB, not literal FAISS** - see the naming note above.

## 7. Running the project

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
The first request to `/api/recommend/` will download `all-MiniLM-L6-v2`
(requires internet once) and build the vector index - subsequent requests
are fast.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open the printed local URL (typically `http://localhost:5173`).

### Comparison harness
```bash
cd backend/api
python evaluate.py
```

## 8. Example

**Query:** "We need 100W LED street lights for municipal roads."

Expect top matches from the LED/luminaire cluster of standards, e.g.
`IS 10322 (Part 5/Sec 3):2012` (street lighting luminaires) and
`IS 15885 (Part 2/Sec 13):2012` (LED driver/controlgear safety) - exact
ranking depends on the embedding model's similarity scores at run time.
