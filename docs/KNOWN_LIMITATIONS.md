# Known Limitations and Measured Results

## Measured fixture results

- **OCR key-field recovery: 82%** — 82 of 100 labeled fields were recovered across 20 reproducibly degraded scans generated from four visibly watermarked synthetic demo documents.
- **Offline Recall@5 baseline: 1.00** — all 3 labeled demo queries retrieved an expected document within the top five using a local TF-IDF cosine baseline over four synthetic documents.

These are deliberately narrow fixture measurements. The OCR result is not a production accuracy claim, and the offline retrieval result is **not** presented as Gemini embedding quality. The deployed semantic Recall@5 must be measured with `evaluation/run_benchmark.py` after indexing the final account dataset.

## Documented failure case

On `python_data_science_cert__messy_1.jpg`, OCR recovered the student name, course title, duration, score, grade, and skills but failed the `DeepLearning.AI` issuer field threshold. The punctuation and small issuer text produced only 50% normalized token coverage. MemoryVerse therefore exposes extraction confidence and routes uncertain metadata through review instead of silently placing it in the graph.

## Product limitations

- **Issuer verification:** Uploaded certificates begin as self-uploaded evidence until an issuer-backed URL or verification workflow supports a stronger status.
- **GitHub identity:** A public repository proves source availability, not exclusive authorship of every contribution.
- **Graph semantics:** Shared skills and chronology support progression, not causation.
- **OCR:** Performance depends on resolution, lighting, rotation, typography, and the local Tesseract configuration.
- **AI extraction:** Metadata may be wrong. Records below the configured confidence threshold, or with unresolved fields, are held out of semantic retrieval and graph creation until reviewed.
- **Degraded retrieval:** When embeddings fail, the UI visibly states: **“Semantic search unavailable — showing keyword matches.”** Keyword mode is never presented as semantic retrieval.
- **Re-ranking:** The Gemini re-ranker can be unavailable independently of embeddings. In that case, vector order is retained and the UI reports the re-ranker status.
- **Career guidance:** Gap analysis describes evidence coverage. It is not salary, hiring, or selection probability.
- **Vector durability:** Chroma is local by default. Multi-instance production deployment should use a shared vector service.
