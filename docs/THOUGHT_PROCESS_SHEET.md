# MemoryVerse AI — Thought Process Sheet

## 1. Problem observation

A student’s real professional identity is scattered across certificates, resumes, reports, emails, repository links, internship records, and achievements. File storage preserves bytes but loses meaning. Portfolios display selected claims but usually do not show how a skill is supported.

## 2. Core insight

The valuable unit is not the file. It is the **evidence inside the file** and the connection between that evidence and the student’s growth.

The system therefore needs to answer two questions simultaneously:

1. **What does this item prove?**
2. **How does it connect to the rest of the journey?**

## 3. Initial approach and weakness

The first prototype uploaded a document, produced one summary embedding, classified it, and drew document-to-document links. This satisfied the broad challenge but had four weaknesses:

- detailed facts inside long documents were not searchable;
- the graph was displayed but not used during chat retrieval;
- uploaded claims and stronger evidence were treated similarly;
- privacy and user isolation were inconsistent.

## 4. Research-driven redesign

### Evidence chunking

Extracted text is split into overlapping page-aware chunks. Each vector retains document, page, type, user, and trust metadata.

### Hybrid Graph-RAG

Semantic retrieval first finds a broader candidate set. A second Gemini pass re-ranks those chunks for direct relevance to the question. The relationship graph then adds connected milestones. Generation receives evidence chunks, vector similarity, re-rank scores, and explainable paths.

### Evidence hierarchy

A skill is assigned an explainable level based on the strongest source:

- resume/self-declaration;
- certification/academic learning;
- project demonstration;
- internship application;
- external verification;
- repeated independent evidence.

### Trust layer

Files receive a SHA-256 fingerprint. Exact duplicates are rejected. Sources are visibly labelled as self-declared, self-uploaded, source-linked, or verified. GitHub repositories are ingested directly from the public source.

### Human review and integrity routing

The AI returns confidence and a list of ambiguous fields. Records below the configured threshold, or with unresolved fields, are stored privately but excluded from vectors, relationships, evidence scoring, guidance, and public sharing. After the user confirms corrected metadata, vectors and graph relationships are rebuilt.

## 5. Why the solution is useful

### For students

- retrieve any evidence through natural language;
- understand which skills are strongly or weakly supported;
- build resumes and portfolios from grounded evidence;
- preserve a long-term growth timeline.

### For reviewers/recruiters

- distinguish claims from demonstrated/applied evidence;
- open the source behind a skill;
- view a filtered, explicitly shared passport;
- understand the candidate journey without browsing folders.

## 6. Innovation claim

The innovation is not simply “RAG plus a graph.” The differentiator is an **evidence-backed career identity** where each skill is linked to the exact certificate, project, internship, achievement, or repository that supports it, with transparent trust status and citations.

## 7. Evaluation strategy

The project avoids unsupported claims such as “95% accurate.” It reports:

- readable-document coverage;
- citation-ready coverage;
- metadata review completion;
- verified-source coverage;
- indexed chunk count;
- graph relationship count.

A labeled query benchmark measures Recall@K. The committed fixture run recovered **82 of 100 labeled OCR fields across 20 reproducibly degraded synthetic scans**. An offline TF-IDF baseline achieved Recall@5 of 1.00 on three disclosed synthetic queries; this is not represented as Gemini embedding performance. The final semantic Recall@5 must be measured after deploying and indexing the owner account.

## 8. Ethical and safety considerations

- Original evidence is private by default.
- Shared views are explicit and revocable.
- AI uncertainty is visible.
- Career guidance is not a salary or hiring prediction.
- Chronology does not automatically imply causation.
- GitHub source linkage does not prove authorship of every contribution.

## 9. Future work

- issuer-verifiable credential URLs and QR validation;
- email/Drive connectors with explicit consent;
- contribution-level GitHub identity verification;
- multilingual OCR evaluation;
- recruiter feedback with user-controlled disclosure;
- temporal contradiction detection across resumes and certificates.
