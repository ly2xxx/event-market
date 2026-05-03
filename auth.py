"""
Email-OTP authentication.

True magic-link auth in Streamlit is awkward — Supabase puts the access
token in the URL hash fragment, which Streamlit can't read server-side.
So we use the same Supabase auth endpoint in OTP mode: the user gets a
6-digit code by email and enters it in the app.

In demo mode (no Supabase env vars) we accept any email + the literal
code "000000" so the rest of the app can be exercised offline.
"""
from __future__ import annotations

from typing import Optional

import streamlit as st

import db


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def current_user() -> Optional[dict]:
    """Returns {id, email, role, org_id} or None."""
    return st.session_state.get("user")


def require_login(role_hint: str = "organiser") -> dict:
    """Render the login UI inline if needed; return the user dict once signed in."""
    user = current_user()
    if user:
        return user

    _render_login_box(role_hint)
    st.stop()


def logout() -> None:
    if db.is_live():
        try:
            db.client().auth.sign_out()
        except Exception:
            pass
    for key in ("user", "sb_session"):
        st.session_state.pop(key, None)


# ─────────────────────────────────────────────────────────────────────────────
# OTP flow
# ─────────────────────────────────────────────────────────────────────────────
def _send_otp(email: str) -> None:
    if not db.is_live():
        st.session_state["pending_email"] = email
        st.info("Demo mode: enter code **000000** to sign in.")
        return
    db.client().auth.sign_in_with_otp({
        "email": email,
        "options": {"should_create_user": True},
    })
    st.session_state["pending_email"] = email
    st.success(f"Code sent to {email}. Check your inbox.")


def _verify_otp(email: str, code: str, display_name: str, role: str) -> bool:
    if not db.is_live():
        if code.strip() != "000000":
            st.error("Demo code is 000000.")
            return False
        user_id = f"demo-{role}-{abs(hash(email)) % 10_000_000}"
        org = db.get_or_create_org(user_id, display_name or email.split("@")[0], role)
        st.session_state.user = {
            "id": user_id,
            "email": email,
            "display_name": display_name,
            "role": role,
            "org_id": org["id"],
        }
        st.session_state.pop("pending_email", None)
        return True

    try:
        resp = db.client().auth.verify_otp({
            "email": email, "token": code.strip(), "type": "email",
        })
    except Exception as e:
        st.error(f"Invalid code: {e}")
        return False

    session = getattr(resp, "session", None)
    auth_user = getattr(resp, "user", None)
    if not session or not auth_user:
        st.error("Verification failed.")
        return False

    st.session_state.sb_session = session

    # Ensure a public.users row exists (RLS lets the user insert their own).
    admin = db.admin_client() or db.client()
    try:
        admin.from_("users").upsert({
            "id": auth_user.id,
            "email": email,
            "display_name": display_name or email.split("@")[0],
            "role": role,
        }).execute()
    except Exception:
        pass  # already exists

    org = db.get_or_create_org(auth_user.id, display_name or email.split("@")[0], role)
    st.session_state.user = {
        "id": auth_user.id,
        "email": email,
        "display_name": display_name or email.split("@")[0],
        "role": role,
        "org_id": org["id"],
    }
    st.session_state.pop("pending_email", None)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────
def _render_login_box(role_hint: str) -> None:
    st.markdown("### Sign in")
    st.caption(
        "We email you a 6-digit code. No password. "
        f"({'Live mode' if db.is_live() else 'Demo mode — code is 000000'})"
    )

    pending = st.session_state.get("pending_email")
    with st.container(border=True):
        if not pending:
            with st.form("otp_request"):
                email = st.text_input("Email", placeholder="you@example.com")
                role = st.selectbox(
                    "I am a…",
                    ["organiser", "sponsor"],
                    index=0 if role_hint == "organiser" else 1,
                )
                display_name = st.text_input(
                    "Display name (optional)",
                    placeholder="Your name or brand",
                )
                if st.form_submit_button("Send code", type="primary", use_container_width=True):
                    if not email or "@" not in email:
                        st.error("Enter a valid email.")
                    else:
                        st.session_state["pending_role"] = role
                        st.session_state["pending_name"] = display_name
                        _send_otp(email.strip().lower())
                        st.rerun()
        else:
            st.write(f"Code sent to **{pending}**.")
            with st.form("otp_verify"):
                code = st.text_input("6-digit code", max_chars=6)
                cols = st.columns(2)
                submit = cols[0].form_submit_button("Verify", type="primary", use_container_width=True)
                back = cols[1].form_submit_button("Use a different email", use_container_width=True)
                if submit:
                    if _verify_otp(
                        pending, code,
                        st.session_state.get("pending_name", ""),
                        st.session_state.get("pending_role", role_hint),
                    ):
                        st.rerun()
                if back:
                    st.session_state.pop("pending_email", None)
                    st.rerun()
