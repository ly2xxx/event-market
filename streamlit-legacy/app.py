"""
Event Sponsor Marketplace — Streamlit MVP
Run:  uv run streamlit run app.py
"""
import random
import string
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Event Sponsor Marketplace",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (dark theme matching the HTML prototype) ───────────────────────
st.markdown(
    """
<style>
/* ── Global dark background ── */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(1200px 800px at 20% -10%, rgba(124,92,255,.18), transparent 55%),
                radial-gradient(900px 700px at 100% 10%, rgba(42,212,255,.12), transparent 55%),
                linear-gradient(180deg, #0b0d12, #070810);
}
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #0f1322; }

/* ── Main text ── */
html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, label,
.stTextInput>div>div>input, .stSelectbox, .stTextArea textarea {
    color: #e7e9ee !important;
}

/* ── Nav pill buttons ── */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background: rgba(15,19,34,.8) !important;
    border: 1px solid #222a41 !important;
    color: #a7afc2 !important;
    border-radius: 999px !important;
    transition: .15s ease;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #2a355a !important;
    color: #e7e9ee !important;
}
div[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background: linear-gradient(135deg, rgba(124,92,255,.9), rgba(42,212,255,.55)) !important;
    border: none !important;
    border-radius: 999px !important;
}

/* ── Cards / containers ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(15,19,34,.85) !important;
    border: 1px solid #222a41 !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 26px rgba(0,0,0,.18) !important;
}

/* ── Inputs ── */
.stTextInput>div>div>input,
.stTextArea textarea,
.stSelectbox>div>div {
    background: rgba(11,13,18,.55) !important;
    border: 1px solid #222a41 !important;
    border-radius: 14px !important;
    color: #e7e9ee !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(15,19,34,.85);
    border: 1px solid #222a41;
    border-radius: 16px;
    padding: 12px;
}
[data-testid="stMetricLabel"] { color: #a7afc2 !important; }
[data-testid="stMetricValue"] { color: #e7e9ee !important; font-weight: 700; }

/* ── Divider ── */
hr { border-color: #222a41 !important; }

/* ── Caption / muted text ── */
.stCaption, small { color: #a7afc2 !important; }

/* ── Pill badges ── */
.mp-pill {
    display: inline-block;
    font-size: 11px;
    color: #a7afc2;
    border: 1px solid #222a41;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(11,13,18,.4);
    margin: 2px;
}

/* ── Brand header ── */
.mp-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0 4px 0;
}
.mp-logo {
    width: 36px; height: 36px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7c5cff, #2ad4ff);
    box-shadow: 0 10px 24px rgba(124,92,255,.25);
    flex-shrink: 0;
}
.mp-brand-text strong { font-size: 15px; display: block; }
.mp-brand-text span { font-size: 12px; color: #a7afc2; }

/* ── Status badges ── */
.badge-pending  { background:rgba(255,204,102,.14); border:1px solid rgba(255,204,102,.35); color:#ffcc66; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; }
.badge-accepted { background:rgba(57,217,138,.14);  border:1px solid rgba(57,217,138,.35);  color:#39d98a; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; }
.badge-declined { background:rgba(255,92,122,.12);  border:1px solid rgba(255,92,122,.35);  color:#ff5c7a; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Constants ─────────────────────────────────────────────────────────────────
PACKAGES: dict[str, dict] = {
    "Bronze": {"price": 250,  "benefits": "Logo on flyer • 1 IG story mention"},
    "Silver": {"price": 500,  "benefits": "Logo on flyer • MC shoutout • 1 post tag"},
    "Gold":   {"price": 1000, "benefits": "Booth • content bundle • headline mention"},
    "Custom": {"price": 750,  "benefits": "Custom deliverables (as agreed)"},
}

EVENT_TYPES   = ["Afrobeats", "Amapiano", "Culture / Community", "Corporate", "Festival"]
AUDIENCE_SIZES = ["100-200", "200-500", "500-1000", "1000+"]
BUDGET_RANGES  = ["£100-£300", "£300-£1,000", "£1,000-£5,000", "£5,000+"]

STATIC_EVENTS = [
    {"id": "e2", "name": "Amapiano Terrace",       "city": "Edinburgh", "type": "Amapiano",          "size": "100-200",  "date": "TBA", "pitch": "Sunset terrace vibe + content-heavy crowd."},
    {"id": "e3", "name": "Culture & Community Mkt", "city": "Glasgow",   "type": "Culture / Community","size": "500-1000", "date": "TBA", "pitch": "Family friendly, diaspora brands, strong community presence."},
    {"id": "e4", "name": "Corporate Afterhours",   "city": "London",    "type": "Corporate",          "size": "200-500",  "date": "TBA", "pitch": "Young professionals, high spending power."},
]


# ── Session-state initialisation ─────────────────────────────────────────────
def _init() -> None:
    if "initialized" in st.session_state:
        return
    st.session_state.update(
        {
            "initialized": True,
            "page": "Home",
            "notification": None,
            # ── Event ──
            "event": {
                "name":     "Afro Vibes Night",
                "city":     "Glasgow",
                "evt_date": None,
                "size":     "200-500",
                "type":     "Afrobeats",
                "pitch":    "High-energy Afro night. 70% students + young professionals. Heavy IG content.",
                "packages": ["Bronze", "Silver", "Gold"],
            },
            # ── Brand ──
            "brand": {"name": "Pulse Drinks", "budget": "£300-£1,000", "industry": "Beverage"},
            # ── Deal ──
            "selected_package": "Silver",
            "deal": {"status": "PENDING", "notes": ""},
            # ── Lists ──
            "offers": [
                {"id": "off_1", "event": "Afro Vibes Night", "sponsor": "Pulse Drinks",
                 "package": "Silver", "amount": 500, "status": "SENT"},
            ],
            "inbox": [
                {"id": "msg_1", "from": "Pulse Drinks",  "about": "Afro Vibes Night",
                 "package": "Silver", "amount": 500, "note": "We can sponsor + provide free cans for VIP."},
                {"id": "msg_2", "from": "Streetwear Co", "about": "Afro Vibes Night",
                 "package": "Bronze", "amount": 250, "note": "Logo + giveaway collab?"},
            ],
            "approvals": [
                {"id": "ap_1", "type": "Event",   "name": "Afro Vibes Night", "status": "PENDING"},
                {"id": "ap_2", "type": "Sponsor", "name": "Pulse Drinks",    "status": "PENDING"},
            ],
            # ── UI visibility toggles ──
            "show_packages": False,
            "show_inbox":    False,
            "show_brand":    False,
            "show_offers":   False,
        }
    )


_init()


# ── Utility helpers ───────────────────────────────────────────────────────────
def nav(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def notify(title: str, msg: str, kind: str = "success") -> None:
    st.session_state.notification = {"title": title, "msg": msg, "kind": kind}


def get_catalogue() -> list[dict]:
    ev = st.session_state.event
    live_event = {
        "id":    "e1",
        "name":  ev["name"],
        "city":  ev["city"],
        "type":  ev["type"],
        "size":  ev["size"],
        "date":  str(ev["evt_date"]) if ev["evt_date"] else "TBA",
        "pitch": ev["pitch"],
    }
    return [live_event] + STATIC_EVENTS


def _rand_id(prefix: str = "off_") -> str:
    return prefix + "".join(random.choices(string.hexdigits[:16], k=5))


def status_badge(status: str) -> str:
    cls = {
        "PENDING":  "badge-pending",
        "ACCEPTED": "badge-accepted",
        "DECLINED": "badge-declined",
    }.get(status, "badge-pending")
    return f'<span class="{cls}">{status}</span>'


# ── Header ────────────────────────────────────────────────────────────────────
def render_header() -> None:
    st.markdown(
        """
        <div class="mp-header">
          <div class="mp-logo"></div>
          <div class="mp-brand-text">
            <strong>Event Sponsor Marketplace</strong>
            <span>Streamlit MVP demo</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pages = ["Home", "Organiser", "Sponsor", "Deal", "Admin"]
    _, *cols, _ = st.columns([0.5] + [1] * len(pages) + [0.5])
    for col, p in zip(cols, pages):
        with col:
            is_active = st.session_state.page == p
            if st.button(
                p,
                key=f"nav_{p}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                nav(p)


# ── Notification banner ───────────────────────────────────────────────────────
def show_notification() -> None:
    notif = st.session_state.notification
    if not notif:
        return
    kind, title, msg = notif["kind"], notif["title"], notif["msg"]
    text = f"**{title}** — {msg}"
    {"success": st.success, "warning": st.warning, "error": st.error}.get(kind, st.info)(text)
    st.session_state.notification = None


# ── HOME ──────────────────────────────────────────────────────────────────────
def page_home() -> None:
    left, right = st.columns([4, 7], gap="large")

    with left:
        st.markdown("### Quick actions")
        m1, m2 = st.columns(2)
        m1.metric("Events live", 6)
        m2.metric("Sponsor leads", len(st.session_state.inbox))

        st.caption(
            "Clickable demo (no backend). Test the full flow: "
            "organiser lists an event → sponsor sends offer → organiser accepts."
        )
        st.divider()

        if st.button("＋ Create event",  key="h_create",  use_container_width=True, type="primary"):
            nav("Organiser")
        if st.button("Browse events",   key="h_browse",  use_container_width=True):
            nav("Sponsor")
        if st.button("Make offer",      key="h_offer",   use_container_width=True):
            nav("Deal")

        st.divider()
        st.caption("Tip: use the top pills to jump screens. Everything is demo data.")

    with right:
        st.markdown("### What's the goal?")
        st.info(
            "Match **events** with **sponsors** without IG DMs + WhatsApp chaos.",
            icon="🎯",
        )

        c1, c2 = st.columns(2, gap="medium")

        with c1:
            with st.container(border=True):
                st.markdown("**I'm an Organiser**")
                st.caption("List your event + packages, receive sponsor offers, accept deals.")
                ga, ld = st.columns(2)
                with ga:
                    if st.button("Go →", key="h_org", use_container_width=True, type="primary"):
                        nav("Organiser")
                with ld:
                    if st.button("Load demo", key="h_org_demo", use_container_width=True):
                        notify("Loaded", "Demo event is pre-filled.")
                        nav("Organiser")

        with c2:
            with st.container(border=True):
                st.markdown("**I'm a Sponsor**")
                st.caption("Filter events, view packages, send an offer in 30 seconds.")
                ga, ld = st.columns(2)
                with ga:
                    if st.button("Go →", key="h_sp", use_container_width=True, type="primary"):
                        nav("Sponsor")
                with ld:
                    if st.button("Load demo", key="h_sp_demo", use_container_width=True):
                        notify("Loaded", "Demo brand is pre-filled.")
                        nav("Sponsor")

        st.divider()

        with st.container(border=True):
            st.markdown("**What's inside this prototype**")
            st.caption("Minimal, but end-to-end clickable.")
            features = [
                "Create event", "Add packages", "Browse events + filters",
                "Send offer", "Accept deal", "Admin approve",
            ]
            pills_html = "".join(f'<span class="mp-pill">{f}</span>' for f in features)
            st.markdown(pills_html, unsafe_allow_html=True)


# ── ORGANISER ────────────────────────────────────────────────────────────────
def page_organiser() -> None:
    ev = st.session_state.event
    left, right = st.columns([4, 7], gap="large")

    with left:
        st.markdown("### Organiser actions")
        st.caption("Build your listing")

        with st.container(border=True):
            st.markdown(f"**Event:** {ev['name']}")
            st.markdown(f"**City:** {ev['city']}")
            st.markdown(f"**Packages:** {', '.join(ev['packages'])}")

        st.divider()

        inbox_label = f"Inbox ({len(st.session_state.inbox)})"
        if st.button(inbox_label,        key="org_inbox_btn", use_container_width=True):
            st.session_state.show_inbox = not st.session_state.show_inbox
            st.rerun()
        if st.button("Preview as Sponsor", key="org_preview",  use_container_width=True):
            nav("Sponsor")
        if st.button("↺ Reset demo",      key="org_reset",    use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    with right:
        st.markdown("### Create / manage event")
        st.caption("Fill the basics. Save. Add packages. Done.")

        with st.container(border=True):
            with st.form("event_form"):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Event name", value=ev["name"],
                                         placeholder="e.g., Afro Vibes Night")
                with c2:
                    city = st.text_input("City", value=ev["city"],
                                          placeholder="e.g., Glasgow")

                c3, c4 = st.columns(2)
                with c3:
                    evt_date = st.date_input("Date", value=ev["evt_date"])
                with c4:
                    size = st.selectbox("Audience size", AUDIENCE_SIZES,
                                         index=AUDIENCE_SIZES.index(ev["size"]))

                evt_type = st.selectbox("Vibe / type", EVENT_TYPES,
                                         index=EVENT_TYPES.index(ev["type"]))

                pitch = st.text_area(
                    "Quick pitch", value=ev["pitch"],
                    placeholder="Why should a sponsor care? Who's attending? What's the vibe?",
                )

                fc1, fc2, fc3 = st.columns(3)
                save_evt  = fc1.form_submit_button("Save event",    use_container_width=True, type="primary")
                add_pkgs  = fc2.form_submit_button("Add packages",  use_container_width=True)
                prev_sp   = fc3.form_submit_button("Preview →",     use_container_width=True)

                if save_evt:
                    ev.update(
                        name=name.strip() or "Untitled Event",
                        city=city.strip() or "Unknown",
                        evt_date=evt_date,
                        size=size,
                        type=evt_type,
                        pitch=pitch.strip() or "No pitch yet.",
                    )
                    notify("Saved", "Event listing updated.")
                    st.rerun()

                if add_pkgs:
                    st.session_state.show_packages = True
                    notify("Packages", "Pick a tier below.", "info")
                    st.rerun()

                if prev_sp:
                    nav("Sponsor")

            st.caption("Once saved it appears in the sponsor browse list.")

        # ── Packages section ──
        if st.session_state.show_packages:
            st.markdown("#### Sponsorship packages")
            st.caption("Give sponsors clear tiers. Less negotiation. More deals.")

            pkg_cols = st.columns(2, gap="medium")
            for i, (pkg_name, pkg_data) in enumerate(PACKAGES.items()):
                with pkg_cols[i % 2]:
                    with st.container(border=True):
                        if pkg_name == "Custom":
                            st.markdown("**Custom**")
                            st.caption("You want something spicy? Write it.")
                            st.text_input("Custom package text", key="custom_pkg",
                                           placeholder="e.g., Drinks partnership + branded cups")
                        else:
                            st.markdown(f"**{pkg_name} — £{pkg_data['price']}**")
                            st.caption(pkg_data["benefits"])

                        if st.button(f"Use {pkg_name}", key=f"pkg_{pkg_name}", use_container_width=True):
                            st.session_state.selected_package = pkg_name
                            if pkg_name not in ev["packages"]:
                                ev["packages"].append(pkg_name)
                            notify("Selected", f"Package set to {pkg_name}.")
                            st.rerun()

        # ── Inbox section ──
        if st.session_state.show_inbox:
            st.markdown("#### Inbox")
            st.caption("Sponsor enquiries land here.")

            for msg in st.session_state.inbox:
                with st.container(border=True):
                    ic1, ic2 = st.columns([3, 1])
                    with ic1:
                        st.markdown(f"**{msg['from']}**")
                        st.caption(
                            f"About: {msg['about']} • Package: {msg['package']} • Offer: £{msg['amount']}"
                        )
                        st.write(msg["note"])
                    with ic2:
                        if st.button("Open deal", key=f"inbox_deal_{msg['id']}", use_container_width=True):
                            st.session_state.brand["name"] = msg["from"]
                            st.session_state.selected_package = msg["package"]
                            st.session_state.deal["status"] = "PENDING"
                            notify("Deal opened", "Ready to accept / decline.")
                            nav("Deal")


# ── SPONSOR ───────────────────────────────────────────────────────────────────
def page_sponsor() -> None:
    left, right = st.columns([4, 7], gap="large")
    br = st.session_state.brand

    with left:
        st.markdown("### Sponsor actions")
        st.caption("Filter + offer")

        with st.container(border=True):
            st.markdown(f"**Brand:** {br['name']}")
            st.markdown(f"**Budget:** {br['budget']}")
            st.markdown(f"**Industry:** {br['industry']}")

        st.divider()

        if st.button("Brand Profile",                              key="sp_brand_btn",  use_container_width=True):
            st.session_state.show_brand = not st.session_state.show_brand
            st.rerun()
        offer_count = len(st.session_state.offers)
        if st.button(f"My Offers ({offer_count})",                 key="sp_offers_btn", use_container_width=True):
            st.session_state.show_offers = not st.session_state.show_offers
            st.rerun()
        if st.button("Go to Deal view",                            key="sp_deal",       use_container_width=True):
            nav("Deal")

    with right:
        st.markdown("### Browse events")
        st.caption("Filters are the whole point. Find the right crowd fast.")

        # ── Filter bar ──
        with st.container(border=True):
            fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
            filter_city = fc1.text_input("City",  placeholder="Filter by city",  label_visibility="collapsed",
                                          key="filter_city")
            filter_type = fc2.selectbox("Type",  ["All types"] + EVENT_TYPES,   label_visibility="collapsed",
                                          key="filter_type")
            filter_size = fc3.selectbox("Size",  ["Any size"]  + AUDIENCE_SIZES, label_visibility="collapsed",
                                          key="filter_size")
            apply_btn   = fc4.button("Apply", use_container_width=True, type="primary", key="filter_apply")
            if apply_btn:
                notify("Filtered", "Showing matching events.", "info")
                st.rerun()
            st.caption("Click an event card to view packages + send offer.")

        # ── Event catalogue ──
        catalogue = get_catalogue()
        filtered = [
            e for e in catalogue
            if (not filter_city or filter_city.lower() in e["city"].lower())
            and (filter_type == "All types" or e["type"] == filter_type)
            and (filter_size == "Any size"  or e["size"] == filter_size)
        ]

        if not filtered:
            st.warning("No matches. Try removing a filter.")
        else:
            for evt in filtered:
                with st.container(border=True):
                    top, btn = st.columns([3, 1])
                    with top:
                        st.markdown(f"**{evt['name']}**")
                        st.caption(
                            f"{evt['city']} • {evt['type']} • Audience {evt['size']} • Date: {evt['date']}"
                        )
                        st.write(evt["pitch"])
                        pkgs = ", ".join(st.session_state.event["packages"])
                        st.markdown(
                            f'<span class="mp-pill">Packages: {pkgs}</span>',
                            unsafe_allow_html=True,
                        )
                    with btn:
                        if st.button("Send offer", key=f"send_offer_{evt['id']}",
                                     use_container_width=True, type="primary"):
                            pkg    = st.session_state.selected_package
                            amount = PACKAGES[pkg]["price"]
                            st.session_state.offers.insert(0, {
                                "id":      _rand_id(),
                                "event":   evt["name"],
                                "sponsor": br["name"],
                                "package": pkg,
                                "amount":  amount,
                                "status":  "SENT",
                            })
                            notify("Offer sent", f"Sent {pkg} offer for £{amount}.")
                            st.session_state.show_offers = True
                            st.rerun()

                        if st.button("Go to deal", key=f"go_deal_{evt['id']}",
                                     use_container_width=True):
                            nav("Deal")

        # ── Brand profile panel ──
        if st.session_state.show_brand:
            st.markdown("#### Brand profile")
            st.caption("Just enough info to match you correctly.")
            with st.container(border=True):
                with st.form("brand_form"):
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        brand_name = st.text_input("Brand name", value=br["name"],
                                                    placeholder="e.g., Red Bull")
                    with bc2:
                        brand_budget = st.selectbox(
                            "Budget range", BUDGET_RANGES,
                            index=BUDGET_RANGES.index(br["budget"]),
                        )
                    brand_industry = st.text_input(
                        "Industry", value=br["industry"],
                        placeholder="e.g., Beverage, Fashion, Tech",
                    )
                    sb, cb = st.columns(2)
                    save_brand  = sb.form_submit_button("Save brand", use_container_width=True, type="primary")
                    close_brand = cb.form_submit_button("Close",      use_container_width=True)

                    if save_brand:
                        br.update(
                            name=brand_name.strip() or "Unnamed Brand",
                            budget=brand_budget,
                            industry=brand_industry.strip() or "Unknown",
                        )
                        notify("Saved", "Brand profile updated.")
                        st.rerun()
                    if close_brand:
                        st.session_state.show_brand = False
                        st.rerun()

        # ── My offers panel ──
        if st.session_state.show_offers:
            st.markdown("#### My offers")
            st.caption("Offers you've sent.")
            with st.container(border=True):
                for offer in st.session_state.offers:
                    oc1, oc2 = st.columns([3, 1])
                    with oc1:
                        st.markdown(f"**{offer['event']}**")
                        st.caption(
                            f"Sponsor: {offer['sponsor']} • Package: {offer['package']} "
                            f"• £{offer['amount']} • Status: {offer['status']}"
                        )
                    with oc2:
                        if st.button("View", key=f"view_offer_{offer['id']}", use_container_width=True):
                            nav("Deal")
                    st.divider()
                if st.button("Close offers", key="close_offers", use_container_width=True):
                    st.session_state.show_offers = False
                    st.rerun()


# ── DEAL ──────────────────────────────────────────────────────────────────────
def page_deal() -> None:
    ev   = st.session_state.event
    br   = st.session_state.brand
    pkg  = st.session_state.selected_package
    deal = st.session_state.deal

    left, right = st.columns([4, 7], gap="large")

    with left:
        st.markdown("### Deal actions")
        st.caption("Confirm the bag")

        status = deal["status"]
        badge  = status_badge(status)
        st.markdown(f"Current status: {badge}", unsafe_allow_html=True)
        st.divider()

        if st.button("✅ Accept deal", key="deal_accept",  use_container_width=True, type="primary"):
            deal["status"] = "ACCEPTED"
            notify("Accepted", "Deal confirmed (demo).", "success")
            st.rerun()
        if st.button("⏳ Set pending", key="deal_pending", use_container_width=True):
            deal["status"] = "PENDING"
            notify("Pending", "Deal set to pending.", "warning")
            st.rerun()
        if st.button("❌ Decline",     key="deal_decline", use_container_width=True):
            deal["status"] = "DECLINED"
            notify("Declined", "Deal declined.", "error")
            st.rerun()

        st.divider()
        if st.button("View in Admin", key="deal_to_admin", use_container_width=True):
            nav("Admin")

    with right:
        st.markdown("### Deal")
        st.caption("Sponsor sends offer → organiser accepts → deal confirmed.")

        with st.container(border=True):
            hc1, hc2 = st.columns([3, 1])
            with hc1:
                st.markdown(f"**{ev['name']} × {br['name']}**")
                st.caption(
                    f"Package: {pkg} — £{PACKAGES[pkg]['price']} "
                    f"• City: {ev['city']} • Audience: {ev['size']}"
                )
            with hc2:
                st.markdown(status_badge(deal["status"]), unsafe_allow_html=True)

            st.divider()

            dc1, dc2 = st.columns(2, gap="medium")
            with dc1:
                with st.container(border=True):
                    st.markdown("**What sponsor gets**")
                    st.caption(PACKAGES[pkg]["benefits"])
            with dc2:
                with st.container(border=True):
                    st.markdown("**What organiser needs**")
                    st.caption("Payment confirmed + deliverables agreed (basic contract later).")

            st.divider()

            with st.form("deal_notes"):
                notes = st.text_area(
                    "Notes (shared)", value=deal["notes"],
                    placeholder="Add logistics, assets deadline, booth size, etc.",
                )
                if st.form_submit_button("Save notes", use_container_width=True, type="primary"):
                    deal["notes"] = notes.strip()
                    notify("Saved", "Deal notes updated.")
                    st.rerun()

            st.caption("MVP: deal acceptance triggers confirmation email + invoice (later).")


# ── ADMIN ─────────────────────────────────────────────────────────────────────
def page_admin() -> None:
    ev   = st.session_state.event
    br   = st.session_state.brand
    deal = st.session_state.deal
    pkg  = st.session_state.selected_package

    left, right = st.columns([4, 7], gap="large")

    with left:
        st.markdown("### Admin actions")
        st.caption("Keep it clean")

        pending  = sum(1 for a in st.session_state.approvals if a["status"] == "PENDING")
        approved = sum(1 for a in st.session_state.approvals if a["status"] == "APPROVED")

        m1, m2 = st.columns(2)
        m1.metric("Pending",  pending)
        m2.metric("Approved", approved)

        st.divider()

        if st.button("✅ Approve all", key="admin_all", use_container_width=True, type="primary"):
            for a in st.session_state.approvals:
                a["status"] = "APPROVED"
            notify("Approved", "All approvals cleared.", "success")
            st.rerun()
        if st.button("🚩 Flag spam",  key="admin_spam", use_container_width=True):
            notify("Flagged", "Spam flagged (demo).", "warning")
            st.rerun()

    with right:
        st.markdown("### Admin")
        st.caption("Approve listings, kill spam, monitor deals.")

        ac1, ac2 = st.columns(2, gap="medium")

        with ac1:
            st.markdown("**Pending approvals**")
            st.caption("Events / Sponsors waiting for review.")

            for approval in st.session_state.approvals:
                with st.container(border=True):
                    apc1, apc2 = st.columns([2, 1])
                    with apc1:
                        st.markdown(f"**{approval['type']}: {approval['name']}**")
                        st.markdown(status_badge(approval["status"]), unsafe_allow_html=True)
                    with apc2:
                        if approval["status"] != "APPROVED":
                            if st.button("Approve", key=f"approve_{approval['id']}",
                                         use_container_width=True):
                                approval["status"] = "APPROVED"
                                notify("Approved", f"{approval['type']} approved.")
                                st.rerun()
                        else:
                            st.success("✓")

        with ac2:
            st.markdown("**Deals activity**")
            st.caption("Quick view of the pipeline.")

            with st.container(border=True):
                dac1, dac2 = st.columns([2, 1])
                with dac1:
                    st.markdown(f"**{ev['name']} × {br['name']}**")
                    st.caption(f"Package: {pkg}")
                    st.markdown(status_badge(deal["status"]), unsafe_allow_html=True)
                with dac2:
                    if st.button("Open", key="admin_open_deal", use_container_width=True):
                        nav("Deal")

            # All sent offers summary
            if st.session_state.offers:
                st.markdown("**All offers**")
                for o in st.session_state.offers:
                    st.caption(
                        f"• {o['event']} × {o['sponsor']} — {o['package']} £{o['amount']} [{o['status']}]"
                    )

        st.caption("Admin is basic on purpose. You can ship this fast.")


# ── Main entrypoint ───────────────────────────────────────────────────────────
def main() -> None:
    render_header()
    show_notification()
    st.divider()

    dispatch = {
        "Home":      page_home,
        "Organiser": page_organiser,
        "Sponsor":   page_sponsor,
        "Deal":      page_deal,
        "Admin":     page_admin,
    }
    dispatch.get(st.session_state.page, page_home)()


if __name__ == "__main__":
    main()
