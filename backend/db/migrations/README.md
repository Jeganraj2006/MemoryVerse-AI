# Supabase database setup

- **New Supabase project:** run `backend/db/schema.sql` once.
- **Existing MemoryVerse project:** run `backend/db/migrations/003_evidence_passport.sql` instead.

Do not run the fresh schema over an older database as a substitute for a migration. PostgreSQL's `CREATE TABLE IF NOT EXISTS` does not add newly introduced columns to an existing table.
