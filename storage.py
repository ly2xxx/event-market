"""
Supabase Storage helper for asset uploads.

Bucket "assets" is private. Files are namespaced by user id so RLS on the
metadata table mirrors RLS on the storage object naturally.

Demo mode keeps the bytes in-memory so the upload UI works without a
Supabase project — useful for local prototyping but obviously not durable.
"""
from __future__ import annotations

import uuid
from typing import Optional

import streamlit as st

import db

BUCKET = "assets"
SIGNED_URL_TTL = 60 * 60  # 1h


def _key(owner_id: str, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"{owner_id}/{uuid.uuid4().hex}.{ext}"


def upload(
    *, owner_id: str, file_bytes: bytes, filename: str, mime: str,
    offer_id: Optional[str] = None, event_id: Optional[str] = None,
    kind: str = "other",
) -> dict:
    """Upload bytes to Storage and record an `assets` row. Returns the asset row."""
    storage_path = _key(owner_id, filename)

    if db.is_live():
        client = db.client()
        client.storage.from_(BUCKET).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": mime, "upsert": "false"},
        )
    else:
        # demo: stash bytes in session_state under their key
        st.session_state.setdefault("demo_blobs", {})[storage_path] = file_bytes

    return db.record_asset({
        "owner_id": owner_id,
        "offer_id": offer_id,
        "event_id": event_id,
        "storage_path": storage_path,
        "filename": filename,
        "mime_type": mime,
        "size_bytes": len(file_bytes),
        "kind": kind,
    })


def signed_url(storage_path: str) -> Optional[str]:
    """Return a temporary URL for a private object. None in demo mode."""
    if not db.is_live():
        return None
    try:
        resp = db.client().storage.from_(BUCKET).create_signed_url(storage_path, SIGNED_URL_TTL)
        return resp.get("signedURL") or resp.get("signed_url")
    except Exception:
        return None


def fetch_bytes(storage_path: str) -> Optional[bytes]:
    """Demo-mode fallback so st.download_button works without Supabase."""
    if not db.is_live():
        return st.session_state.get("demo_blobs", {}).get(storage_path)
    try:
        return db.client().storage.from_(BUCKET).download(storage_path)
    except Exception:
        return None
