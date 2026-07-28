# Privacy and Trust Model

- Authentication is required for every private portfolio API.
- Database queries include an explicit owner filter.
- RLS policies restrict rows to `auth.uid() = user_id`.
- Files use paths beginning with the authenticated user UUID.
- The Storage bucket is private.
- Source access uses short-lived signed URLs.
- Public portfolios require an explicit random share token.
- Public payloads exclude raw OCR text, hashes, and storage paths.
- Share tokens can be revoked or given an expiry.
- Backend secrets never belong in Vite environment variables.
