"""
Data-access layer for the Event Sponsor Marketplace.

Two backends, picked at runtime by `is_live()`:

  • LIVE   — Supabase Postgres via supabase-py. Requires SUPABASE_URL and
             SUPABASE_ANON_KEY. Reads/writes use the user's JWT so RLS
             policies apply. The `service` client is used sparingly for
             operations that genuinely need to bypass RLS (e.g. creating
             the `users` row right after signup).

  • DEMO   — In-memory dicts kept on st.session_state. Lets you boot the app
             with zero config and keeps the original prototype working.

The DAO functions all return plain dicts (not ORM rows) so the UI code
doesn't have to care which backend is active.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any, Optional

import streamlit as st
from slugify import slugify

try:
    from supabase import Client, create_client  # type: ignore
except ImportError:  # supabase not installed yet during local exploration
    Client = None  # type: ignore
    create_client = None  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# Mode detection
# ─────────────────────────────────────────────────────────────────────────────
def _env(key: str) -> Optional[str]:
    """Read from os.environ first, then st.secrets if the file exists."""
    val = os.environ.get(key)
    if val:
        return val
    try:
        return st.secrets.get(key, None)  # raises if no secrets.toml
    except Exception:
        return None


def is_live() -> bool:
    """True if Supabase is configured. False = demo mode (in-memory)."""
    return bool(_env("SUPABASE_URL") and _env("SUPABASE_ANON_KEY") and create_client is not None)


# ─────────────────────────────────────────────────────────────────────────────
# Supabase clients (anon = user-scoped, service = admin)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _anon_client() -> "Client":
    return create_client(_env("SUPABASE_URL"), _env("SUPABASE_ANON_KEY"))


@st.cache_resource(show_spinner=False)
def _service_client() -> Optional["Client"]:
    key = _env("SUPABASE_SERVICE_KEY")
    if not key:
        return None
    return create_client(_env("SUPABASE_URL"), key)


def client() -> "Client":
    """Return the Supabase client with the current user's session attached."""
    c = _anon_client()
    sess = st.session_state.get("sb_session")
    if sess and getattr(sess, "access_token", None):
        # supabase-py v2 stores per-call auth headers; setting session here
        # ensures every subsequent .from_().select() runs as the user.
        try:
            c.postgrest.auth(sess.access_token)
        except Exception:
            pass
    return c


def admin_client() -> Optional["Client"]:
    return _service_client()


# ─────────────────────────────────────────────────────────────────────────────
# Demo-mode store
# ─────────────────────────────────────────────────────────────────────────────
def _demo() -> dict[str, list[dict]]:
    if "demo_db" not in st.session_state:
        st.session_state.demo_db = {
            "events": [
                {
                    "id": "e2",
                    "slug": "amapiano-terrace",
                    "name": "Amapiano Terrace",
                    "city": "Edinburgh",
                    "type": "Amapiano",
                    "audience_size": "100-200",
                    "event_date": None,
                    "pitch": "Sunset terrace vibe + content-heavy crowd.",
                    "status": "published",
                    "org_id": "demo-org",
                },
                {
                    "id": "e3",
                    "slug": "culture-and-community-mkt",
                    "name": "Culture & Community Mkt",
                    "city": "Glasgow",
                    "type": "Culture / Community",
                    "audience_size": "500-1000",
                    "event_date": None,
                    "pitch": "Family friendly, diaspora brands, strong community presence.",
                    "status": "published",
                    "org_id": "demo-org",
                },
                {
                    "id": "e4",
                    "slug": "corporate-afterhours",
                    "name": "Corporate Afterhours",
                    "city": "London",
                    "type": "Corporate",
                    "audience_size": "200-500",
                    "event_date": None,
                    "pitch": "Young professionals, high spending power.",
                    "status": "published",
                    "org_id": "demo-org",
                },
            ],
            "packages": [],
            "offers": [],
            "deals": [],
            "messages": [],
            "assets": [],
        }
    return st.session_state.demo_db


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.utcnow().isoformat()


