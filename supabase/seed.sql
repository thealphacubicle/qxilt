-- Seed data for local dev (runs after migrations on supabase db reset)
insert into public.agents (agent_id) values
  ('agent_A'),
  ('agent_B'),
  ('agent_C')
on conflict (agent_id) do nothing;

insert into public.reviews (reviewer_agent_id, target_agent_id, approved, task_type) values
  ('agent_A', 'agent_B', true, 'forecasting'),
  ('agent_A', 'agent_B', true, 'forecasting'),
  ('agent_C', 'agent_B', false, 'forecasting'),
  ('agent_A', 'agent_C', true, 'summarization'),
  ('agent_B', 'agent_C', true, 'summarization');
