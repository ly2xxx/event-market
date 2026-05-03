"""
Outbound notifications: email (Resend) + WhatsApp (Twilio).

Both are no-op when their env vars are missing, so the app always works
locally and any channel can be enabled independently.

Env vars:
    RESEND_API_KEY            — required for email
    NOTIFICATIONS_FROM_EMAIL  — e.g. "marketplace@yourdomain.com"
    TWILIO_ACCOUNT_SID        — required for WhatsApp
    TWILIO_AUTH_TOKEN         — required for WhatsApp
    TWILIO_WHATSAPP_FROM      — e.g. "whatsapp:+14155238886" (sandbox)
    PUBLIC_BASE_URL           — used to build shareable links in messages
"""
from __future__ import annotations

import logging
import os
from typing import Optional

log = logging.getLogger("notifications")


def _env(key: str) -> Optional[str]:
    return os.environ.get(key) or None


def public_url(path: str = "/") -> str:
    base = _env("PUBLIC_BASE_URL") or "http://localhost:8501"
    return f"{base.rstrip('/')}{path}"


# ─────────────────────────────────────────────────────────────────────────────
# Email (Resend)
# ─────────────────────────────────────────────────────────────────────────────
def send_email(to: str, subject: str, html: str) -> bool:
    api_key = _env("RESEND_API_KEY")
    sender = _env("NOTIFICATIONS_FROM_EMAIL")
    if not api_key or not sender:
        log.info("email skipped (no RESEND_API_KEY): to=%s subject=%s", to, subject)
        return False
    try:
        import resend  # type: ignore
        resend.api_key = api_key
        resend.Emails.send({
            "from": sender, "to": to, "subject": subject, "html": html,
        })
        return True
    except Exception as e:
        log.warning("email failed: %s", e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# WhatsApp (Twilio)
# ─────────────────────────────────────────────────────────────────────────────
def send_whatsapp(to_phone: str, body: str) -> bool:
    sid = _env("TWILIO_ACCOUNT_SID")
    token = _env("TWILIO_AUTH_TOKEN")
    sender = _env("TWILIO_WHATSAPP_FROM")
    if not (sid and token and sender):
        log.info("whatsapp skipped (no TWILIO_*): to=%s", to_phone)
        return False
    try:
        from twilio.rest import Client  # type: ignore
        Client(sid, token).messages.create(
            from_=sender,
            to=f"whatsapp:{to_phone}" if not to_phone.startswith("whatsapp:") else to_phone,
            body=body,
        )
        return True
    except Exception as e:
        log.warning("whatsapp failed: %s", e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# High-level events (one function per business event keeps callers tidy)
# ─────────────────────────────────────────────────────────────────────────────
def notify_new_offer(*, organiser_email: str, organiser_phone: Optional[str],
                     sponsor_name: str, event_name: str, amount_pennies: int,
                     event_slug: str) -> None:
    amount = f"£{amount_pennies / 100:,.0f}"
    link = public_url(f"/event?slug={event_slug}")
    subject = f"New sponsor offer for {event_name}"
    html = f"""
        <p>You've got a new offer.</p>
        <ul>
            <li><b>Sponsor:</b> {sponsor_name}</li>
            <li><b>Event:</b> {event_name}</li>
            <li><b>Amount:</b> {amount}</li>
        </ul>
        <p><a href="{link}">Review the offer →</a></p>
    """
    send_email(organiser_email, subject, html)
    if organiser_phone:
        send_whatsapp(
            organiser_phone,
            f"New offer for {event_name}: {sponsor_name} — {amount}. {link}",
        )


def notify_offer_accepted(*, sponsor_email: str, sponsor_phone: Optional[str],
                          event_name: str, amount_pennies: int, event_slug: str) -> None:
    amount = f"£{amount_pennies / 100:,.0f}"
    link = public_url(f"/event?slug={event_slug}")
    subject = f"Your offer for {event_name} was accepted"
    html = f"""
        <p>Good news — your {amount} offer for <b>{event_name}</b> was accepted.</p>
        <p><a href="{link}">Open the deal →</a></p>
    """
    send_email(sponsor_email, subject, html)
    if sponsor_phone:
        send_whatsapp(
            sponsor_phone,
            f"Accepted: {event_name} — {amount}. {link}",
        )


def notify_new_message(*, recipient_email: str, recipient_phone: Optional[str],
                       sender_name: str, event_name: str, preview: str,
                       event_slug: str) -> None:
    link = public_url(f"/event?slug={event_slug}")
    subject = f"{sender_name} replied about {event_name}"
    html = f"""
        <p><b>{sender_name}</b> sent you a message about <b>{event_name}</b>:</p>
        <blockquote>{preview[:200]}</blockquote>
        <p><a href="{link}">Open thread →</a></p>
    """
    send_email(recipient_email, subject, html)
    if recipient_phone:
        send_whatsapp(
            recipient_phone,
            f"{sender_name} re: {event_name}: {preview[:120]} {link}",
        )
