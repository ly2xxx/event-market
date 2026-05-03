# Fly.io Onboarding Guide

Tuned for this repo (Python 3.10+, uv, Streamlit) and Windows.

## 1. Accounts + tooling (5 min)

1. Sign up at https://fly.io/app/sign-up. Add a card — Fly requires one even on the free allowance (as of late 2024). You won't be charged until you exceed ~$5/mo of usage.
2. Install `flyctl` in PowerShell:
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```
   Then restart your shell so `flyctl` is on PATH.
3. Log in:
   ```bash
   flyctl auth login
   ```

## 2. Files already added to the repo

- `Dockerfile` — Python 3.12 slim + uv + Streamlit on port 8080
- `fly.toml` — London region, scale-to-zero, 512MB shared CPU
- `.dockerignore` — keeps the build context lean

If your app name `event-sponsor-marketplace` is already taken globally on Fly, edit the `app = "..."` line in `fly.toml` to something unique like `event-sponsor-mkt-<your-handle>`.

## 3. First deploy

From the project root:

```bash
flyctl launch --no-deploy --copy-config
```

When prompted:
- App name: confirm or pick a unique one.
- Region: London (`lhr`).
- Postgres / Redis / Tigris: **No** to all three. You're using Supabase.

Then:

```bash
flyctl deploy
```

First build is 2–3 min. When it finishes:

```bash
flyctl open
```

…opens the live URL (`https://<app>.fly.dev`).

## 4. Verify the WebSocket works

Streamlit lives on a WebSocket. Fly's `http_service` proxies it automatically, but symptoms of misconfiguration are: page loads, then "Please wait…" hangs forever.

Quick check:
```bash
flyctl logs
```

You should see `You can now view your Streamlit app in your browser.` Click around the live app — if a button click reflects in the UI, the WebSocket is fine.

## 5. Secrets (Phase 1: Supabase + Resend + optional Twilio)

The app boots in DEMO mode without any secrets — useful for the very first
deploy. To turn it LIVE, set the secrets below. They become env vars at runtime
and trigger an automatic redeploy.

### 5a. Supabase (required for live mode)

1. Create a project at https://supabase.com (free tier).
2. Open the SQL editor and paste the contents of `migrations/001_init.sql`. Run it.
3. In Storage, create a private bucket called `assets`.
4. From Project Settings → API, copy `URL`, `anon public`, and `service_role`.
5. Set the secrets:
   ```bash
   flyctl secrets set \
     SUPABASE_URL="https://xxx.supabase.co" \
     SUPABASE_ANON_KEY="eyJ..." \
     SUPABASE_SERVICE_KEY="eyJ..."
   ```

### 5b. Resend (email — required for notifications)

1. Sign up at https://resend.com, verify your sending domain.
2. Create an API key.
3. Set:
   ```bash
   flyctl secrets set \
     RESEND_API_KEY="re_..." \
     NOTIFICATIONS_FROM_EMAIL="marketplace@yourdomain.com"
   ```

### 5c. Twilio WhatsApp (optional)

Use the Twilio sandbox for now — both sender and recipients must opt in to
the sandbox number. For production you'll need a WhatsApp Business sender,
which takes ~1 week of approval.

```bash
flyctl secrets set \
  TWILIO_ACCOUNT_SID="AC..." \
  TWILIO_AUTH_TOKEN="..." \
  TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"
```

### 5d. Public base URL (used in notification deep-links)

```bash
flyctl secrets set PUBLIC_BASE_URL="https://<your-app>.fly.dev"
```

Verify which secrets are set:
```bash
flyctl secrets list
```

## 6. Custom domain (optional, do later)

```bash
flyctl certs add app.yourdomain.com
flyctl certs show app.yourdomain.com
```

It tells you the exact A/AAAA records to add at your DNS provider. HTTPS is auto-provisioned via Let's Encrypt within ~1 min of the DNS resolving.

## 7. Day-2 commands you'll actually use

```bash
flyctl deploy              # ship a change
flyctl logs                # tail logs
flyctl status              # is it up? where? cost?
flyctl ssh console         # shell into the running container
flyctl scale count 1       # pin one machine always-on (kills cold starts, ~$5/mo)
flyctl scale count 0       # back to scale-to-zero
flyctl secrets list        # what env vars are set
flyctl apps destroy <name> # nuke it if you want a fresh start
```

## 8. Common gotchas (in order of how often they bite)

- **Forgot `--server.address=0.0.0.0`** → app starts but Fly's healthcheck can't reach it. Look for `Address already in use` or repeated `1 desired, 0 placed` in `flyctl logs`.
- **Memory too low** → Streamlit OOMs on first WebSocket connect. Bump `memory = "1024mb"` in `fly.toml` and `flyctl deploy` if you see SIGKILL.
- **Build times out on `uv sync`** → almost always a corrupt `uv.lock`. Delete it locally, run `uv lock`, commit, redeploy.
- **`flyctl launch` regenerates your `fly.toml`** → that's why this guide uses `--copy-config` plus `--no-deploy`. If it ever overwrites yours, restore from git.

## 9. Cost reality check

With scale-to-zero on a `shared-cpu-1x` 512MB machine, you'll likely stay inside the free allowance until you have steady traffic. When you start sharing event links publicly and want zero cold start:

```bash
flyctl scale count 1
```

That's about **$3–5/mo** for one always-on machine in London. Add `flyctl scale count 2` only if you ever see CPU sustained >70% in `flyctl status`.
