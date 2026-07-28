# Three-Minute Judge Demo Script

## Before recording

Use a clean account, seed the four visibly watermarked demo records, and import one public GitHub repository. Keep one deliberately low-quality scan ready to demonstrate the integrity gate. Confirm that the backend, Supabase, Gemini, and frontend are already running; do not spend demo time on setup.

## 0:00–0:18 — Hook

“Students do not lose achievements; they lose the ability to find and prove them. MemoryVerse is an evidence-backed career passport. It understands each record, connects the journey, and answers questions with the exact source.”

## 0:18–0:45 — Trust-aware ingestion

Upload the deliberately messy scan. Point out:

- automatic title, issuer, date, skills, and confidence;
- the visible fields requiring review;
- the message **Held out of semantic search and the knowledge graph**;
- private original-file preservation and duplicate fingerprinting.

Say:

“Low-confidence extraction cannot silently pollute a student’s identity. It is stored safely, but it becomes searchable only after the user confirms it.”

Open the edit dialog, correct the field, save, and show that it becomes eligible for indexing.

## 0:45–1:08 — Skill Evidence Passport

Open **Career Passport**.

“Python is not one flat claim. A certificate supports learning, a project demonstrates it, and an internship shows application. The level is deterministic and every source can be opened.”

Open one evidence source.

## 1:08–1:35 — Graph that affects retrieval

Open **Knowledge Graph** and select a skill or project node.

“The graph is not decorative. It expands retrieval from the best matching record to related evidence. We use ‘supports progression to,’ not unsupported causal language.”

## 1:35–2:12 — Defining retrieval moment

Ask:

> What evidence proves that I am prepared for a data analyst role?

Show:

- the green **Semantic retrieval active** badge;
- vector similarity on `[S1]`, `[S2]`, and other source cards;
- second-stage re-rank scores and explanations;
- page number, excerpt, trust label, and original source;
- graph paths used to broaden the evidence.

Say:

“The system retrieves more candidates semantically, re-ranks them for the exact question, then expands through trusted graph links before generating a cited answer.”

For a backup recording only, temporarily use an invalid embedding model and show the amber badge:

> Semantic search unavailable — showing keyword matches

Then restore the correct model. This proves failure modes are disclosed rather than hidden.

## 2:12–2:34 — Useful next action

Open **Career Mentor → Job Description**, paste the prepared Data Analyst description, and show:

- role coverage;
- matching evidence;
- missing requirements;
- weakly supported skills;
- learning-and-evidence plan.

Say:

“This is not a hiring probability. It is an explainable comparison between role requirements and evidence the student actually possesses.”

## 2:34–2:50 — Recruiter delight moment

Create a revocable public passport link and open it in a separate tab. Show its proof map, evidence timeline, trust labels, and controlled source links. Return to the owner screen and point to **Revoke**.

## 2:50–3:00 — Measured close

Open Analytics.

“We report 82% key-field recovery on 100 labeled fields across 20 reproducibly degraded scan fixtures. We also publish the failure case and do not present the offline TF-IDF baseline as Gemini performance.”

Close with:

“MemoryVerse changes a folder of files into a private, searchable, evidence-backed identity—and never hides when the AI is uncertain.”
