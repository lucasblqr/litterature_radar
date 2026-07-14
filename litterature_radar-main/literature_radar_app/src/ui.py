from __future__ import annotations

import streamlit as st


def apply_global_style() -> None:
    return


def hero(
    title: str,
    subtitle: str,
    eyebrow: str = "Literature Radar",
    pills: list[tuple[str, str]] | None = None,
) -> None:
    st.caption(eyebrow)
    st.title(title)
    st.write(subtitle)

    if pills:
        pill_text = " · ".join([str(label) for label, _ in pills])
        st.caption(pill_text)


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
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(text)

        if pills:
            pill_text = " · ".join([str(label) for label, _ in pills])
            st.caption(pill_text)


def soft_note(text: str) -> None:
    st.caption(text)
