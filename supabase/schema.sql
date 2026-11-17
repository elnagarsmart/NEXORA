-- NEXORA starter schema. Run in Supabase SQL Editor.
create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text,
  preferred_language text not null default 'ar' check (preferred_language in ('ar','en')),
  role text not null default 'member' check (role in ('owner','admin','moderator','member')),
  created_at timestamptz not null default now()
);

create table if not exists public.notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  body text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  completed boolean not null default false,
  due_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.posts (
  id uuid primary key default gen_random_uuid(),
  author_id uuid not null references auth.users(id) on delete cascade,
  body text not null,
  visibility text not null default 'public' check (visibility in ('public','followers','private')),
  status text not null default 'pending' check (status in ('pending','published','hidden','removed')),
  created_at timestamptz not null default now()
);

create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now()
);

create table if not exists public.conversation_members (
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  primary key (conversation_id, user_id)
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  sender_id uuid not null references auth.users(id) on delete cascade,
  body text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  reporter_id uuid not null references auth.users(id) on delete cascade,
  target_type text not null check (target_type in ('post','profile','message')),
  target_id uuid not null,
  reason text not null,
  status text not null default 'open' check (status in ('open','reviewing','resolved','dismissed')),
  created_at timestamptz not null default now()
);

create table if not exists public.user_blocks (
  blocker_id uuid not null references auth.users(id) on delete cascade,
  blocked_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (blocker_id, blocked_id),
  check (blocker_id <> blocked_id)
);

alter table public.profiles enable row level security;
alter table public.notes enable row level security;
alter table public.tasks enable row level security;
alter table public.posts enable row level security;
alter table public.conversations enable row level security;
alter table public.conversation_members enable row level security;
alter table public.messages enable row level security;
alter table public.reports enable row level security;
alter table public.user_blocks enable row level security;

create policy "profiles visible to signed-in users" on public.profiles
for select to authenticated using (true);
create policy "users update own profile" on public.profiles
for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);
create policy "users insert own profile" on public.profiles
for insert to authenticated with check (auth.uid() = id);

create policy "notes are private to owner" on public.notes
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "tasks are private to owner" on public.tasks
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "published public posts readable" on public.posts
for select to authenticated using (
  (status = 'published' and visibility = 'public') or author_id = auth.uid()
);
create policy "users create own pending posts" on public.posts
for insert to authenticated with check (author_id = auth.uid() and status = 'pending');
create policy "users edit own pending posts" on public.posts
for update to authenticated using (author_id = auth.uid() and status = 'pending')
with check (author_id = auth.uid() and status = 'pending');

create policy "members can see their conversations" on public.conversations
for select to authenticated using (
  exists(select 1 from public.conversation_members m where m.conversation_id = id and m.user_id = auth.uid())
);
create policy "members can see membership" on public.conversation_members
for select to authenticated using (user_id = auth.uid());
create policy "members can read messages" on public.messages
for select to authenticated using (
  exists(select 1 from public.conversation_members m where m.conversation_id = messages.conversation_id and m.user_id = auth.uid())
);
create policy "members can send messages" on public.messages
for insert to authenticated with check (
  sender_id = auth.uid() and exists(
    select 1 from public.conversation_members m where m.conversation_id = messages.conversation_id and m.user_id = auth.uid()
  )
);

create policy "users create reports" on public.reports
for insert to authenticated with check (reporter_id = auth.uid());
create policy "users see own reports" on public.reports
for select to authenticated using (reporter_id = auth.uid());
create policy "users manage own blocks" on public.user_blocks
for all to authenticated using (blocker_id = auth.uid()) with check (blocker_id = auth.uid());

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
for each row execute procedure public.handle_new_user();

-- Assign the first owner manually after signup using a trusted SQL Editor session.
-- Never allow users to set their own role from the client.
