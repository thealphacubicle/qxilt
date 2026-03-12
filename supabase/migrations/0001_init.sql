-- Qxilt: agents and reviews tables

create table if not exists public.agents (
  id uuid primary key default gen_random_uuid(),
  agent_id text unique not null,
  created_at timestamptz default now()
);

create table if not exists public.reviews (
  id uuid primary key default gen_random_uuid(),
  reviewer_agent_id text not null,
  target_agent_id text not null,
  approved boolean not null,
  task_type text,
  metadata_json jsonb,
  created_at timestamptz default now()
);
