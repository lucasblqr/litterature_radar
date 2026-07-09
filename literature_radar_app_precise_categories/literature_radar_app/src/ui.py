from __future__ import annotations

import streamlit as st


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --radar-bg: #f6f7fb;
            --radar-card: #ffffff;
            --radar-border: #e7e9f0;
            --radar-text: #172033;
            --radar-muted: #687083;
            --radar-blue: #244f8f;
            --radar-blue-soft: #eaf1fb;
            --radar-green: #216e5a;
            --radar-green-soft: #e9f5f1;
            --radar-orange: #a45c1a;
            --radar-orange-soft: #fff1e2;
            --radar-purple: #6a4ca3;
            --radar-purple-soft: #f0ebfa;
        }

        .stApp {
            background: linear-gradient(180deg, #f8f9fc 0%, #f3f5fa 100%);
            color: var(--radar-text);
        }

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--radar-border);
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
        }

        h1 {
            font-size: 2.15rem !important;
            margin-bottom: 0.35rem !important;
        }

        h2 {
            margin-top: 1.5rem !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        .radar-hero {
            padding: 1.45rem 1.65rem;
            border-radius: 22px;
            background:
                radial-gradient(circle at top left, rgba(36,79,143,0.16), transparent 30%),
                linear-gradient(135deg, #ffffff 0%, #f4f7fc 100%);
            border: 1px solid var(--radar-border);
            box-shadow: 0 16px 40px rgba(30, 42, 70, 0.07);
            margin-bottom: 1.2rem;
        }

        .radar-eyebrow {
            color: var(--radar-blue);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .radar-subtitle {
            color: var(--radar-muted);
            font-size: 1.02rem;
            max-width: 940px;
            line-height: 1.55;
            margin-top: 0.3rem;
        }

        .radar-card {
            background: var(--radar-card);
            border: 1px solid var(--radar-border);
            border-radius: 18px;
            padding: 1.08rem 1.18rem;
            box-shadow: 0 12px 28px rgba(30, 42, 70, 0.055);
            height: 100%;
            margin-bottom: 0.75rem;
        }

        .radar-card-title {
            font-weight: 800;
            font-size: 1.03rem;
            margin-bottom: 0.25rem;
            color: var(--radar-text);
        }

        .radar-card-text {
            color: var(--radar-muted);
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .radar-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 0.25rem 0.62rem;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            border: 1px solid transparent;
        }

        .pill-blue {
            background: var(--radar-blue-soft);
            color: var(--radar-blue);
            border-color: rgba(36,79,143,0.12);
        }

        .pill-green {
            background: var(--radar-green-soft);
            color: var(--radar-green);
            border-color: rgba(33,110,90,0.12);
        }

        .pill-orange {
            background: var(--radar-orange-soft);
            color: var(--radar-orange);
            border-color: rgba(164,92,26,0.12);
        }

        .pill-purple {
            background: var(--radar-purple-soft);
            color: var(--radar-purple);
            border-color: rgba(106,76,163,0.12);
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--radar-border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 28px rgba(30, 42, 70, 0.05);
        }

        div[data-testid="stMetric"] label {
            color: var(--radar-muted) !important;
            font-weight: 700;
        }

        div[data-testid="stMetricValue"] {
            color: var(--radar-text);
            font-weight: 850;
        }

        .stButton > button {
            border-radius: 999px;
            border: 1px solid rgba(36,79,143,0.24);
            background: #244f8f;
            color: white;
            font-weight: 750;
            padding: 0.56rem 1.08rem;
            box-shadow: 0 10px 24px rgba(36,79,143,0.20);
        }

        .stButton > button:hover {
            border: 1px solid rgba(36,79,143,0.4);
            background: #1f447b;
            color: white;
        }

        div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--radar-border);
            box-shadow: 0 12px 28px rgba(30, 42, 70, 0.05);
        }

        div[data-testid="stAlert"] {
            border-radius: 16px;
        }

        .radar-footer-note {
            color: var(--radar-muted);
            font-size: 0.88rem;
            margin-top: 0.6rem;
        }

        a {
            text-decoration: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _pill_html(pills: list[tuple[str, str]] | None) -> str:
    if not pills:
        return ""
    out = "<div style='margin-top:0.85rem;'>"
    for label, color in pills:
        out += f"<span class='radar-pill pill-{color}'>{label}</span>"
    out += "</div>"
    return out


def hero(title: str, subtitle: str, eyebrow: str = "Literature Radar", pills: list[tuple[str, str]] | None = None) -> None:
    st.markdown(
        f"""
        <div class="radar-hero">
            <div class="radar-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <div class="radar-subtitle">{subtitle}</div>
            {_pill_html(pills)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_intro(title: str, description: str, pills: list[tuple[str, str]] | None = None) -> None:
    hero(title, description, "Ranking page", pills)


def card(title: str, text: str, pills: list[tuple[str, str]] | None = None) -> None:
    st.markdown(
        f"""
        <div class="radar-card">
            <div class="radar-card-title">{title}</div>
            <div class="radar-card-text">{text}</div>
            {_pill_html(pills)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def soft_note(text: str) -> None:
    st.markdown(f"<div class='radar-footer-note'>{text}</div>", unsafe_allow_html=True)
