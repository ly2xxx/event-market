"""
Public event page — the link organisers share on IG/WhatsApp.

URL pattern (Streamlit limitation): /event?slug=<slug>

True /e/{slug} routing isn't possible without leaving Streamlit. The slug
itself is what matters for the share link; the path prefix is cosmetic.
A reverse-proxy rewrite from /e/<slug> → /event?slug=<slug> on the Fly
side would close that gap when needed.
"""
from __future__ import annotations

import streamlit as st

import auth
import db
import storage
from notifications import notify_new_offer

st.set_page_config(page_title="Event", page_icon="🎪", layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# Read slug from query param
# ─────────────────────────────────────────────────────────────────────────────
slug = st.query_params.get("slug")
if not slug:
    st.error("No event specified. Open from a shared link like `/event?slug=…`.")
    st.stop()

event = db.get_event_by_slug(slug)
if not event:
    st.error("Event not found or not yet published.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"## {event['name']}")
meta = " · ".join(filter(None, [
    event.get("city"),
    event.get("type"),
    f"Audience {event['audience_size']}" if event.get("audience_size") else None,
    f"Date: {event.get('event_date')}" if event.get("event_date") else None,
]))
st.caption(meta)

if event.get("pitch"):
    st.write(event["pitch"])

# Venue photos / decks attached to the event
event_assets = db.list_assets_for_event(event["id"])
photos = [a for a in event_assets if (a.get("mime_type") or "").startswith("image/")]
docs = [a for a in event_assets if a not in photos]

if photos:
    cols = st.columns(min(3, len(photos)))
    for i, a in enumerate(photos[:6]):
        url = storage.signed_url(a["storage_path"])
        if url:
            cols[i % len(cols)].image(url, caption=a.get("filename"))

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Packages
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Sponsorship packages")
packages = db.list_packages(event["id"])
if not packages:
    st.info("This organiser hasn't published packages yet.")
else:
    cols = st.columns(min(3, len(packages)))
    for i, p in enumerate(packages):
        with cols[i % len(cols)]:
            with st.container(border=True):
                st.markdown(f"**{p['name']} — £{p['price_pennies'] / 100:,.0f}**")
                if p.get("benefits"):
                    st.caption(p["benefits"])
                if p.get("inventory") is not None:
                    remaining = p["inventory"] - (p.get("sold_count") or 0)
                    st.caption(f"{max(remaining, 0)} of {p['inventory']} left")

if docs:
    st.markdown("**Deck / brief**")
    for a in docs:
        url = storage.signed_url(a["storage_path"])
        if url:
            st.markdown(f"- [{a['filename']}]({url})")
        else:
            data = storage.fetch_bytes(a["storage_path"])
            if data:
                st.download_button(a["filename"], data=data, file_name=a["filename"])

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Offer form (requires login)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Send an offer")
user = auth.current_user()
if not user:
    st.info("Sign in as a sponsor to make an offer.")
    auth.require_login(role_hint="sponsor")  # renders inline + st.stop()

if user["role"] != "sponsor":
    st.warning("You're signed in as an organiser. Switch accounts to send offers.")
    st.stop()

with st.form("public_offer"):
    pkg_options = {f"{p['name']} — £{p['price_pennies'] / 100:,.0f}": p for p in packages}
    pkg_options["Custom amount"] = None
    choice = st.selectbox("Package", list(pkg_options.keys()))
    chosen = pkg_options[choice]
    default_pence = chosen["price_pennies"] if chosen else 50000
    amount_pounds = st.number_input(
        "Offer (£)", min_value=10, value=default_pence // 100, step=10,
    )
    note = st.text_area("Note to organiser", placeholder="What you bring + any asks")
    if st.form_submit_button("Send offer", type="primary", use_container_width=True):
        offer = db.create_offer(
            event_id=event["id"],
            sponsor_org_id=user["org_id"],
            package_id=chosen["id"] if chosen else None,
            amount_pennies=int(amount_pounds * 100),
            note=note.strip(),
        )
        st.success("Offer sent. The organiser has been notified.")
        # Best-effort notification — silent if creds aren't set
        notify_new_offer(
            organiser_email=event.get("_organiser_email", ""),
            organiser_phone=event.get("_organiser_phone"),
            sponsor_name=user.get("display_name") or user["email"],
            event_name=event["name"],
            amount_pennies=int(amount_pounds * 100),
            event_slug=event["slug"],
        )
