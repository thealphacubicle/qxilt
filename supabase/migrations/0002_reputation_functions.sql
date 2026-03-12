-- Qxilt: RPC functions for submit_review, get_agent_reputation, get_leaderboard_counts

create or replace function public.submit_review(
  p_reviewer_agent_id text,
  p_target_agent_id text,
  p_approved boolean,
  p_task_type text default null,
  p_metadata jsonb default null
)
returns jsonb
language plpgsql
security definer set search_path = ''
as $$
declare
  v_review jsonb;
begin
  insert into public.agents (agent_id) values (p_reviewer_agent_id)
  on conflict (agent_id) do nothing;
  insert into public.agents (agent_id) values (p_target_agent_id)
  on conflict (agent_id) do nothing;
  insert into public.reviews (reviewer_agent_id, target_agent_id, approved, task_type, metadata_json)
  values (p_reviewer_agent_id, p_target_agent_id, p_approved, p_task_type, p_metadata)
  returning to_jsonb(reviews.*) into v_review;
  return v_review;
end;
$$;

create or replace function public.get_agent_reputation(
  p_target_agent_id text,
  p_task_type text default null
)
returns table(target_agent_id text, approvals bigint, rejections bigint, total_reviews bigint)
language plpgsql
security definer set search_path = ''
as $$
begin
  if not exists (select 1 from public.agents where agent_id = p_target_agent_id) then
    return;
  end if;
  return query
  select
    p_target_agent_id,
    count(*) filter (where r.approved)::bigint,
    count(*) filter (where not r.approved)::bigint,
    count(*)::bigint
  from public.reviews r
  where r.target_agent_id = p_target_agent_id
    and (p_task_type is null or r.task_type = p_task_type);
end;
$$;

create or replace function public.get_leaderboard_counts(
  p_task_type text default null,
  p_max_rows int default 1000
)
returns table(target_agent_id text, approvals bigint, rejections bigint)
language plpgsql
security definer set search_path = ''
as $$
begin
  return query
  select
    r.target_agent_id,
    count(*) filter (where r.approved)::bigint,
    count(*) filter (where not r.approved)::bigint
  from public.reviews r
  where (p_task_type is null or r.task_type = p_task_type)
  group by r.target_agent_id
  limit p_max_rows;
end;
$$;
