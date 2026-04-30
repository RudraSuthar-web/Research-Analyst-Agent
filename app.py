"""
app.py — Research Analyst Agent · Streamlit UI
Run: streamlit run app.py
"""
import os, tempfile, time, threading
import streamlit as st

st.set_page_config(
    page_title="Research Analyst",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --ink:    #0d0d0d;
    --paper:  #f5f2eb;
    --paper2: #ede9e0;
    --green:  #1a3a2a;
    --orange: #c8502a;
    --muted:  #7a7060;
    --border: #d4cfc4;
    --mono:   'DM Mono', monospace;
    --sans:   'DM Sans', sans-serif;
}

html, body, [class*="css"], .stApp {
    font-family: var(--sans) !important;
    background: var(--paper) !important;
    color: var(--ink) !important;
}

/* hide all streamlit chrome + sidebar */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }

/* ═══ NAVBAR ═══════════════════════════════════════════════════════════════ */
/* The nav is built from st.columns + st.button — we style those buttons     */

/* Outer nav wrapper div we inject */
.navbar-wrap {
    background: var(--green);
    display: flex;
    align-items: stretch;
    height: 54px;
    padding: 0 32px;
    gap: 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 1px solid rgba(255,255,255,.08);
}
.navbar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-right: 40px;
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 400;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #e8e0d0;
    white-space: nowrap;
    flex-shrink: 0;
}
.navbar-brand .hex { color: var(--orange); font-size: 16px; }
.navbar-stats {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 28px;
    font-family: var(--mono);
    font-size: 11px;
    color: rgba(255,255,255,.35);
    letter-spacing: .06em;
    flex-shrink: 0;
}
.navbar-stats b { color: rgba(255,255,255,.7); font-weight: 400; }

/* Nav buttons — these are real st.buttons inside the navbar */
div[data-testid="stHorizontalBlock"].navbar-row > div > div > div > div button {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: rgba(255,255,255,.45) !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    padding: 0 20px !important;
    height: 54px !important;
    width: 100% !important;
    transition: all .15s !important;
    box-shadow: none !important;
    cursor: pointer !important;
}
div[data-testid="stHorizontalBlock"].navbar-row > div > div > div > div button:hover {
    color: rgba(255,255,255,.85) !important;
    background: rgba(255,255,255,.05) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Active nav button states — set via class on wrapper */
.nav-active-chat div[data-testid="stHorizontalBlock"].navbar-row > div:nth-child(2) button,
.nav-active-ingest div[data-testid="stHorizontalBlock"].navbar-row > div:nth-child(3) button,
.nav-active-library div[data-testid="stHorizontalBlock"].navbar-row > div:nth-child(4) button {
    color: #e8e0d0 !important;
    border-bottom-color: var(--orange) !important;
}

/* ═══ PAGE BODY ═════════════════════════════════════════════════════════════ */
.page-wrap { padding: 44px 64px; max-width: 940px; margin: 0 auto; }
.pg-eyebrow {
    font-family: var(--mono);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: .18em;
    color: var(--muted);
    margin-bottom: 8px;
}
.pg-title {
    font-family: var(--mono);
    font-size: 22px;
    font-weight: 300;
    letter-spacing: .02em;
    color: var(--ink);
    margin-bottom: 8px;
}
.pg-sub {
    font-size: 13px;
    color: var(--muted);
    font-style: italic;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}

/* ═══ CHAT ══════════════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 3px 0 !important; }
[data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--paper2) !important; border: 1px solid var(--border) !important;
    border-radius: 2px 12px 12px 12px !important; padding: 11px 16px !important;
    font-size: 14px !important; max-width: 76% !important; margin-left: auto !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: white !important; border: 1px solid var(--border) !important;
    border-left: 3px solid var(--orange) !important; border-radius: 12px 2px 12px 12px !important;
    padding: 14px 18px !important; font-size: 14px !important; line-height: 1.75 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.05) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: var(--sans) !important; font-size: 14px !important;
    background: white !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
}

/* suggestion buttons */
.suggestions .stButton button {
    font-family: var(--sans) !important; font-size: 13px !important;
    border: 1px solid var(--border) !important; background: white !important;
    color: var(--ink) !important; border-radius: 8px !important;
    text-align: left !important; padding: 12px 16px !important;
    height: auto !important; line-height: 1.5 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.04) !important;
    transition: all .15s !important;
}
.suggestions .stButton button:hover {
    border-color: var(--green) !important; background: var(--paper2) !important;
    box-shadow: 0 3px 10px rgba(0,0,0,.08) !important; transform: translateY(-1px) !important;
}