def make_slug(name: str) -> str:
    """Slugify with a short uuid suffix to guarantee uniqueness."""
    base = slugify(name)[:48] or "event"
    return f"{base}-{uuid.uuid4().hex[:6]}"


# ─────────────────────────────────────────────────────────────────────────────
# Events
# ─────────────────────────────────────────────────────────────────────────────
def list_published_events(
    city: Optional[str] = None,
    type_: Optional[str] = None,
    size: Optional[str] = None,
) -> list[dict]:
    if is_live():
        q = client().from_("events").select("*").eq("status", "published")
        if city:
            q = q.ilike("city", f"%{city}%")
        if type_ and type_ != "All types":
            q = q.eq("type", type_)
        if size and size != "Any size":
            q = q.eq("audience_size", size)
        return q.order("created_at", desc=True).execute().data or []

    rows = [e for e in _demo()["events"] if e["status"] == "published"]
    if city:
        rows = [e for e in rows if city.lower() in (e["city"] or "").lower()]
    if type_ and type_ != "All types":
        rows = [e for e in rows if e["type"] == type_]
    if size and size != "Any size":
        rows = [e for e in rows if e["audience_size"] == size]
    return rows


def get_event_by_slug(slug: str) -> Optional[dict]:
    if is_live():
        rows = client().from_("events").select("*").eq("slug", slug).limit(1).execute().data
        return rows[0] if rows else None
    return next((e for e in _demo()["events"] if e["slug"] == slug), None)


def get_events_by_org(org_id: str) -> list[dict]:
    if is_live():
        return client().from_("events").select("*").eq("org_id", org_id).execute().data or []
    return [e for e in _demo()["events"] if e["org_id"] == org_id]


def upsert_event(payload: dict) -> dict:
    """Insert or update an event. Generates slug on first insert."""
    if "slug" not in payload or not payload["slug"]:
        payload["slug"] = make_slug(payload["name"])
    if is_live():
        if "id" in payload and payload["id"]:
            return client().from_("events").update(payload).eq("id", payload["id"]).execute().data[0]
        return client().from_("events").insert(payload).execute().data[0]

    db = _demo()
    if payload.get("id"):
        for i, e in enumerate(db["events"]):
            if e["id"] == payload["id"]:
                db["events"][i] = {**e, **payload}
                return db["events"][i]
    payload.setdefault("id", _new_id())
    payload.setdefault("status", "draft")
    db["events"].append(payload)
    return payload


def publish_event(event_id: str) -> None:
    if is_live():
        client().from_("events").update({"status": "published"}).eq("id", event_id).execute()
        return
    for e in _demo()["events"]:
        if e["id"] == event_id:
            e["status"] = "published"


# ─────────────────────────────────────────────────────────────────────────────
# Packages
# ─────────────────────────────────────────────────────────────────────────────
def list_packages(event_id: str) -> list[dict]:
    if is_live():
        return (
            client().from_("packages").select("*").eq("event_id", event_id)
            .order("price_pennies").execute().data or []
        )
    return [p for p in _demo()["packages"] if p["event_id"] == event_id]


def add_package(event_id: str, name: str, price_pennies: int, benefits: str, inventory: Optional[int] = None) -> dict:
    payload = {
        "event_id": event_id,
        "name": name,
        "price_pennies": price_pennies,
        "benefits": benefits,
        "inventory": inventory,
    }
    if is_live():
        return client().from_("packages").insert(payload).execute().data[0]
    payload["id"] = _new_id()
    payload["sold_count"] = 0
    _demo()["packages"].append(payload)
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Offers
# ─────────────────────────────────────────────────────────────────────────────
def list_offers_for_event(event_id: str) -> list[dict]:
    if is_live():
        return client().from_("offers").select("*").eq("event_id", event_id).execute().data or []
    return [o for o in _demo()["offers"] if o["event_id"] == event_id]


def list_offers_for_sponsor(sponsor_org_id: str) -> list[dict]:
    if is_live():
        return (
            client().from_("offers").select("*").eq("sponsor_org_id", sponsor_org_id)
            .execute().data or []
        )
    return [o for o in _demo()["offers"] if o["sponsor_org_id"] == sponsor_org_id]


