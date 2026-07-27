"""Local-only review UI for content proposals submitted on the public site.

Run with: uv run streamlit run app.py
Never deployed — reads/writes Firestore with admin credentials that bypass
firestore.rules, and writes directly into the repo's data/ tree + git.
"""

from __future__ import annotations

from typing import Any

import streamlit as st
from google.cloud.firestore_v1.base_query import FieldFilter

import integrate
from firestore_client import get_db

st.set_page_config(page_title="the-platform · local cms", layout="wide")

STATUSES = ["pending", "accepted", "rejected", "deferred"]


@st.cache_resource
def db():
    return get_db()


def fetch_proposals(status: str) -> list[dict[str, Any]]:
    docs = db().collection("proposals").where(filter=FieldFilter("status", "==", status)).stream()
    proposals = []
    for doc in docs:
        data = doc.to_dict()
        data["_id"] = doc.id
        proposals.append(data)
    proposals.sort(key=lambda p: p.get("createdAt") or 0, reverse=True)
    return proposals


def set_status(proposal_id: str, status: str, **extra) -> None:
    db().collection("proposals").document(proposal_id).update({"status": status, **extra})


def render_object_proposal(p: dict[str, Any]) -> None:
    path = f"{p.get('top')}" + (f"/{p['sub']}" if p.get("sub") else "") + f"/{p.get('slug')}"
    st.markdown(f"**new object** · `{path}`")
    st.write(f"**name:** {p.get('name')}")
    if p.get("description"):
        st.write(f"**description:** {p.get('description')}")
    if p.get("topics"):
        st.write(f"**topics:** {', '.join(p.get('topics') or [])}")
    if p.get("url"):
        st.write(f"**url:** [{p.get('urlLabel') or p.get('url')}]({p.get('url')})")


def render_relationship_proposal(p: dict[str, Any]) -> None:
    st.markdown(
        f"**new relationship** · `{p.get('sourceId')}` → `{p.get('targetId')}` "
        f"(context: `{p.get('context')}`)"
    )
    st.write(f"**{p.get('sourceName')}** → **{p.get('targetName')}**")
    st.write(f"**description:** {p.get('label')}")


def render_proposal(p: dict[str, Any], *, actionable: bool) -> None:
    with st.container(border=True):
        cols = st.columns([3, 1])
        with cols[0]:
            if p.get("type") == "object":
                render_object_proposal(p)
            elif p.get("type") == "relationship":
                render_relationship_proposal(p)
            else:
                st.write(p)
            submitted = p.get("submittedByEmail") or p.get("submittedByUid") or "unknown"
            created = p.get("createdAt")
            st.caption(f"submitted by {submitted}" + (f" · {created}" if created else ""))

        if actionable:
            with cols[1]:
                if st.button("Accept", key=f"accept-{p['_id']}", type="primary"):
                    try:
                        if p.get("type") == "object":
                            result_path = integrate.accept_object_proposal(
                                {
                                    "top": p.get("top"),
                                    "sub": p.get("sub"),
                                    "slug": p.get("slug"),
                                    "name": p.get("name"),
                                    "description": p.get("description"),
                                    "topics": p.get("topics"),
                                    "url": p.get("url"),
                                    "url_label": p.get("urlLabel"),
                                    "submitted_by_email": p.get("submittedByEmail"),
                                }
                            )
                        else:
                            result_path = integrate.accept_relationship_proposal(
                                {
                                    "source_id": p.get("sourceId"),
                                    "target_id": p.get("targetId"),
                                    "context": p.get("context"),
                                    "label": p.get("label"),
                                    "submitted_by_email": p.get("submittedByEmail"),
                                }
                            )
                        set_status(p["_id"], "accepted", resultPath=result_path)
                        st.success(f"committed {result_path}")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                if st.button("Defer", key=f"defer-{p['_id']}"):
                    set_status(p["_id"], "deferred")
                    st.rerun()
                if st.button("Reject", key=f"reject-{p['_id']}"):
                    set_status(p["_id"], "rejected")
                    st.rerun()
        elif p.get("status") != "pending":
            with cols[1]:
                st.caption(f"status: {p.get('status')}")
                if p.get("resultPath"):
                    st.caption(f"→ {p['resultPath']}")
                if st.button("Reopen", key=f"reopen-{p['_id']}"):
                    set_status(p["_id"], "pending")
                    st.rerun()


st.title("the-platform · local cms")
st.caption("Review content proposals submitted on the public site. Accepted proposals are written into data/ and committed to git — nothing is pushed.")

tab_labels = [f"pending", "accepted", "rejected", "deferred"]
tabs = st.tabs(tab_labels)

for status, tab in zip(STATUSES, tabs):
    with tab:
        proposals = fetch_proposals(status)
        if not proposals:
            st.write("nothing here")
        for p in proposals:
            render_proposal(p, actionable=(status == "pending"))
