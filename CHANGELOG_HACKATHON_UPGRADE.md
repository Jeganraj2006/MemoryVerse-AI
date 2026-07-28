# MemoryVerse AI — Hackathon Selection Upgrade

## Product position

MemoryVerse is now an **Evidence-Backed Career Passport**. Its central promise is that every skill claim can point to the exact certificate, project, internship, achievement, academic record, or source-linked repository that supports it.

## Selection-round improvements implemented

### AI organization and retrieval

- Added an explicit retrieval state to every chat response.
- Added a green **Semantic retrieval active** badge and an amber **Semantic search unavailable — showing keyword matches** badge.
- Keyword matching is now clearly reported as degraded mode rather than silently substituted.
- Added a configurable review threshold (`REVIEW_CONFIDENCE_THRESHOLD`, default `0.70`).
- Documents below the threshold, or with unresolved fields, are stored but excluded from vectors, Graph-RAG, evidence scoring, career guidance, gap analysis, and public shares.
- Confirming corrected metadata sets confidence to `1.0`, clears review fields, rebuilds vectors, and rediscovers safe relationships.
- Added 20 reproducibly degraded OCR scan fixtures and committed raw benchmark output.
- Measured OCR key-field recovery: **82/100 fields (82%)**. This is explicitly disclosed as a synthetic degraded-scan fixture benchmark, not production accuracy.
- Documented an OCR failure where the small issuer field was not recovered above the benchmark threshold.

### Advanced RAG

- Added second-stage Gemini re-ranking after semantic retrieval and before graph expansion.
- Added configurable candidate and final counts.
- Source cards now expose cosine similarity, re-rank score, and a short re-rank reason.
- If the re-ranker is unavailable, semantic ordering remains usable and its status is reported.
- Page-aware citations, excerpts, trust labels, and original source links remain part of every grounded answer.

### Usefulness and UX

- Added a visual role-gap experience with matching evidence, weak evidence, missing requirements, and a learning-and-evidence plan.
- Rebuilt the public passport as a polished recruiter/judge artifact with a proof map, evidence timeline, trust labels, controlled source links, and revocation.
- Added a timed three-minute demo script and rehearsal scorecard.
- Added explicit upload messaging explaining why a low-confidence document is being held out.

### Explanation and submission quality

- Replaced the pitch architecture with four readable stages: **Ingest → Integrity Gate → Evidence Graph-RAG → Trusted Identity**.
- Preserved the full technical diagram separately as `docs/architecture-detailed.*`.
- Put measured fixture results and one failure case directly in the root README.
- Clearly distinguishes the **offline TF-IDF Recall@5 baseline (1.00 on 3 synthetic queries)** from the deployed Gemini embedding benchmark, which requires real credentials and a final indexed account.
- Restored a true fresh-install Supabase schema and separated it from the idempotent existing-database migration.

## Previously completed foundation

- Current Google GenAI SDK integration with configurable generation and embedding models.
- Page-aware chunking and authenticated per-user vector filters.
- Explainable graph expansion and evidence-safe relationship language.
- SHA-256 duplicate detection and binary signature validation.
- Private Supabase Storage, signed URLs, RLS, ownership checks, and revocable shares.
- GitHub repository evidence ingestion.
- Deterministic skill evidence levels instead of salary or selection predictions.
- Synthetic demo credentials visibly watermarked as invalid for verification.

## Verified in this source release

- Python source compilation: passed.
- Backend unit tests: **13/13 passed**.
- OCR benchmark runner executed: **82/100 labeled fields recovered**.
- Offline retrieval baseline executed: **Recall@5 = 1.00 on 3/3 disclosed synthetic queries**.
- Architecture PNG/SVG generated from editable Graphviz source.
- Final package excludes credentials, dependency directories, local databases, vector stores, caches, and Git history.

## Must be verified in the owner’s deployed environment

These cannot be honestly claimed without the owner’s credentials and deployment:

- final Gemini embedding Recall@5 over the owner’s indexed portfolio;
- live Gemini re-ranking latency and failure behavior;
- live Supabase authentication, Storage, RLS, and signed URLs with two accounts;
- live GitHub API behavior and rate limits;
- full browser production build and end-to-end demo;
- timed screen recording using the final deployed URL.
