-- Qxilt: indexes for reviews table

create index if not exists idx_reviews_target_agent_id on public.reviews(target_agent_id);
create index if not exists idx_reviews_task_type on public.reviews(task_type);
