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
            --radar-blue-hover: #1f447b;
            --radar-blue-soft: #eaf1fb;
            --radar-green: #216e5a;
            --radar-green-soft: #e9f5f1;
            --radar-orange: #a45c1a;
            --radar-orange-soft: #fff1e2;
            --radar-purple: #6a4ca3;
            --radar-purple-soft: #f0ebfa;
        }

        html, body, .stApp {
            background: #f6f7fb !important;
            color: #172033 !important;
        }

        .stApp {
            background: linear-gradient(180deg, #f8f9fc 0%, #f3f5fa 100%) !important;
            color: #172033 !important;
        }

        .stApp,
        .stApp p,
        .stApp span,
        .stApp div,
        .stApp label,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6,
        .stApp li {
            color: #172033 !important;
        }

        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] *,
        [data-testid="stText"],
        [data-testid="stText"] * {
            color: #172033 !important;
        }

        section[data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid var(--radar-border);
        }

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] * {
            color: #172033 !important;
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
            color: #172033 !important;
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
                linear-gradient(135deg, #ffffff 0%, #f4f7fc 100%) !important;
            border: 1px solid var(--radar-border);
            box-shadow: 0 16px 40px rgba(30, 42, 70, 0.07);
            margin-bottom: 1.2rem;
        }

        .radar-hero,
        .radar-hero * {
            color: #172033 !important;
        }

        .radar-eyebrow {
            color: #244f8f !important;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .radar-subtitle {
            color: #687083 !important;
            font-size: 1.02rem;
            max-width: 940px;
            line-height: 1.55;
            margin-top: 0.3rem;
        }

        .radar-card {
            background: #ffffff !important;
            border: 1px solid var(--radar-border);
            border-radius: 18px;
            padding: 1.08rem 1.18rem;
            box-shadow: 0 12px 28px rgba(30, 42, 70, 0.055);
            height: 100%;
            margin-bottom: 0.75rem;
        }

        .radar-card,
        .radar-card * {
            color: #172033 !important;
        }

        .radar-card-title {
            font-weight: 800;
            font-size: 1.03rem;
            margin-bottom: 0.25rem;
            color: #172033 !important;
        }

        .radar-card-text {
            color: #687083 !important;
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
            background: #eaf1fb !important;
            color: #244f8f !important;
            border-color: rgba(36,79,143,0.12);
        }

        .pill-green {
            background: #e9f5f1 !important;
            color: #216e5a !important;
            border-color: rgba(33,110,90,0.12);
        }

        .pill-orange {
            background: #fff1e2 !important;
            color: #a45c1a !important;
            border-color: rgba(164,92,26,0.12);
        }

        .pill-purple {
            background: #f0ebfa !important;
            color: #6a4ca3 !important;
            border-color: rgba(106,76,163,0.12);
        }

        div[data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid var(--radar-border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 28px rgba(30, 42, 70, 0.05);
        }

        div[data-testid="stMetric"],
        div[data-testid="stMetric"] * {
            color: #172033 !important;
        }

        div[data-testid="stMetric"] label {
            color: #687083 !important;
            font-weight: 700;
        }

        div[data-testid="stMetricValue"] {
            color: #172033 !important;
            font-weight: 850;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stDataEditor"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--radar-border);
            box-shadow: 0 12px 28px rgba(30, 42, 70, 0.05);
            background: #ffffff !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 16px;
        }

        div[data-testid="stAlert"],
        div[data-testid="stAlert"] * {
            color: #172033 !important;
        }

        .radar-footer-note {
            color: #687083 !important;
            font-size: 0.88rem;
            margin-top: 0.6rem;
        }

        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] *,
        small {
            color: #687083 !important;
        }

        a {
            color: #244f8f !important;
            text-decoration: none !important;
        }

        hr {
            border-color: #e7e9f0 !important;
        }

        /* Expander / Filters fix */
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid #d8dee9 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }

        div[data-testid="stExpander"] details {
            background-color: #ffffff !important;
            border-radius: 12px !important;
        }

        div[data-testid="stExpander"] summary {
            background-color: #ffffff !important;
            color: #172033 !important;
            border-radius: 12px !important;
            min-height: 2.6rem !important;
        }

        div[data-testid="stExpander"] summary:hover {
            background-color: #f3f5fa !important;
            color: #172033 !important;
        }

        div[data-testid="stExpander"] summary * {
            color: #172033 !important;
            background-color: transparent !important;
        }

        div[data-testid="stExpander"] svg {
            fill: #172033 !important;
            color: #172033 !important;
        }

        div[data-testid="stExpander"] div {
            color: #172033 !important;
        }

        /* Forms */
        div[data-testid="stForm"] {
            background-color: #ffffff !important;
            border: 1px solid #e7e9f0 !important;
            border-radius: 14px !important;
            padding: 0.75rem !important;
        }

        div[data-testid="stForm"],
        div[data-testid="stForm"] * {
            color: #172033 !important;
        }

        /* Input boxes */
        input,
        textarea,
        div[data-baseweb="input"],
        div[data-baseweb="textarea"],
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: #ffffff !important;
            color: #172033 !important;
            border-color: #d8dee9 !important;
        }

        input::placeholder,
        textarea::placeholder {
            color: #687083 !important;
            opacity: 1 !important;
        }

        /* Select boxes and dropdowns */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #172033 !important;
            border-color: #d8dee9 !important;
        }

        div[data-baseweb="select"] *,
        div[data-baseweb="popover"] *,
        div[data-baseweb="menu"] * {
            color: #172033 !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"],
        div[role="listbox"] {
            background-color: #ffffff !important;
            color: #172033 !important;
        }

        li[role="option"],
        div[role="option"] {
            background-color: #ffffff !important;
            color: #172033 !important;
        }

        li[role="option"]:hover,
        div[role="option"]:hover {
            background-color: #eaf1fb !important;
            color: #172033 !important;
        }

        /* Checkbox fix */
        div[data-testid="stCheckbox"] {
            color: #172033 !important;
        }

        div[data-testid="stCheckbox"] *,
        div[data-testid="stCheckbox"] label,
        div[data-testid="stCheckbox"] label * {
            color: #172033 !important;
        }

        div[data-testid="stCheckbox"] div[role="checkbox"],
        div[data-testid="stCheckbox"] [role="checkbox"] {
            background-color: #ffffff !important;
            border: 2px solid #244f8f !important;
            border-radius: 5px !important;
            box-shadow: none !important;
        }

        div[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"],
        div[data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] {
            background-color: #244f8f !important;
            border-color: #244f8f !important;
        }

        div[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] *,
        div[data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] * {
            color: #ffffff !important;
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        div[data-testid="stCheckbox"] svg {
            color: #ffffff !important;
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        label[data-baseweb="checkbox"] > div:first-child {
            background-color: #ffffff !important;
            border: 2px solid #244f8f !important;
            border-radius: 5px !important;
        }

        label[data-baseweb="checkbox"] > div:first-child[aria-checked="true"] {
            background-color: #244f8f !important;
            border-color: #244f8f !important;
        }

        /* Radio buttons */
        div[data-testid="stRadio"],
        div[data-testid="stRadio"] *,
        div[data-testid="stRadio"] label {
            color: #172033 !important;
        }

        /* Sliders */
        div[data-testid="stSlider"],
        div[data-testid="stSlider"] * {
            color: #172033 !important;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            color: #172033 !important;
            border: none !important;
            box-shadow: none !important;
        }

        button[data-baseweb="tab"] * {
            color: #172033 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #244f8f !important;
            border-bottom: 2px solid #244f8f !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] * {
            color: #244f8f !important;
        }

        /* Normal Streamlit buttons */
        .stButton > button,
        div[data-testid="stButton"] button,
        button[kind="primary"],
        button[kind="secondary"],
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"] {
            border-radius: 999px !important;
            border: 1px solid rgba(36,79,143,0.24) !important;
            background-color: #244f8f !important;
            color: #ffffff !important;
            font-weight: 750 !important;
            padding: 0.56rem 1.08rem !important;
            box-shadow: 0 10px 24px rgba(36,79,143,0.20) !important;
        }

        .stButton > button *,
        div[data-testid="stButton"] button *,
        button[kind="primary"] *,
        button[kind="secondary"] *,
        button[data-testid="baseButton-primary"] *,
        button[data-testid="baseButton-secondary"] * {
            color: #ffffff !important;
        }

        .stButton > button:hover,
        div[data-testid="stButton"] button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover {
            background-color: #1f447b !important;
            color: #ffffff !important;
            border-color: rgba(36,79,143,0.4) !important;
        }

        /* Open paper link button fix */
        div[data-testid="stLinkButton"] a,
        div[data-testid="stLinkButton"] a:visited,
        div[data-testid="stLinkButton"] a:hover,
        div[data-testid="stLinkButton"] a:active,
        a[data-testid="stLinkButton"],
        a[data-testid="stLinkButton"]:visited,
        a[data-testid="stLinkButton"]:hover,
        a[data-testid="stLinkButton"]:active {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 999px !important;
            border: 1px solid rgba(36,79,143,0.24) !important;
            background-color: #244f8f !important;
            color: #ffffff !important;
            font-weight: 750 !important;
            padding: 0.56rem 1.08rem !important;
            box-shadow: 0 10px 24px rgba(36,79,143,0.20) !important;
            text-decoration: none !important;
        }

        div[data-testid="stLinkButton"] a *,
        a[data-testid="stLinkButton"] *,
        div[data-testid="stLinkButton"] p,
        div[data-testid="stLinkButton"] span {
            color: #ffffff !important;
        }

        div[data-testid="stLinkButton"] a:hover,
        a[data-testid="stLinkButton"]:hover {
            background-color: #1f447b !important;
            color: #ffffff !important;
            border-color: rgba(36,79,143,0.4) !important;
            text-decoration: none !important;
        }

        /* Sidebar navigation */
        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNav"] a * {
            color: #172033 !important;
        }

        [data-testid="stSidebarNav"] a:hover {
            background-color: #f3f5fa !important;
            color: #172033 !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #eaf1fb !important;
            color: #244f8f !important;
            border-radius: 10px !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] * {
            color: #244f8f !important;
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
