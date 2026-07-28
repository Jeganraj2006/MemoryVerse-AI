# Three-minute architecture

The pitch diagram intentionally shows only the four decisions a judge must understand:

1. **Ingest evidence** — accept files, scanned images, and GitHub repositories while preserving the original source.
2. **Review gate** — extract metadata with confidence. Any document below the configured threshold, or with unresolved fields, is stored privately but held out of vectors and the relationship graph.
3. **Build the proof layer** — chunk full text with page numbers, create per-user embeddings, re-rank retrieved chunks, and expand through evidence relationships.
4. **Deliver trusted identity** — answer with citations and retrieval scores, generate an evidence passport, and visualize role gaps.

The detailed engineering diagram is retained as `architecture-detailed.svg` for technical review. The simplified diagram is used in the README and three-minute pitch.
