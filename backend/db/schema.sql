-- MemoryVerse AI — Fresh Supabase Schema
-- Run this file only in a new Supabase project with no existing MemoryVerse tables.

create extension if not exists pgcrypto;

create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  type text not null default 'Project' check (type in ('Certification','Project','Internship','Achievement','Academic','Skill')),
  issuer text,
  date date,
  skills text[] not null default '{}',
  summary text not null default '',
  raw_text text not null default '',
  extracted_pages jsonb not null default '[]'::jsonb,
  confidence double precision not null default 0.5 check (confidence >= 0 and confidence <= 1),
  organization text,
  location text,
  technologies text[] not null default '{}',
  experience text,
  achievements text[] not null default '{}',
  tags text[] not null default '{}',
  source_kind text not null default 'file',
  source_url text,
  storage_path text,
  original_filename text,
  mime_type text,
  page_count integer not null default 1 check (page_count >= 1),
  file_hash text,
  trust_level text not null default 'self_uploaded',
  verification_status text not null default 'self_uploaded',
  verification_details jsonb not null default '{}'::jsonb,
  review_required boolean not null default false,
  fields_needing_review text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists idx_documents_user_hash_unique
  on public.documents(user_id, file_hash) where file_hash is not null;
create index if not exists idx_documents_user_date
  on public.documents(user_id, date desc nulls last);
create index if not exists idx_documents_user_type
  on public.documents(user_id, type);
create index if not exists idx_documents_skills_gin
  on public.documents using gin(skills);

create table if not exists public.relationships (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  source_id uuid not null references public.documents(id) on delete cascade,
  target_id uuid not null references public.documents(id) on delete cascade,
  relation_type text not null check (relation_type in (
    'EVIDENCES','DEMONSTRATES','APPLIED_IN','SUPPORTS_PROGRESSION_TO',
    'PRECEDES','PART_OF','RELATED_TO','CONTRADICTS'
  )),
  label text not null,
  confidence double precision not null default 0.8 check (confidence >= 0 and confidence <= 1),
  evidence jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint relationships_no_self_link check (source_id <> target_id),
  constraint relationships_user_edge_unique unique (user_id, source_id, target_id, relation_type)
);

create index if not exists idx_relationships_user_source on public.relationships(user_id, source_id);
create index if not exists idx_relationships_user_target on public.relationships(user_id, target_id);

create table if not exists public.career_analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  analysis jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.resume_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  resume_type text,
  html_code text,
  latex_code text,
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.portfolio_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  html_code text,
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.mock_interviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  overall_score double precision,
  feedback text,
  detailed_grades jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

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
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists documents_set_updated_at on public.documents;
create trigger documents_set_updated_at
before update on public.documents
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
values ('documents', 'documents', false)
on conflict (id) do update set public = false;

drop policy if exists "Users read own evidence" on storage.objects;
create policy "Users read own evidence" on storage.objects
for select using (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users upload own evidence" on storage.objects;
create policy "Users upload own evidence" on storage.objects
for insert with check (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users update own evidence" on storage.objects;
create policy "Users update own evidence" on storage.objects
for update using (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
) with check (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users delete own evidence" on storage.objects;
create policy "Users delete own evidence" on storage.objects
for delete using (
  bucket_id = 'documents' and (storage.foldername(name))[1] = auth.uid()::text
);

select
  to_regclass('public.documents') is not null as documents_exists,
  to_regclass('public.relationships') is not null as relationships_exists,
  to_regclass('public.portfolio_shares') is not null as portfolio_shares_exists;
