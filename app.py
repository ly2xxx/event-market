"""
Event Sponsor Marketplace — Streamlit app.

Phase 1: persistence + auth + messaging + notifications + asset upload +
shareable event pages.

Run locally (demo mode, no Supabase):
    uv run streamlit run app.py

Run live (Supabase + Resend + optionally Twilio):
    Set the env vars in `.env.example`, then `uv run streamlit run app.py`.
"""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # local dev convenience; no-op in prod where Fly injects env vars

import auth
import db
import notifications
import storage
import theme

# ─────────────────────────────────────────────────────────────────────────────
# Page config + theme
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Event Sponsor Marketplace",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="collapsed",
)
theme.inject()

EVENT_TYPES = ["Afrobeats", "Amapiano", "Culture / Community", "Corporate", "Festival"]
AUDIENCE_SIZES = ["100-200", "200-500", "500-1000", "1000+"]
BUDGET_RANGES = ["£100-£300", "£300-£1,000", "£1,000-£5,000", "£5,000+"]


# ─────────────────────────────────────────────────────────────────────────────
# Header + nav
# ─────────────────────────────────────────────────────────────────────────────
def render_header(user: dict | None) -> None:
    theme.header()
    cols = st.columns([1, 1, 1, 1, 2])
    pages_for = {
        None: ["Home"],
        "organiser": ["Home", "My events", "Inbox"],
        "sponsor":   ["Home", "Browse", "My offers"],
        "admin":     ["Home", "Admin"],
    }
    visible = pages_for.get(user["role"] if user else None, ["Home"])
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    for i, p in enumerate(visible):
        if cols[i].button(
            p, key=f"nav_{p}", use_container_width=True,
            type="primary" if st.session_state.page == p else "secondary",
        ):
            st.session_state.page = p
            st.rerun()

    with cols[-1]:
        if user:
            st.caption(f"{user['email']} · {user['role']}")
            if st.button("Sign out", key="logout", use_container_width=True):
                auth.logout()
                st.session_state.page = "Home"
                st.rerun()
        else:
            mode = "LIVE" if db.is_live() else "DEMO"
            st.caption(f"Not signed in · {mode} mode")

    st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────────────────
def page_home(user: dict | None) -> None:
    left, right = st.columns([4, 7], gap="large")

    with left:
        st.markdown("### What's the goal?")
        st.info("Match **events** with **sponsors** without IG DMs + WhatsApp chaos.", icon="🎯")
        st.markdown("**Phase 1 features live:**")
        for f in [
            "Magic-link sign in",
            "Persistent events + offers (Supabase)",
            "Per-offer message threads",
            "Email + WhatsApp notifications",
            "Asset uploads (logo, deck, venue photos)",
            "Public event pages with shareable links",
        ]:
            st.markdown(f"- {f}")

    with right:
        if user:
            st.markdown(f"### Welcome back, {user.get('display_name') or user['email']}")
            st.caption(f"Signed in as **{user['role']}**.")
            cols = st.columns(2)
            if user["role"] == "organiser":
                if cols[0].button("Manage my events →", type="primary", use_container_width=True):
                    st.session_state.page = "My events"; st.rerun()
                if cols[1].button("Open inbox", use_container_width=True):
                    st.session_state.page = "Inbox"; st.rerun()
            elif user["role"] == "sponsor":
                if cols[0].button("Browse events →", type="primary", use_container_width=True):
                    st.session_state.page = "Browse"; st.rerun()
                if cols[1].button("My offers", use_container_width=True):
                    st.session_state.page = "My offers"; st.rerun()
        else:
            c1, c2 = st.columns(2, gap="medium")
            with c1, st.container(border=True):
                st.markdown("**I'm an Organiser**")
                st.caption("List your event + packages, receive sponsor offers, accept deals.")
                if st.button("Sign in as organiser", key="login_org", type="primary", use_container_width=True):
                    st.session_state["pending_role"] = "organiser"
                    st.session_state.page = "_login"
                    st.rerun()
            with c2, st.container(border=True):
                st.markdown("**I'm a Sponsor**")
                st.caption("Filter events, view packages, send an offer in 30 seconds.")
                if st.button("Sign in as sponsor", key="login_sp", type="primary", use_container_width=True):
                    st.session_state["pending_role"] = "sponsor"
                    st.session_state.page = "_login"
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ORGANISER — My events (list + create + per-event detail)
# ─────────────────────────────────────────────────────────────────────────────
def page_my_events(user: dict) -> None:
    st.markdown("### My events")
    selected_id = st.session_state.get("editing_event_id")

    events = db.get_events_by_org(user["org_id"])

    list_col, edit_col = st.columns([2, 3], gap="large")

    with list_col:
        with st.container(border=True):
            st.caption("Your events")
            for e in events:
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**{e['name']}**")
                    st.caption(f"{e.get('city') or '—'} · {e.get('status')}")
                with cols[1]:
                    if st.button("Edit", key=f"edit_{e['id']}", use_container_width=True):
                        st.session_state.editing_event_id = e["id"]
                        st.rerun()
            if st.button("＋ New event", key="new_event", type="primary", use_container_width=True):
                st.session_state.editing_event_id = None
                st.session_state["new_event_form"] = True
                st.rerun()

    with edit_col:
        editing = next((e for e in events if e["id"] == selected_id), None)
        if editing or st.session_state.get("new_event_form"):
            _render_event_editor(user, editing)
        else:
            st.info("Pick an event on the left, or create a new one.")


