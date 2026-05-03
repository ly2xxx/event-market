-- Event Sponsor Marketplace — initial schema
-- Run this in the Supabase SQL editor (or via `supabase db push`).
--
-- Conventions:
--   * All ids are uuid, default gen_random_uuid()
--   * created_at / updated_at on every row
--   * RLS enabled on every table; policies live next to the table
--   * Public-facing reads (event pages) explicitly allow anon
--   * Everything else requires auth.uid() ownership

create extension if not exists "pgcrypto";

-- ─────────────────────────────────────────────────────────────────────────────
-- USERS (mirrors auth.users with profile data the app needs)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.users (
    id uuid primary key references auth.users(id) on delete cascade,
    email text not null unique,
    display_name text,
    role text not null check (role in ('organiser', 'sponsor', 'admin')) default 'organiser',
    phone text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
alter table public.users enable row level security;

create policy "users read own"
    on public.users for select
    using (auth.uid() = id);

create policy "users update own"
    on public.users for update
    using (auth.uid() = id);

create policy "users insert own"
    on public.users for insert
    with check (auth.uid() = id);

-- ─────────────────────────────────────────────────────────────────────────────
-- ORGANISATIONS (an organiser can have one; a sponsor has one)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.organisations (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references public.users(id) on delete cascade,
    name text not null,
    kind text not null check (kind in ('organiser', 'sponsor')),
    industry text,
    budget_range text,
    verified boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
alter table public.organisations enable row level security;

create policy "orgs read own"
    on public.organisations for select
    using (auth.uid() = owner_id);

create policy "orgs write own"
    on public.organisations for all
    using (auth.uid() = owner_id)
    with check (auth.uid() = owner_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- EVENTS
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.events (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references public.organisations(id) on delete cascade,
    slug text not null unique,
    name text not null,
    city text,
    type text,
    audience_size text,
    event_date date,
    pitch text,
    status text not null check (status in ('draft', 'pending_review', 'published', 'archived')) default 'draft',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists events_status_idx on public.events(status);
create index if not exists events_org_idx on public.events(org_id);
alter table public.events enable row level security;

-- Anyone (including anon) can read PUBLISHED events. This powers /event?slug=...
create policy "events public read"
    on public.events for select
    using (status = 'published');

-- Owner can read all their own (drafts included)
create policy "events owner read"
    on public.events for select
    using (
        exists (
            select 1 from public.organisations o
            where o.id = events.org_id and o.owner_id = auth.uid()
        )
    );

create policy "events owner write"
    on public.events for all
    using (
        exists (
            select 1 from public.organisations o
            where o.id = events.org_id and o.owner_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from public.organisations o
            where o.id = events.org_id and o.owner_id = auth.uid()
        )
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- PACKAGES (per-event sponsorship tiers)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.packages (
    id uuid primary key default gen_random_uuid(),
    event_id uuid not null references public.events(id) on delete cascade,
    name text not null,
    price_pennies integer not null check (price_pennies >= 0),
    benefits text,
    inventory integer,                 -- null = unlimited
    sold_count integer not null default 0,
    created_at timestamptz not null default now()
);
create index if not exists packages_event_idx on public.packages(event_id);
alter table public.packages enable row level security;

create policy "packages public read"
    on public.packages for select
    using (
        exists (
            select 1 from public.events e
            where e.id = packages.event_id and e.status = 'published'
        )
    );

create policy "packages owner all"
    on public.packages for all
    using (
        exists (
            select 1
            from public.events e
            join public.organisations o on o.id = e.org_id
            where e.id = packages.event_id and o.owner_id = auth.uid()
        )
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- OFFERS (sponsor → event)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.offers (
    id uuid primary key default gen_random_uuid(),
    event_id uuid not null references public.events(id) on delete cascade,
    package_id uuid references public.packages(id) on delete set null,
    sponsor_org_id uuid not null references public.organisations(id) on delete cascade,
    amount_pennies integer not null check (amount_pennies >= 0),
    note text,
    status text not null check (status in ('sent', 'accepted', 'declined', 'withdrawn')) default 'sent',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists offers_event_idx on public.offers(event_id);
create index if not exists offers_sponsor_idx on public.offers(sponsor_org_id);
alter table public.offers enable row level security;

-- Sponsor sees their own offers; organiser sees offers on their events
create policy "offers visibility"
    on public.offers for select
    using (
        exists (
            select 1 from public.organisations o
            where o.id = offers.sponsor_org_id and o.owner_id = auth.uid()
        )
        or exists (
            select 1 from public.events e
            join public.organisations o on o.id = e.org_id
            where e.id = offers.event_id and o.owner_id = auth.uid()
        )
    );

create policy "offers sponsor insert"
    on public.offers for insert
    with check (
        exists (
            select 1 from public.organisations o
            where o.id = offers.sponsor_org_id and o.owner_id = auth.uid()
        )
    );

-- Either party can update (sponsor withdraws, organiser accepts/declines).
-- Application logic enforces which transitions are valid.
create policy "offers update either party"
    on public.offers for update
    using (
        exists (
            select 1 from public.organisations o
            where o.id = offers.sponsor_org_id and o.owner_id = auth.uid()
        )
        or exists (
            select 1 from public.events e
            join public.organisations o on o.id = e.org_id
            where e.id = offers.event_id and o.owner_id = auth.uid()
        )
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- DEALS (created when an offer is accepted; carries lifecycle past acceptance)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.deals (
    id uuid primary key default gen_random_uuid(),
    offer_id uuid not null unique references public.offers(id) on delete cascade,
    status text not null check (status in ('confirmed', 'paid', 'delivered', 'cancelled')) default 'confirmed',
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
alter table public.deals enable row level security;

create policy "deals visibility"
    on public.deals for select
    using (
        exists (
            select 1 from public.offers off
            join public.organisations spo on spo.id = off.sponsor_org_id
            where off.id = deals.offer_id and spo.owner_id = auth.uid()
        )
        or exists (
            select 1 from public.offers off
            join public.events e on e.id = off.event_id
            join public.organisations o on o.id = e.org_id
            where off.id = deals.offer_id and o.owner_id = auth.uid()
        )
    );

create policy "deals write either party"
    on public.deals for all
    using (
        exists (
            select 1 from public.offers off
            join public.organisations spo on spo.id = off.sponsor_org_id
            where off.id = deals.offer_id and spo.owner_id = auth.uid()
        )
        or exists (
            select 1 from public.offers off
            join public.events e on e.id = off.event_id
            join public.organisations o on o.id = e.org_id
            where off.id = deals.offer_id and o.owner_id = auth.uid()
        )
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- MESSAGES (one thread per offer — both parties post)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.messages (
    id uuid primary key default gen_random_uuid(),
    offer_id uuid not null references public.offers(id) on delete cascade,
    sender_id uuid not null references public.users(id) on delete cascade,
    body text not null,
    created_at timestamptz not null default now()
);
create index if not exists messages_offer_idx on public.messages(offer_id, created_at);
alter table public.messages enable row level security;

create policy "messages thread visibility"
    on public.messages for select
    using (
        exists (
            select 1 from public.offers off
            join public.organisations spo on spo.id = off.sponsor_org_id
            where off.id = messages.offer_id and spo.owner_id = auth.uid()
        )
        or exists (
            select 1 from public.offers off
            join public.events e on e.id = off.event_id
            join public.organisations o on o.id = e.org_id
            where off.id = messages.offer_id and o.owner_id = auth.uid()
        )
    );

create policy "messages thread insert"
    on public.messages for insert
    with check (
        sender_id = auth.uid()
        and (
            exists (
                select 1 from public.offers off
                join public.organisations spo on spo.id = off.sponsor_org_id
                where off.id = messages.offer_id and spo.owner_id = auth.uid()
            )
            or exists (
                select 1 from public.offers off
                join public.events e on e.id = off.event_id
                join public.organisations o on o.id = e.org_id
                where off.id = messages.offer_id and o.owner_id = auth.uid()
            )
        )
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- ASSETS (logos, decks, venue photos — file pointer + metadata)
-- Files live in Supabase Storage bucket "assets". This row is the metadata.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.assets (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references public.users(id) on delete cascade,
    offer_id uuid references public.offers(id) on delete cascade,
    event_id uuid references public.events(id) on delete cascade,
    storage_path text not null,    -- e.g. "{owner_id}/{uuid}.pdf"
    filename text not null,
    mime_type text,
    size_bytes integer,
    kind text check (kind in ('logo', 'brief', 'deck', 'venue_photo', 'other')) default 'other',
    created_at timestamptz not null default now()
);
create index if not exists assets_offer_idx on public.assets(offer_id);
create index if not exists assets_event_idx on public.assets(event_id);
alter table public.assets enable row level security;

create policy "assets owner read"
    on public.assets for select
    using (auth.uid() = owner_id);

-- An asset attached to an offer is visible to both parties of the offer
create policy "assets thread read"
    on public.assets for select
    using (
        offer_id is not null and (
            exists (
                select 1 from public.offers off
                join public.organisations spo on spo.id = off.sponsor_org_id
                where off.id = assets.offer_id and spo.owner_id = auth.uid()
            )
            or exists (
                select 1 from public.offers off
                join public.events e on e.id = off.event_id
                join public.organisations o on o.id = e.org_id
                where off.id = assets.offer_id and o.owner_id = auth.uid()
            )
        )
    );

-- An asset attached to a published event is publicly readable (e.g. venue photo on /event)
create policy "assets event public read"
    on public.assets for select
    using (
        event_id is not null and exists (
            select 1 from public.events e
            where e.id = assets.event_id and e.status = 'published'
        )
    );

create policy "assets owner write"
    on public.assets for all
    using (auth.uid() = owner_id)
    with check (auth.uid() = owner_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- PAYOUTS (placeholder for Phase 2 Stripe Connect integration)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.payouts (
    id uuid primary key default gen_random_uuid(),
    deal_id uuid not null references public.deals(id) on delete cascade,
    amount_pennies integer not null check (amount_pennies >= 0),
    currency text not null default 'GBP',
    stripe_payment_intent_id text,
    stripe_transfer_id text,
    status text not null check (status in ('pending', 'held', 'released', 'refunded', 'failed')) default 'pending',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
alter table public.payouts enable row level security;

create policy "payouts deal parties read"
    on public.payouts for select
    using (
        exists (
            select 1 from public.deals d
            join public.offers off on off.id = d.offer_id
            join public.organisations spo on spo.id = off.sponsor_org_id
            where d.id = payouts.deal_id and spo.owner_id = auth.uid()
        )
        or exists (
            select 1 from public.deals d
            join public.offers off on off.id = d.offer_id
            join public.events e on e.id = off.event_id
            join public.organisations o on o.id = e.org_id
            where d.id = payouts.deal_id and o.owner_id = auth.uid()
        )
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- updated_at triggers
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function public.touch_updated_at() returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

do $$
declare
    t text;
begin
    for t in select unnest(array['users','organisations','events','offers','deals','payouts']) loop
        execute format('drop trigger if exists trg_%I_touch on public.%I', t, t);
        execute format('create trigger trg_%I_touch before update on public.%I
                        for each row execute function public.touch_updated_at()', t, t);
    end loop;
end$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Storage bucket for assets (run once)
-- Note: bucket creation can also be done via the Supabase dashboard.
-- Policies below assume the bucket exists and is private.
-- ─────────────────────────────────────────────────────────────────────────────
-- insert into storage.buckets (id, name, public) values ('assets', 'assets', false)
--   on conflict (id) do nothing;
