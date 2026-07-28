-- MemoryVerse AI — Existing Database Upgrade
-- Run this file when older MemoryVerse tables already exist.
-- It is idempotent and can be rerun after a partial failure.

create extension if not exists pgcrypto;

alter table public.documents
  add column if not exists extracted_pages jsonb default '[]'::jsonb,
  add column if not exists source_kind text default 'file',
  add column if not exists source_url text,
  add column if not exists storage_path text,
  add column if not exists original_filename text,
  add column if not exists mime_type text,
  add column if not exists page_count integer default 1,
  add column if not exists file_hash text,
  add column if not exists trust_level text default 'self_uploaded',
  add column if not exists verification_status text default 'self_uploaded',
  add column if not exists verification_details jsonb default '{}'::jsonb,
  add column if not exists review_required boolean default false,
  add column if not exists fields_needing_review text[] default '{}';

create unique index if not exists idx_documents_user_hash_unique
  on public.documents(user_id, file_hash) where file_hash is not null;
create index if not exists idx_documents_user_date
  on public.documents(user_id, date desc nulls last);
create index if not exists idx_documents_user_type
  on public.documents(user_id, type);
create index if not exists idx_documents_skills_gin
  on public.documents using gin(skills);

alter table public.relationships
  add column if not exists user_id uuid references auth.users(id) on delete cascade,
  add column if not exists evidence jsonb default '{}'::jsonb;

update public.relationships r
set user_id = d.user_id
from public.documents d
where r.source_id = d.id and r.user_id is null;

alter table public.relationships drop constraint if exists relationships_relation_type_check;
alter table public.relationships add constraint relationships_relation_type_check
check (relation_type in (
  'EVIDENCES','DEMONSTRATES','APPLIED_IN','SUPPORTS_PROGRESSION_TO',
  'PRECEDES','PART_OF','RELATED_TO','CONTRADICTS'
)) not valid;

create index if not exists idx_relationships_user_source on public.relationships(user_id, source_id);
create index if not exists idx_relationships_user_target on public.relationships(user_id, target_id);

alter table public.career_analyses add column if not exists analysis jsonb default '{}'::jsonb;

create table if not exists public.portfolio_shares (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  share_token text not null unique default encode(gen_random_bytes(24), 'hex'),
  title text not null default 'Evidence-Backed Career Passport',
  include_document_ids uuid[] not null default '{}',
  expires_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz not null default now()
);

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

drop trigger if exists documents_set_updated_at on public.documents;
create trigger documents_set_updated_at before update on public.documents
for each row execute function public.set_updated_at();

alter table public.documents enable row level security;
alter table public.relationships enable row level security;
alter table public.career_analyses enable row level security;
alter table public.resume_versions enable row level security;
alter table public.portfolio_versions enable row level security;
alter table public.mock_interviews enable row level security;
alter table public.portfolio_shares enable row level security;

do $$
declare t text;
begin
  foreach t in array array[
    'documents','relationships','career_analyses','resume_versions',
    'portfolio_versions','mock_interviews','portfolio_shares'
  ] loop
    execute format('drop policy if exists "Users own %1$s" on public.%1$I', t);
    execute format(
      'create policy "Users own %1$s" on public.%1$I for all using (auth.uid() = user_id) with check (auth.uid() = user_id)',
      t
    );
  end loop;
end $$;

insert into storage.buckets (id, name, public)
values ('documents','documents',false)
on conflict (id) do update set public=false;

drop policy if exists "Users read own evidence" on storage.objects;
create policy "Users read own evidence" on storage.objects
for select using (bucket_id='documents' and (storage.foldername(name))[1]=auth.uid()::text);

drop policy if exists "Users upload own evidence" on storage.objects;
create policy "Users upload own evidence" on storage.objects
for insert with check (bucket_id='documents' and (storage.foldername(name))[1]=auth.uid()::text);

drop policy if exists "Users update own evidence" on storage.objects;
create policy "Users update own evidence" on storage.objects
for update using (bucket_id='documents' and (storage.foldername(name))[1]=auth.uid()::text)
with check (bucket_id='documents' and (storage.foldername(name))[1]=auth.uid()::text);

drop policy if exists "Users delete own evidence" on storage.objects;
create policy "Users delete own evidence" on storage.objects
for delete using (bucket_id='documents' and (storage.foldername(name))[1]=auth.uid()::text);

select
  exists(select 1 from information_schema.columns where table_schema='public' and table_name='documents' and column_name='file_hash') as file_hash_exists,
  exists(select 1 from information_schema.columns where table_schema='public' and table_name='relationships' and column_name='user_id') as relationship_user_id_exists,
  exists(select 1 from information_schema.tables where table_schema='public' and table_name='portfolio_shares') as portfolio_shares_exists;