def create_offer(
    event_id: str, sponsor_org_id: str, package_id: Optional[str],
    amount_pennies: int, note: str = ""
) -> dict:
    payload = {
        "event_id": event_id,
        "sponsor_org_id": sponsor_org_id,
        "package_id": package_id,
        "amount_pennies": amount_pennies,
        "note": note,
        "status": "sent",
    }
    if is_live():
        return client().from_("offers").insert(payload).execute().data[0]
    payload["id"] = _new_id()
    payload["created_at"] = _now()
    _demo()["offers"].insert(0, payload)
    return payload


def set_offer_status(offer_id: str, status: str) -> None:
    if is_live():
        client().from_("offers").update({"status": status}).eq("id", offer_id).execute()
        return
    for o in _demo()["offers"]:
        if o["id"] == offer_id:
            o["status"] = status


# ─────────────────────────────────────────────────────────────────────────────
# Deals
# ─────────────────────────────────────────────────────────────────────────────
def create_deal(offer_id: str) -> dict:
    payload = {"offer_id": offer_id, "status": "confirmed"}
    if is_live():
        return client().from_("deals").insert(payload).execute().data[0]
    payload["id"] = _new_id()
    _demo()["deals"].append(payload)
    return payload


def get_deal_for_offer(offer_id: str) -> Optional[dict]:
    if is_live():
        rows = client().from_("deals").select("*").eq("offer_id", offer_id).limit(1).execute().data
        return rows[0] if rows else None
    return next((d for d in _demo()["deals"] if d["offer_id"] == offer_id), None)


# ─────────────────────────────────────────────────────────────────────────────
# Messages (per-offer thread)
# ─────────────────────────────────────────────────────────────────────────────
def list_messages(offer_id: str) -> list[dict]:
    if is_live():
        return (
            client().from_("messages").select("*").eq("offer_id", offer_id)
            .order("created_at").execute().data or []
        )
    return sorted(
        [m for m in _demo()["messages"] if m["offer_id"] == offer_id],
        key=lambda m: m["created_at"],
    )


def post_message(offer_id: str, sender_id: str, body: str) -> dict:
    payload = {"offer_id": offer_id, "sender_id": sender_id, "body": body}
    if is_live():
        return client().from_("messages").insert(payload).execute().data[0]
    payload["id"] = _new_id()
    payload["created_at"] = _now()
    _demo()["messages"].append(payload)
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Assets metadata (file bytes go through storage.py)
# ─────────────────────────────────────────────────────────────────────────────
def record_asset(payload: dict) -> dict:
    if is_live():
        return client().from_("assets").insert(payload).execute().data[0]
    payload.setdefault("id", _new_id())
    payload.setdefault("created_at", _now())
    _demo()["assets"].append(payload)
    return payload


def list_assets_for_offer(offer_id: str) -> list[dict]:
    if is_live():
        return client().from_("assets").select("*").eq("offer_id", offer_id).execute().data or []
    return [a for a in _demo()["assets"] if a.get("offer_id") == offer_id]


def list_assets_for_event(event_id: str) -> list[dict]:
    if is_live():
        return client().from_("assets").select("*").eq("event_id", event_id).execute().data or []
    return [a for a in _demo()["assets"] if a.get("event_id") == event_id]


# ─────────────────────────────────────────────────────────────────────────────
# Organisation helpers (used by auth.py to attach an org to the new user)
# ─────────────────────────────────────────────────────────────────────────────
def get_or_create_org(owner_id: str, name: str, kind: str) -> dict:
    if is_live():
        rows = (
            client().from_("organisations").select("*")
            .eq("owner_id", owner_id).eq("kind", kind).limit(1).execute().data
        )
        if rows:
            return rows[0]
        return client().from_("organisations").insert({
            "owner_id": owner_id, "name": name, "kind": kind,
        }).execute().data[0]

    # demo mode: synthesise a single org keyed off the role
    return {"id": f"demo-org-{kind}", "owner_id": owner_id, "name": name, "kind": kind}