def _render_event_editor(user: dict, ev: dict | None) -> None:
    st.markdown("#### " + ("Edit event" if ev else "Create event"))
    with st.container(border=True):
        with st.form("event_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Event name", value=(ev or {}).get("name", ""))
            city = c2.text_input("City", value=(ev or {}).get("city", ""))

            c3, c4 = st.columns(2)
            evt_date = c3.date_input("Date", value=(ev or {}).get("event_date") or None)
            current_size = (ev or {}).get("audience_size", AUDIENCE_SIZES[1])
            size = c4.selectbox(
                "Audience size", AUDIENCE_SIZES,
                index=AUDIENCE_SIZES.index(current_size) if current_size in AUDIENCE_SIZES else 1,
            )
            current_type = (ev or {}).get("type", EVENT_TYPES[0])
            evt_type = st.selectbox(
                "Vibe / type", EVENT_TYPES,
                index=EVENT_TYPES.index(current_type) if current_type in EVENT_TYPES else 0,
            )
            pitch = st.text_area("Quick pitch", value=(ev or {}).get("pitch", ""))

            cols = st.columns(3)
            save = cols[0].form_submit_button("Save", type="primary", use_container_width=True)
            publish = cols[1].form_submit_button("Save & publish", use_container_width=True)
            cancel = cols[2].form_submit_button("Close", use_container_width=True)

            if save or publish:
                payload = {
                    "org_id": user["org_id"],
                    "name": name.strip() or "Untitled Event",
                    "city": city.strip() or None,
                    "type": evt_type,
                    "audience_size": size,
                    "event_date": str(evt_date) if evt_date else None,
                    "pitch": pitch.strip(),
                }
                if ev:
                    payload["id"] = ev["id"]
                    payload["slug"] = ev.get("slug")
                saved = db.upsert_event(payload)
                if publish:
                    db.publish_event(saved["id"])
                    saved["status"] = "published"
                st.session_state.editing_event_id = saved["id"]
                st.session_state.pop("new_event_form", None)
                st.success("Saved." + (" Now published." if publish else ""))
                st.rerun()
            if cancel:
                st.session_state.editing_event_id = None
                st.session_state.pop("new_event_form", None)
                st.rerun()

    if not ev:
        return

    # ── Share link ──
    base = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/") or "(set PUBLIC_BASE_URL)"
    st.markdown("**Share this event**")
    st.code(f"{base}/event?slug={ev['slug']}", language="text")
    st.caption("Paste this in IG bio, WhatsApp, or wherever your sponsors hang out.")

    # ── Packages ──
    st.markdown("#### Packages")
    pkgs = db.list_packages(ev["id"])
    for p in pkgs:
        with st.container(border=True):
            st.markdown(f"**{p['name']} — £{p['price_pennies'] / 100:,.0f}**")
            st.caption(p.get("benefits") or "")
    with st.container(border=True), st.form(f"add_pkg_{ev['id']}"):
        st.markdown("**Add package**")
        c1, c2 = st.columns([2, 1])
        pname = c1.text_input("Name", placeholder="Bronze / Silver / Gold")
        price = c2.number_input("Price (£)", min_value=10, value=250, step=10)
        benefits = st.text_input("Benefits", placeholder="Logo + 1 IG story mention")
        if st.form_submit_button("Add", type="primary"):
            db.add_package(ev["id"], pname.strip() or "Tier", int(price) * 100, benefits.strip())
            st.rerun()

    # ── Venue photos ──
    st.markdown("#### Venue photos / decks")
    existing = db.list_assets_for_event(ev["id"])
    if existing:
        for a in existing:
            st.caption(f"📎 {a['filename']} ({a.get('kind')})")
    upload = st.file_uploader(
        "Upload photo or deck", type=["png", "jpg", "jpeg", "pdf"],
        key=f"up_event_{ev['id']}",
    )
    if upload is not None:
        storage.upload(
            owner_id=user["id"],
            file_bytes=upload.read(),
            filename=upload.name,
            mime=upload.type or "application/octet-stream",
            event_id=ev["id"],
            kind="venue_photo" if (upload.type or "").startswith("image/") else "deck",
        )
        st.success(f"Uploaded {upload.name}")
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ORGANISER — Inbox (offers across all my events)
# ─────────────────────────────────────────────────────────────────────────────
def page_inbox(user: dict) -> None:
    st.markdown("### Inbox")
    st.caption("Offers across all your events.")

    events = db.get_events_by_org(user["org_id"])
    if not events:
        st.info("Create an event first.")
        return

    by_event = {e["id"]: e for e in events}
    all_offers: list[dict] = []
    for e in events:
        for o in db.list_offers_for_event(e["id"]):
            o["_event"] = e
            all_offers.append(o)

    if not all_offers:
        st.info("No offers yet. Share your event link to get inbound.")
        return

    for o in sorted(all_offers, key=lambda x: x.get("created_at", ""), reverse=True):
        with st.container(border=True):
            top = st.columns([3, 1])
            with top[0]:
                st.markdown(f"**{o['_event']['name']}** — £{o['amount_pennies'] / 100:,.0f}")
                st.markdown(theme.status_badge(o["status"]), unsafe_allow_html=True)
                if o.get("note"):
                    st.caption(o["note"])
            with top[1]:
                if st.button("Open", key=f"open_offer_{o['id']}", use_container_width=True, type="primary"):
                    st.session_state.viewing_offer_id = o["id"]
                    st.session_state.page = "Deal"
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SPONSOR — Browse
# ─────────────────────────────────────────────────────────────────────────────
def page_browse(user: dict) -> None:
    st.markdown("### Browse events")
    st.caption("Filters first. Find the right crowd fast.")

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        f_city = c1.text_input("City", placeholder="Filter by city", label_visibility="collapsed")
        f_type = c2.selectbox("Type", ["All types"] + EVENT_TYPES, label_visibility="collapsed")
        f_size = c3.selectbox("Size", ["Any size"] + AUDIENCE_SIZES, label_visibility="collapsed")
        c4.button("Apply", use_container_width=True, type="primary")

    events = db.list_published_events(city=f_city or None, type_=f_type, size=f_size)
    if not events:
        st.warning("No matches. Try removing a filter.")
        return

    for e in events:
        with st.container(border=True):
            top, btn = st.columns([3, 1])
            with top:
                st.markdown(f"**{e['name']}**")
                st.caption(
                    f"{e.get('city') or '—'} · {e.get('type') or '—'} · "
                    f"Audience {e.get('audience_size') or '—'} · "
                    f"Date: {e.get('event_date') or 'TBA'}"
                )
                if e.get("pitch"):
                    st.write(e["pitch"])
            with btn:
                if st.button("View / offer", key=f"view_{e['id']}", type="primary", use_container_width=True):
                    st.session_state.viewing_event_id = e["id"]
                    st.session_state.page = "_event_detail"
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SPONSOR — Event detail (view packages + send offer)
# ─────────────────────────────────────────────────────────────────────────────
def page_event_detail(user: dict) -> None:
    eid = st.session_state.get("viewing_event_id")
    e = next((x for x in db.list_published_events() if x["id"] == eid), None)
    if not e:
        st.error("Event not found.")
        return

    st.markdown(f"## {e['name']}")
    st.caption(
        f"{e.get('city') or '—'} · {e.get('type') or '—'} · Audience {e.get('audience_size') or '—'}"
    )
    if e.get("pitch"):
        st.write(e["pitch"])

    pkgs = db.list_packages(e["id"])
    if pkgs:
        cols = st.columns(min(3, len(pkgs)))
        for i, p in enumerate(pkgs):
            with cols[i % len(cols)], st.container(border=True):
                st.markdown(f"**{p['name']} — £{p['price_pennies'] / 100:,.0f}**")
                if p.get("benefits"):
                    st.caption(p["benefits"])

    st.divider()
    st.markdown("### Send an offer")
    with st.form("send_offer"):
        opts = {f"{p['name']} — £{p['price_pennies'] / 100:,.0f}": p for p in pkgs}
        opts["Custom amount"] = None
        choice = st.selectbox("Package", list(opts.keys()) or ["Custom amount"])
        chosen = opts.get(choice)
        amount = st.number_input(
            "Offer (£)", min_value=10,
            value=(chosen["price_pennies"] // 100) if chosen else 500, step=10,
        )
        note = st.text_area("Note")
        if st.form_submit_button("Send offer", type="primary", use_container_width=True):
            offer = db.create_offer(
                event_id=e["id"], sponsor_org_id=user["org_id"],
                package_id=(chosen or {}).get("id"),
                amount_pennies=int(amount) * 100, note=note.strip(),
            )
            notifications.notify_new_offer(
                organiser_email=e.get("_organiser_email", ""),
                organiser_phone=e.get("_organiser_phone"),
                sponsor_name=user.get("display_name") or user["email"],
                event_name=e["name"], amount_pennies=offer["amount_pennies"],
                event_slug=e["slug"],
            )
            st.session_state.viewing_offer_id = offer["id"]
            st.session_state.page = "Deal"
            st.success("Offer sent.")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SPONSOR — My offers
# ─────────────────────────────────────────────────────────────────────────────
def page_my_offers(user: dict) -> None:
    st.markdown("### My offers")
    offers = db.list_offers_for_sponsor(user["org_id"])
    if not offers:
        st.info("No offers yet.")
        return
    for o in offers:
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**Event:** {o['event_id']}")
                st.markdown(theme.status_badge(o["status"]), unsafe_allow_html=True)
                st.caption(f"£{o['amount_pennies'] / 100:,.0f} · {o.get('note', '')}")
            with cols[1]:
                if st.button("Open", key=f"my_open_{o['id']}", use_container_width=True, type="primary"):
                    st.session_state.viewing_offer_id = o["id"]
                    st.session_state.page = "Deal"
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# DEAL view (per-offer: status controls + message thread + assets)
# ─────────────────────────────────────────────────────────────────────────────
def page_deal(user: dict) -> None:
    offer_id = st.session_state.get("viewing_offer_id")
    if not offer_id:
        st.info("Open an offer from your inbox or My offers.")
        return

    # Find the offer (cheap: scan visible offers — RLS makes this safe in live mode)
    offer = None
    if user["role"] == "organiser":
        for e in db.get_events_by_org(user["org_id"]):
            offer = next((o for o in db.list_offers_for_event(e["id"]) if o["id"] == offer_id), None)
            if offer:
                offer["_event"] = e
                break
    else:
        offer = next((o for o in db.list_offers_for_sponsor(user["org_id"]) if o["id"] == offer_id), None)

    if not offer:
        st.error("Offer not found.")
        return

    st.markdown("### Deal")
    with st.container(border=True):
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(f"**Offer:** £{offer['amount_pennies'] / 100:,.0f}")
            st.caption(offer.get("note") or "")
        with cols[1]:
            st.markdown(theme.status_badge(offer["status"]), unsafe_allow_html=True)

        if user["role"] == "organiser" and offer["status"] == "sent":
            ac, dc = st.columns(2)
            if ac.button("✅ Accept", type="primary", use_container_width=True):
                db.set_offer_status(offer["id"], "accepted")
                db.create_deal(offer["id"])
                ev = offer.get("_event") or {}
                notifications.notify_offer_accepted(
                    sponsor_email="", sponsor_phone=None,
                    event_name=ev.get("name", ""),
                    amount_pennies=offer["amount_pennies"],
                    event_slug=ev.get("slug", ""),
                )
                st.rerun()
            if dc.button("❌ Decline", use_container_width=True):
                db.set_offer_status(offer["id"], "declined")
                st.rerun()

    # ── Message thread ──
    st.markdown("#### Conversation")
    msgs = db.list_messages(offer["id"])
    if not msgs:
        st.caption("No messages yet — say hi.")
    for m in msgs:
        cls = "msg-bubble-me" if m["sender_id"] == user["id"] else "msg-bubble-them"
        st.markdown(
            f'<div class="{cls}">{m["body"]}<div class="msg-meta">{m.get("created_at", "")}</div></div>',
            unsafe_allow_html=True,
        )

    with st.form(f"msg_{offer['id']}", clear_on_submit=True):
        body = st.text_area("Message", placeholder="Type a reply…", height=80)
        if st.form_submit_button("Send", type="primary"):
            if body.strip():
                db.post_message(offer["id"], user["id"], body.strip())
                ev = offer.get("_event") or {}
                notifications.notify_new_message(
                    recipient_email="", recipient_phone=None,
                    sender_name=user.get("display_name") or user["email"],
                    event_name=ev.get("name", "this event"),
                    preview=body.strip(),
                    event_slug=ev.get("slug", ""),
                )
                st.rerun()

    # ── Assets attached to this offer ──
    st.markdown("#### Files")
    assets = db.list_assets_for_offer(offer["id"])
    for a in assets:
        url = storage.signed_url(a["storage_path"])
        if url:
            st.markdown(f"- [{a['filename']}]({url})  ·  *{a.get('kind')}*")
        else:
            data = storage.fetch_bytes(a["storage_path"])
            if data:
                st.download_button(a["filename"], data=data, file_name=a["filename"],
                                   key=f"dl_{a['id']}")
    upload = st.file_uploader(
        "Attach a logo / brief / deck",
        type=["png", "jpg", "jpeg", "pdf"],
        key=f"up_offer_{offer['id']}",
    )
    if upload is not None:
        storage.upload(
            owner_id=user["id"],
            file_bytes=upload.read(),
            filename=upload.name,
            mime=upload.type or "application/octet-stream",
            offer_id=offer["id"],
            kind="logo" if (upload.type or "").startswith("image/") else "brief",
        )
        st.success("Uploaded.")
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────────────────────
def page_admin(user: dict) -> None:
    st.markdown("### Admin")
    if user["role"] != "admin":
        st.warning("Admin role required.")
        return
    st.caption("Lightweight oversight. Most things self-serve.")
    # Real admin views (verification, payouts) ship in Phase 2.


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    user = auth.current_user()
    render_header(user)

    page = st.session_state.get("page", "Home")

    if page == "_login":
        auth.require_login(role_hint=st.session_state.get("pending_role", "organiser"))
        return

    if page == "Home":
        page_home(user); return

    # Everything below requires login
    if not user:
        auth.require_login()
        return

    routes = {
        "My events": lambda: page_my_events(user),
        "Inbox":     lambda: page_inbox(user),
        "Browse":    lambda: page_browse(user),
        "My offers": lambda: page_my_offers(user),
        "Deal":      lambda: page_deal(user),
        "Admin":     lambda: page_admin(user),
        "_event_detail": lambda: page_event_detail(user),
    }
    routes.get(page, lambda: page_home(user))()


if __name__ == "__main__":
    main()