.status-anim {
    font-family: var(--mono); font-size: 12px; color: var(--muted);
    letter-spacing: .05em; padding: 10px 0;
    animation: blink 1.6s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:.4} 50%{opacity:1} }

/* ═══ BUTTONS ═══════════════════════════════════════════════════════════════ */
button[kind="primary"] {
    background: var(--green) !important; color: #e8e0d0 !important; border: none !important;
    font-family: var(--mono) !important; font-size: 11px !important;
    letter-spacing: .08em !important; text-transform: uppercase !important;
    border-radius: 6px !important; padding: 10px 22px !important;
}
button[kind="primary"]:hover { background: #0f2218 !important; transform: none !important; box-shadow: none !important; }
button[kind="secondary"] {
    font-family: var(--mono) !important; font-size: 11px !important;
    letter-spacing: .06em !important; text-transform: uppercase !important;
    border: 1px solid var(--border) !important; background: white !important;
    color: var(--muted) !important; border-radius: 6px !important;
}
button[kind="secondary"]:hover { border-color: #c0392b !important; color: #c0392b !important; }

/* ═══ TABS ══════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid var(--border); background: transparent; margin-bottom: 24px; }
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: .1em; padding: 10px 24px;
    color: var(--muted) !important; border-bottom: 2px solid transparent; margin-bottom: -1px; background: transparent !important;
}
.stTabs [aria-selected="true"] { color: var(--green) !important; border-bottom-color: var(--orange) !important; }

/* ═══ INPUTS ════════════════════════════════════════════════════════════════ */
.stTextInput input {
    font-family: var(--sans) !important; font-size: 13px !important;
    border: 1px solid var(--border) !important; border-radius: 6px !important; background: white !important;
}
.stTextInput input:focus { border-color: var(--green) !important; box-shadow: 0 0 0 2px rgba(26,58,42,.08) !important; }
[data-testid="stFileUploader"] { border: 2px dashed var(--border) !important; border-radius: 10px !important; background: white !important; }

/* ═══ METRICS ═══════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px !important; }
[data-testid="stMetricValue"] { font-family: var(--mono) !important; font-size: 30px !important; font-weight: 300 !important; }
[data-testid="stMetricLabel"] { font-family: var(--mono) !important; font-size: 10px !important; text-transform: uppercase !important; letter-spacing: .12em !important; color: var(--muted) !important; }

/* ═══ EXPANDER ══════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 8px !important; background: white !important; margin-bottom: 8px !important; box-shadow: 0 1px 3px rgba(0,0,0,.03) !important; }
[data-testid="stExpander"] summary { font-size: 14px !important; font-weight: 400 !important; padding: 14px 18px !important; }

/* ═══ MISC ══════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] { border-radius: 6px !important; font-size: 13px !important; }
hr { border-color: var(--border) !important; }
.stCaption { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stProgressBar"] > div > div { background: var(--orange) !important; }
.tag {
    display: inline-block; font-family: var(--mono); font-size: 11px;
    background: var(--paper2); border: 1px solid var(--border);
    border-radius: 3px; padding: 2px 8px; margin: 2px 3px 2px 0; color: var(--muted);
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("chat_history", []), ("use_web", False), ("page", "Chat")]:
    if k not in st.session_state:
        st.session_state[k] = v

page = st.session_state.page


# ── DB helper ──────────────────────────────────────────────────────────────────
@st.cache_resource
def _db():
    from storage.database import get_session, Document as D
    return get_session, D

def get_docs():
    try:
        gs, D = _db()
        with gs() as s:
            return s.query(D).order_by(D.created_at.desc()).all()
    except Exception:
        return []

docs        = get_docs()
doc_count   = len(docs)
chunk_count = sum(d.chunk_count or 0 for d in docs)


# ── NAVBAR ─────────────────────────────────────────────────────────────────────
# Inject the brand + stats HTML wrapper
st.markdown(f"""
<div class="navbar-wrap">
    <div class="navbar-brand"><span class="hex">⬡</span> Research Analyst</div>
    <div style="display:flex;align-items:stretch;gap:0;flex:1" id="nav-btns-placeholder"></div>
    <div class="navbar-stats">
        <span><b>{doc_count}</b> docs</span>
        <span><b>{chunk_count}</b> chunks</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Real Streamlit buttons for navigation — overlaid on navbar via CSS
nav_css_class = f"nav-active-{page.lower()}"
st.markdown(f'<div class="{nav_css_class}">', unsafe_allow_html=True)
n1, n2, n3, spacer = st.columns([1, 1, 1, 7])

with n1:
    if st.button("01 · Chat", key="nav1", use_container_width=True):
        st.session_state.page = "Chat"; st.rerun()
with n2:
    if st.button("02 · Ingest", key="nav2", use_container_width=True):
        st.session_state.page = "Ingest"; st.rerun()
with n3:
    if st.button("03 · Library", key="nav3", use_container_width=True):
        st.session_state.page = "Library"; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Pull nav buttons up into the navbar via CSS transform
st.markdown("""
<style>
/* Grab the first columns row (our nav buttons) and slide it up into navbar */
div[data-testid="stHorizontalBlock"]:first-of-type {
    position: relative;
    margin-top: -54px !important;
    margin-left: 260px !important;
    width: auto !important;
    z-index: 1001;
    background: transparent;
    padding: 0 !important;
    gap: 0 !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 130px !important;
    padding: 0 !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:last-child {
    display: none !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: rgba(255,255,255,.45) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    height: 54px !important;
    padding: 0 !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: color .15s !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button:hover {
    color: rgba(255,255,255,.85) !important;
    background: rgba(255,255,255,.06) !important;
    transform: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# Active state highlight — injected per page
active_idx = {"Chat": 1, "Ingest": 2, "Library": 3}[page]
st.markdown(f"""
<style>
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child({active_idx}) button {{
    color: #e8e0d0 !important;
    border-bottom-color: #c8502a !important;
}}
</style>
""", unsafe_allow_html=True)


# ── Page content ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
if page == "Chat":
    st.markdown("""
    <div class="pg-eyebrow">01 · Chat</div>
    <div class="pg-title">Research Chat</div>
    <div class="pg-sub">Ask questions across your ingested papers. Every claim is cited.</div>
    """, unsafe_allow_html=True)

    if doc_count == 0:
        st.info("No documents yet — go to **02 · Ingest** to add papers.", icon="📄")

    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    if not st.session_state.chat_history and doc_count > 0:
        st.markdown('<div class="pg-eyebrow" style="margin:28px 0 14px">Suggested queries</div>', unsafe_allow_html=True)
        suggestions = [
            "What are the key contributions of the ingested papers?",
            "Summarise the methodology used in this research.",
            "What datasets or benchmarks were used for evaluation?",
            "What limitations do the authors identify?",
        ]
        st.markdown('<div class="suggestions">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        for i, s in enumerate(suggestions):
            if (c1 if i % 2 == 0 else c2).button(s, use_container_width=True, key=f"sug{i}"):
                st.session_state.chat_history.append({"role": "user", "content": s})
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    tc1, tc2 = st.columns([8, 2])
    with tc2:
        st.session_state.use_web = st.toggle("Web search", value=st.session_state.use_web)
        if st.session_state.chat_history:
            if st.button("Clear chat", use_container_width=True):
                st.session_state.chat_history = []; st.rerun()

    query = st.chat_input("Ask a research question…")
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            steps = ["Planning retrieval strategy", "Searching knowledge base", "Synthesizing answer"]
            if st.session_state.use_web:
                steps.insert(2, "Searching the web")
            result = {"answer": None, "error": None}
            def _run():
                try:
                    from agent.graph import run_agent
                    result["answer"] = run_agent(query, force_web_search=st.session_state.use_web)
                except Exception as e:
                    result["error"] = str(e)
            t = threading.Thread(target=_run); t.start()
            i = 0
            while t.is_alive():
                placeholder.markdown(f'<div class="status-anim">◌ {steps[i % len(steps)]}…</div>', unsafe_allow_html=True)
                i += 1; time.sleep(1.6)
            t.join(); placeholder.empty()
            answer = f"**Error:** {result['error']}" if result["error"] else result["answer"]
            st.markdown(answer)
            st.session_state.chat_history.append({"role": "ai", "content": answer})


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — INGEST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Ingest":
    st.markdown("""
    <div class="pg-eyebrow">02 · Ingest</div>
    <div class="pg-title">Ingest Documents</div>
    <div class="pg-sub">Add PDFs or web pages — chunked, embedded, and stored locally.</div>
    """, unsafe_allow_html=True)

    tab_pdf, tab_url = st.tabs(["PDF Upload", "Web URL"])

    with tab_pdf:
        uploaded = st.file_uploader("Drop PDFs here", type=["pdf"],
            accept_multiple_files=True, label_visibility="collapsed")
        tags_pdf = st.text_input("Tags", placeholder="transformers, nlp, 2024", key="tpdf")
        cb, cn = st.columns([2, 5])
        go = cb.button("Ingest PDFs", type="primary", disabled=not uploaded, use_container_width=True)
        cn.caption("Embeddings generated locally — no API cost.")
        if go and uploaded:
            from ingestion.pipeline import ingest_pdf
            tags = [t.strip() for t in tags_pdf.split(",") if t.strip()]
            prog = st.progress(0)
            for i, f in enumerate(uploaded):
                prog.progress(i / len(uploaded), text=f"Processing {f.name}…")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(f.read()); tmp_path = tmp.name
                try:
                    r = ingest_pdf(tmp_path, tags=tags)
                    st.success(f"✅ **{r['title']}** — {r['chunks']} chunks") if r["status"] == "ok" else st.warning(f"⚠️ **{r['title']}** already indexed")
                except Exception as e:
                    st.error(f"{f.name}: {e}")
                finally:
                    os.unlink(tmp_path)
            prog.progress(1.0); time.sleep(0.5); prog.empty()
            st.cache_resource.clear(); st.rerun()

    with tab_url:
        url = st.text_input("URL", placeholder="https://arxiv.org/abs/2307.09288", label_visibility="collapsed")
        tags_url = st.text_input("Tags", placeholder="llama, meta, 2023", key="turl")
        if st.button("Ingest URL", type="primary", disabled=not url):
            from ingestion.pipeline import ingest_url
            tags = [t.strip() for t in tags_url.split(",") if t.strip()]
            with st.spinner("Fetching and indexing…"):
                try:
                    r = ingest_url(url, tags=tags)
                    st.success(f"✅ **{r['title']}** — {r['chunks']} chunks") if r["status"] == "ok" else st.warning(f"⚠️ Already indexed")
                except Exception as e:
                    st.error(str(e))
            st.cache_resource.clear(); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Library":
    st.markdown("""
    <div class="pg-eyebrow">03 · Library</div>
    <div class="pg-title">Knowledge Library</div>
    <div class="pg-sub">All documents currently indexed and searchable by the agent.</div>
    """, unsafe_allow_html=True)

    try:
        gs, D = _db()
        from storage.vector_store import get_vector_store
        with gs() as s:
            all_docs = s.query(D).order_by(D.created_at.desc()).all()

        if not all_docs:
            st.info("No documents yet — go to **02 · Ingest** to add papers.", icon="📄")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Documents",  len(all_docs))
            c2.metric("Chunks",     sum(d.chunk_count or 0 for d in all_docs))
            c3.metric("PDFs",       sum(1 for d in all_docs if d.source_type == "pdf"))
            c4.metric("Web pages",  sum(1 for d in all_docs if d.source_type == "url"))

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
            search = st.text_input("", placeholder="🔎  Filter by title, author, or tag…")
            filtered = [d for d in all_docs if not search or
                        search.lower() in f"{d.title} {d.authors or ''} {d.tags or ''}".lower()]
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if not filtered:
                st.warning("No documents match.")
            else:
                for doc in filtered:
                    icon = "PDF" if doc.source_type == "pdf" else "URL"
                    with st.expander(f"[{icon}]  {doc.title}"):
                        left, right = st.columns([5, 1])
                        with left:
                            st.markdown(f"""<div style='font-family:DM Mono,monospace;
                                font-size:12px;color:#7a7060;line-height:2.2;letter-spacing:.02em;'>
                                {doc.source_path}<br>
                                {doc.created_at.strftime('%Y-%m-%d  %H:%M')} &nbsp;·&nbsp; {doc.chunk_count} chunks
                            </div>""", unsafe_allow_html=True)
                            tags_val = doc.tags if isinstance(doc.tags, str) else ", ".join(doc.tags or [])
                            if tags_val:
                                st.markdown("".join(f'<span class="tag">{t.strip()}</span>'
                                    for t in tags_val.split(",") if t.strip()), unsafe_allow_html=True)
                        with right:
                            if st.button("Ask", key=f"ask_{doc.id}", use_container_width=True):
                                st.session_state.chat_history.append({"role": "user",
                                    "content": f"Summarise the key findings of: {doc.title}"})
                                st.session_state.page = "Chat"; st.rerun()
                            if st.button("Delete", key=f"del_{doc.id}", use_container_width=True):
                                try:
                                    with gs() as s:
                                        d = s.get(D, doc.id)
                                        if d: s.delete(d); s.commit()
                                    from qdrant_client.models import Filter, FieldCondition, MatchValue
                                    vs = get_vector_store()
                                    vs.client.delete(collection_name=vs.collection_name,
                                        points_selector=Filter(must=[
                                            FieldCondition(key="metadata.doc_id", match=MatchValue(value=doc.id))
                                        ]))
                                    st.success("Deleted.")
                                    st.cache_resource.clear(); st.rerun()
                                except Exception as e:
                                    st.error(str(e))
    except Exception as e:
        st.error(f"Could not load library: {e}"); st.exception(e)

st.markdown('</div>', unsafe_allow_html=True)