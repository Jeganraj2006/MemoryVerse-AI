# Testing and Evaluation

## Automated core tests

```bash
cd backend
python -m unittest discover -s tests -v
```

Tests cover page-aware chunking, evidence-level rules, non-causal relationships, upload signature validation, date normalization, the low-confidence review gate, re-ranker ordering, and re-ranker failure behavior.

## Reproduce the OCR robustness result

The included fixtures are visibly synthetic and are degraded with rotation, lower resolution, blur, contrast loss, compression, and noise.

```bash
cd backend
python -m evaluation.generate_ocr_fixtures
python -m evaluation.run_ocr_benchmark \
  --manifest evaluation/ocr_benchmark_manifest.json \
  --output evaluation/results/ocr_benchmark_result.json
```

Expected result for the committed deterministic fixtures:

```text
20 scan fixtures
100 labeled fields
82 recovered fields
OCR key-field recovery = 0.82
```

Metric definition: a field is recovered when at least 70% of its normalized tokens occur in Tesseract output.

## Reproduce the exercised offline Recall@5 baseline

```bash
python -m evaluation.run_offline_retrieval_benchmark \
  --file evaluation/sample_benchmark.json \
  --k 5 \
  --output evaluation/results/offline_retrieval_result.json
```

Expected committed fixture result: `Recall@5 = 1.00` on 3 queries and 4 synthetic documents. This is a TF-IDF baseline, not a semantic embedding claim.

## Measure deployed semantic Recall@5

After configuring Gemini, Supabase, and indexing the final portfolio:

```bash
python -m evaluation.run_benchmark \
  --user-id YOUR_SUPABASE_USER_UUID \
  --file evaluation/sample_benchmark.json \
  --k 5
```

Replace the demo benchmark with at least 20 labeled questions for the final submission. Paste the exact output into the README without rounding it upward.

## Required manual failure-mode checks

1. Temporarily remove `GEMINI_API_KEY`, ask a question, and confirm the amber degraded-mode badge appears.
2. Upload a document below the confidence threshold and confirm it is saved but not indexed or linked.
3. Correct that document in the review/edit screen and confirm it becomes searchable after re-indexing.
4. Open a shared passport in a private browser window, then revoke it and confirm the link becomes unavailable.
5. Verify source cards show vector similarity and re-rank score when semantic retrieval is active.
