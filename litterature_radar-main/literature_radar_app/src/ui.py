from __future__ import annotations

from html import escape

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
            background: #f6f7fb;
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
            color: #244f8f;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .radar-subtitle {
            color: #687083;
            font-size: 1.02rem;
            max-width: 940px;
            line-height: 1.55;
            margin-top: 0.3rem;
        }

        .radar-card {
            background: #ffffff;
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
            color: #172033;
        }

        .radar-card-text {
            color: #687083;
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
            background: #eaf1fb;
            color: #244f8f;
            border-color: rgba(36,79,143,0.12);
        }

        .pill-green {
            background: #e9f5f1;
            color: #216e5a;
            border-color: rgba(33,110,90,0.12);
        }

        .pill-orange {
            background: #fff1e2;
            color: #a45c1a;
            border-color: rgba(164,92,26,0.12);
        }

        .pill-purple {
            background: #f0ebfa;
            color: #6a4ca3;
            border-color: rgba(106,76,163,0.12);
        }

        .radar-footer-note {
            color: #687083;
            font-size: 0.88rem;
            margin-top: 0.6rem;
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
        safe_label = escape(str(label))
        safe_color = escape(str(color))
        out += f"<span class='radar-pill pill-{safe_color}'>{safe_label}</span>"

    out += "</div>"
    return out


def hero(
    title: str,
    subtitle: str,
    eyebrow: str = "Literature Radar",
    pills: list[tuple[str, str]] | None = None,
) -> None:
    st.markdown(
        f"""
        <div class="radar-hero">
            <div class="radar-eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <div class="radar-subtitle">{escape(subtitle)}</div>
            {_pill_html(pills)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_intro(
    title: str,
    description: str,
    pills: list[tuple[str, str]] | None = None,
) -> None:
    hero(title, description, "Ranking page", pills)


def card(
    title: str,
    text: str,
    pills: list[tuple[str, str]] | None = None,
) -> None:
    st.markdown(
        f"""
        <div class="radar-card">
            <div class="radar-card-title">{escape(title)}</div>
            <div class="radar-card-text">{escape(text)}</div>
            {_pill_html(pills)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def soft_note(text: str) -> None:
    st.markdown(
        f"<div class='radar-footer-note'>{escape(text)}</div>",
        unsafe_allow_html=True,
    )
