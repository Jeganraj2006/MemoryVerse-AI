# MemoryVerse AI Submission Checklist

## 1. Secrets and accounts

- [ ] Create or select the final Supabase project.
- [ ] Create a fresh Gemini API key for the hackathon deployment.
- [ ] Optionally create a GitHub token for higher repository API limits.
- [ ] Copy `backend/.env.example` to `backend/.env` and fill all server values.
- [ ] Copy `frontend/.env.example` to `frontend/.env` and add only browser-safe values.
- [ ] Confirm no `.env` file is committed or uploaded.
- [ ] Rotate any key that was ever exposed in a public repository or shared archive.

## 2. Database and privacy

For a fresh database:

- [ ] Run `backend/db/schema.sql` in the Supabase SQL Editor.

For an existing database:

- [ ] Back it up.
- [ ] Run `backend/db/migrations/003_evidence_passport.sql`.
- [ ] Inspect old rows whose `user_id` is null.
- [ ] Assign or remove legacy rows before the demo.

Then verify:

- [ ] `documents` Storage bucket is private.
- [ ] RLS is enabled on all seven user-owned tables.
- [ ] User A cannot read, edit, search, or delete User B’s records.
- [ ] Original files open only through signed URLs.
- [ ] Revoked public-share links become unavailable.

## 3. Local functional test

Backend:

```bash
cd backend
python -m venv .venv
# activate the environment
pip install -r requirements.txt
python -m compileall .
python -m unittest discover -s tests -v
uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run build
npm run dev
```

- [ ] Open `/health`; confirm `ai_configured` and `supabase_configured` are true.
- [ ] Register/sign in with a clean account.
- [ ] Upload one text PDF and one scanned image/PDF.
- [ ] Confirm metadata, confidence, review flags, and page count.
- [ ] Correct one field and confirm search/timeline update.
- [ ] Upload the same file again and confirm duplicate detection.
- [ ] Import one public GitHub repository.
- [ ] Ask a question that requires a page-two fact and open its citation.
- [ ] Ask about absent evidence and confirm the answer says evidence is insufficient.
- [ ] Create, open, and revoke a public share link.

## 4. AI evaluation

- [ ] Replace sample benchmark titles with exact final titles.
- [ ] Run `python -m evaluation.run_benchmark --user-id <UUID> --file evaluation/sample_benchmark.json --k 5`.
- [ ] Record the actual Recall@5 result.
- [ ] Manually review citation correctness for at least ten questions.
- [ ] Record classification, issuer/date/skill extraction results on a labeled test set.
- [ ] Include one documented failure and how human review corrects it.
- [ ] Never publish an invented accuracy, latency, or success figure.

## 5. Demo preparation

- [ ] Use the included synthetic demo documents or anonymized personal documents.
- [ ] Rehearse `docs/JUDGE_DEMO_SCRIPT.md` within the required time.
- [ ] Lead with the evidence-backed career-passport distinction.
- [ ] Demonstrate: ingest → understand → connect → retrieve → cite → share → revoke.
- [ ] Keep salary prediction and hiring probability out of the presentation.
- [ ] Prepare a recorded backup in case an external API fails.
- [ ] Blur keys, tokens, email addresses, and private URLs in the video.

## 6. Repository and deliverables

- [ ] Commit the clean release only—not the original 173 MB workspace.
- [ ] Confirm `.gitignore` excludes environments, dependencies, builds, vectors, databases, and secrets.
- [ ] Add the final live URL and demo-video URL to the README.
- [ ] Confirm the architecture image renders on GitHub.
- [ ] Submit the GitHub repository, working prototype/demo video, architecture diagram, and thought-process sheet to Wooble.
- [ ] Test every submitted link in a private/incognito browser.
