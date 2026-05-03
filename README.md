# Event Sponsor Marketplace

A streamlined marketplace designed to connect event organisers with brand sponsors, replacing the fragmented "WhatsApp and IG DM chaos" with a structured, professional platform. End-to-end flow: list event → receive offer → accept → message → exchange assets → close deal.

## 📺 Screens

| Screen | Description |
| :--- | :--- |
| **Home** | Role-aware landing — sign in as organiser or sponsor. |
| **My events** *(organiser)* | Create / edit / publish events, define per-event sponsorship tiers, upload venue photos and decks, copy a shareable link. |
| **Inbox** *(organiser)* | All offers across your events, sorted newest first. |
| **Browse** *(sponsor)* | Filter published events by city, type, and audience size. |
| **My offers** *(sponsor)* | Track every offer you've sent and its status. |
| **Deal** | Per-offer view: accept / decline, in-app message thread, attach logos / briefs / decks. |
| **Admin** | Lightweight oversight (Phase 2 will add verification + payouts). |
| **/event?slug=…** | Public, shareable event page — no login required to view. |

## 🛠️ Setup

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reliable Python dependency management.

### 1. Install uv

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Run in DEMO mode (zero config)

```bash
uv sync
uv run streamlit run app.py
```

Sign in with any email; the verification code is `000000`. All data is in-memory and resets on restart.

### 3. Run in LIVE mode (Supabase + Resend)

1. Create a Supabase project, run [`migrations/001_init.sql`](./migrations/001_init.sql) in the SQL editor, and create a private Storage bucket called `assets`.
2. Sign up for [Resend](https://resend.com) and verify a sending domain.
3. Copy `.env.example` → `.env` and fill in `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`, `RESEND_API_KEY`, `NOTIFICATIONS_FROM_EMAIL`.
4. `uv run streamlit run app.py` — the app auto-detects live mode when env vars are present.

WhatsApp notifications via Twilio are optional; see `.env.example`.

### 4. Deploy to Fly.io

See [`flyio.md`](./flyio.md) for the full walkthrough.

## 📂 Project Structure

```text
event-market/
├── app.py              # Main Streamlit app (role-based nav)
├── auth.py             # Email-OTP sign-in (Supabase or demo)
├── db.py               # Data-access layer with demo-mode fallback
├── notifications.py    # Resend email + Twilio WhatsApp wrappers
├── storage.py          # Supabase Storage uploads
├── theme.py            # Shared CSS / header / status badges
├── pages/
│   └── 1_event.py      # Public event page (/event?slug=…)
├── migrations/
│   └── 001_init.sql    # Postgres schema with RLS
├── Dockerfile          # Python 3.12 + uv + Streamlit
├── fly.toml            # Fly.io config (London, scale-to-zero)
├── flyio.md            # Deployment walkthrough
├── .env.example        # All required + optional env vars
└── pyproject.toml      # uv-managed dependencies
```

## ⚡ Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Database / Auth / Storage**: [Supabase](https://supabase.com) (Postgres + Auth + Storage)
- **Email**: [Resend](https://resend.com)
- **WhatsApp**: [Twilio](https://www.twilio.com) *(optional)*
- **Hosting**: [Fly.io](https://fly.io) (London region, scale-to-zero)
- **Tooling**: [uv](https://github.com/astral-sh/uv)
- **Styling**: Custom dark-mode CSS (radial gradients, glassmorphism)

## 🔄 Demo Flow

1. **Organiser**: Sign in as organiser. Create an event in **My events**, add Bronze / Silver / Gold packages, upload a venue photo, click **Save & publish**. Copy the share link.
2. **Sponsor** (in another browser tab, or after signing out): Open the share link. View packages and submit an offer.
3. **Organiser**: Open **Inbox**, accept the offer. Reply in the in-app message thread.
4. **Sponsor**: Reply. Attach a logo. Both sides see the conversation and files (refresh required — Supabase Realtime is Phase 2).

## 💎 Sponsorship Packages

Packages are defined **per event** by the organiser — no fixed tiers. The defaults that ship in the demo are aligned with what most grassroots organisers expect:

| Tier | Typical Price | Typical Benefits |
| :--- | :--- | :--- |
| **Bronze** | £250 | Logo on flyer • 1 IG story mention |
| **Silver** | £500 | Logo on flyer • MC shoutout • 1 post tag |
| **Gold** | £1,000 | Booth • content bundle • headline mention |
| **Custom** | varies | Tailored deliverables |

## ⚠️ Notes

- **Demo mode is in-memory** — restarting the server wipes everything. Use it for local exploration only.
- **Live mode requires Supabase** — once `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set, the app switches automatically and persists everything to Postgres with row-level security.
- **`/e/{slug}` paths** — true path-based slug routing isn't possible in pure Streamlit. The shareable URL pattern is `/event?slug=<slug>`. A reverse-proxy rewrite is a Phase-2 nginx-sidecar job.
- **Reference**: UI aesthetics and flow are based on the original [`event-sponsor-marketplace-clickable-prototype (2).html`](./event-sponsor-marketplace-clickable-prototype%20(2).html).
