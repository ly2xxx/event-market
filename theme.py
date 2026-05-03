"""
Shared dark theme — kept identical to the HTML prototype so the Streamlit
app and the public event page look the same.
"""
import streamlit as st

_CSS = """
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(1200px 800px at 20% -10%, rgba(124,92,255,.18), transparent 55%),
                radial-gradient(900px 700px at 100% 10%, rgba(42,212,255,.12), transparent 55%),
                linear-gradient(180deg, #0b0d12, #070810);
}
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #0f1322; }

html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, label,
.stTextInput>div>div>input, .stSelectbox, .stTextArea textarea {
    color: #e7e9ee !important;
}

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

[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(15,19,34,.85) !important;
    border: 1px solid #222a41 !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 26px rgba(0,0,0,.18) !important;
}

.stTextInput>div>div>input,
.stTextArea textarea,
.stSelectbox>div>div {
    background: rgba(11,13,18,.55) !important;
    border: 1px solid #222a41 !important;
    border-radius: 14px !important;
    color: #e7e9ee !important;
}

[data-testid="stMetric"] {
    background: rgba(15,19,34,.85);
    border: 1px solid #222a41;
    border-radius: 16px;
    padding: 12px;
}
[data-testid="stMetricLabel"] { color: #a7afc2 !important; }
[data-testid="stMetricValue"] { color: #e7e9ee !important; font-weight: 700; }

hr { border-color: #222a41 !important; }
.stCaption, small { color: #a7afc2 !important; }

.mp-pill {
    display: inline-block; font-size: 11px; color: #a7afc2;
    border: 1px solid #222a41; padding: 4px 10px;
    border-radius: 999px; background: rgba(11,13,18,.4); margin: 2px;
}
.mp-header { display: flex; align-items: center; gap: 12px; padding: 12px 0 4px 0; }
.mp-logo {
    width: 36px; height: 36px; border-radius: 12px;
    background: linear-gradient(135deg, #7c5cff, #2ad4ff);
    box-shadow: 0 10px 24px rgba(124,92,255,.25); flex-shrink: 0;
}
.mp-brand-text strong { font-size: 15px; display: block; }
.mp-brand-text span { font-size: 12px; color: #a7afc2; }

.badge-pending  { background:rgba(255,204,102,.14); border:1px solid rgba(255,204,102,.35); color:#ffcc66; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; }
.badge-accepted { background:rgba(57,217,138,.14);  border:1px solid rgba(57,217,138,.35);  color:#39d98a; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; }
.badge-declined { background:rgba(255,92,122,.12);  border:1px solid rgba(255,92,122,.35);  color:#ff5c7a; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; }

.msg-bubble-me { background: rgba(124,92,255,.18); border: 1px solid rgba(124,92,255,.35);
                 border-radius: 14px; padding: 10px 12px; margin: 4px 0; }
.msg-bubble-them { background: rgba(15,19,34,.85); border: 1px solid #222a41;
                   border-radius: 14px; padding: 10px 12px; margin: 4px 0; }
.msg-meta { font-size: 11px; color: #a7afc2; margin-top: 4px; }
</style>
"""


def inject() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def header() -> None:
    st.markdown(
        """
        <div class="mp-header">
          <div class="mp-logo"></div>
          <div class="mp-brand-text">
            <strong>Event Sponsor Marketplace</strong>
            <span>Match events with sponsors — without the DM chaos</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    cls = {
        "sent": "badge-pending", "pending": "badge-pending",
        "accepted": "badge-accepted", "confirmed": "badge-accepted",
        "declined": "badge-declined", "withdrawn": "badge-declined",
    }.get((status or "").lower(), "badge-pending")
    return f'<span class="{cls}">{status.upper()}</span>'
