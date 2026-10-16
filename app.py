import re
import html
import time
import traceback
import streamlit as st
from pipeline import research_pipeline

st.set_page_config(page_title="Research Agent", page_icon="🔍", layout="wide",
                   initial_sidebar_state="collapsed")

st.session_state.setdefault("result", None)
st.session_state.setdefault("error", None)
st.session_state.setdefault("topic", "")

# ---- copy -------------------------------------------------------------------
PILL = "Multi-agent research"
TITLE_A, TITLE_EM, TITLE_B = "What should we ", "research", " today?"
SUBTITLE = "Agents search the web, read the sources, write the report and score it."
PLACEHOLDER = "Ask a question or paste a topic, e.g. How do solid-state batteries work?"
PIPELINE_CHIP = "Search · Read · Write · Critic"

# ---- CSS --------------------------------------------------------------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html {color-scheme:dark;}
html, body, .stApp, textarea, button {font-family:'Inter',system-ui,-apple-system,sans-serif !important;}
html, body, .stApp {background:#121212 !important; color:#e4e4e7;}
/* force every Streamlit wrapper transparent so no white boxes show through (no config.toml needed) */
[data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"],
section.main, .main, [data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"], [data-testid="stElementContainer"], [data-testid="stMarkdownContainer"] {background:transparent !important;}
body, html {background:#121212 !important; min-height:100vh !important;}
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stDecoration"] {visibility:hidden; height:0;}
.block-container {max-width:100% !important; padding:0 1rem 8rem 1rem !important;}

@keyframes fadeUp {from {opacity:0; transform:translateY(12px);} to {opacity:1; transform:none;}}
@keyframes dropDown {from {opacity:0; transform:translateY(-38vh);} to {opacity:1; transform:none;}}

/* hero */
.hero {display:flex; flex-direction:column; align-items:center; text-align:center; padding-top:18vh;
  animation:fadeUp .9s cubic-bezier(.22,1,.36,1) both;}
.pill {display:inline-flex; align-items:center; gap:9px; padding:9px 20px; border-radius:999px;
  background:#121a27; border:1px solid #243049; color:#e8eefc; font-size:14px; font-weight:600;}
.h-title {margin-top:28px; font-size:clamp(36px,3.1vw,60px); font-weight:800; letter-spacing:-.03em; line-height:1.1; color:#fff;}
.h-title em {font-style:italic; padding-right:.06em; background:linear-gradient(90deg,#7ab8ff,#3b82f6);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;}
.h-sub {margin-top:10px; font-size:clamp(14px,1.05vw,19px); font-weight:500; color:#8b8d97;}

/* prompt input (Enter = send, Shift+Enter = new line) */
.st-key-hero_input {width:clamp(560px,40vw,800px) !important; max-width:94vw; margin:30px auto 0;
  animation:fadeUp 1s .12s cubic-bezier(.22,1,.36,1) both;}
[data-testid="stBottom"], [data-testid="stBottom"] > div {background:#121212 !important;}
[data-testid="stBottomBlockContainer"] {background:#121212 !important; max-width:min(780px,92vw) !important;
  padding:12px 0 22px !important; animation:dropDown .7s cubic-bezier(.22,1,.36,1) both;}
[data-testid="stChatInput"] {background:#18181d !important; border:1px solid #2b2d36 !important; border-radius:16px !important;
  box-shadow:0 20px 50px rgba(0,0,0,.5) !important; transition:border-color .2s, box-shadow .2s;}
[data-testid="stChatInput"]:focus-within {border-color:#3b82f6 !important; box-shadow:0 0 0 3px rgba(59,130,246,.18) !important;}
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] div[data-baseweb] {background:transparent !important; border:none !important;}
[data-testid="stChatInput"] textarea {color:#e4e4e7 !important; -webkit-text-fill-color:#e4e4e7 !important; font-size:15px !important;
  background:transparent !important; caret-color:#3b82f6;}
[data-testid="stChatInput"] textarea::placeholder {color:#6b6e78 !important; -webkit-text-fill-color:#6b6e78 !important; opacity:1;}
[data-testid="stChatInputSubmitButton"] {background:#3b82f6 !important; color:#fff !important; border-radius:10px !important;
  cursor:pointer; transition:background .2s;}
[data-testid="stChatInputSubmitButton"]:hover {background:#2563eb !important;}
[data-testid="stChatInputSubmitButton"]:disabled {background:#1d4a80 !important; color:#a9c7f0 !important; cursor:default;}
[data-testid="stChatInputSubmitButton"] svg {color:inherit !important; fill:currentColor !important;}
.chip-row {display:flex; justify-content:center; margin-top:12px;}
.chip {display:inline-flex; align-items:center; gap:8px; padding:6px 12px; border-radius:999px; background:#212127;
  border:1px solid #2b2d36; color:#a1a1aa; font-size:12.5px; font-weight:500; white-space:nowrap;}

/* ---------- chat-style output ---------- */
.u-row {display:flex; justify-content:flex-end; width:min(780px,92vw); margin:42px auto 18px; animation:fadeUp .5s both;}
.u-bubble {max-width:80%; padding:11px 18px; border-radius:18px 18px 4px 18px; background:#1d4a80; color:#eaf2ff;
  font-size:15px; line-height:1.55;}
[data-testid="stChatMessage"] {width:min(780px,92vw); margin:0 auto; padding:0 !important; background:transparent !important; gap:14px;}
[data-testid="stChatMessageAvatarAssistant"] {background:#18181d !important; border:1px solid #2b2d36; color:#7ab8ff !important;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {color:#d4d4d8;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] :is(p,li) {font-size:15.5px; line-height:1.75; color:#d4d4d8;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] :is(h1,h2,h3,h4) {color:#fff; font-weight:650; letter-spacing:-.01em;
  margin:1.5em 0 .5em; padding:0;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1 {font-size:24px;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2 {font-size:19px;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {font-size:16.5px;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] :is(strong,b) {color:#fff;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] a {color:#7ab8ff; text-decoration:none; border-bottom:1px solid rgba(122,184,255,.35); word-break:break-all;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] code {background:#212127; color:#e4e4e7; border-radius:6px; padding:2px 6px;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {margin-bottom:.35em;}
[data-testid="stHeaderActionElements"] {display:none;}

.score-card {display:flex; align-items:center; gap:18px; padding:14px 20px; margin:2px 0 14px;
  background:#18181d; border:1px solid #2b2d36; border-radius:14px; animation:fadeUp .6s both;}
.score-card .trk {fill:none; stroke:#2b2d36; stroke-width:7;}
.score-card .bar {fill:none; stroke:#3b82f6; stroke-width:7; stroke-linecap:round; stroke-dasharray:213.63;
  stroke-dashoffset:var(--off); transform:rotate(-90deg); transform-box:fill-box; transform-origin:center;
  animation:ring 1.3s cubic-bezier(.22,1,.36,1) both;}
@keyframes ring {from {stroke-dashoffset:213.63;}}
.score-card .lbl {font-size:11px; letter-spacing:.09em; text-transform:uppercase; color:#71717a;}
.score-card .num {font-size:26px; font-weight:700; color:#fff; line-height:1.15;}
.score-card .vrd {font-size:13.5px; color:#a1a1aa; margin-top:3px; line-height:1.45;}

[data-testid="stExpander"], [data-testid="stAlert"], [data-testid="stStatusWidget"] {width:min(780px,92vw); margin-left:auto; margin-right:auto;}
[data-testid="stExpander"] details {background:#18181d !important; border:1px solid #2b2d36 !important; border-radius:14px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {color:#d4d4d8 !important;}
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] :is(p,li,h1,h2,h3,strong) {color:#d4d4d8;}
[data-testid="stText"], [data-testid="stText"] * {color:#a1a1aa !important; font-size:13px;}
[data-testid="stDownloadButton"] button {background:#18181d; color:#e4e4e7; border:1px solid #2b2d36; border-radius:10px;}
[data-testid="stDownloadButton"] button:hover {border-color:#3b82f6; color:#fff;}

/* Claude-style "generating" loader */
.thinking {display:flex; align-items:center; gap:12px; width:min(780px,92vw); margin:4px auto 0; animation:fadeUp .4s both;}
.thinking .spark {flex:none; animation:spark 1.6s cubic-bezier(.45,0,.55,1) infinite;}
@keyframes spark {0% {transform:rotate(0) scale(.85);} 50% {transform:rotate(90deg) scale(1.1);} 100% {transform:rotate(180deg) scale(.85);}}
.thinking span {font-size:15px; font-weight:500;
  background:linear-gradient(90deg,#71717a 40%,#e4e4e7 50%,#71717a 60%); background-size:250% 100%;
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; animation:shimmer 2s linear infinite;}
@keyframes shimmer {from {background-position:100% 0;} to {background-position:0 0;}}
@media (prefers-reduced-motion:reduce) {.thinking .spark, .thinking span {animation:none;}}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ---- hero (single-line HTML on purpose; indented/blank lines become a code block) ----
ICON = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>')
BOLT = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>')
STEPS = {1: "Searching the web", 2: "Reading the sources", 3: "Writing the report", 4: "Reviewing the report"}
SPARK = ('<svg class="spark" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" '
         'stroke-width="2.4" stroke-linecap="round" aria-hidden="true">'
         '<path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4"/></svg>')

# ---- prompt: centered on the landing screen, docked at the bottom once a chat exists ----
if not st.session_state.topic:
    st.markdown(
        f'<div class="hero"><div class="pill">{ICON}{PILL}</div>'
        f'<div class="h-title">{TITLE_A}<em>{TITLE_EM}</em>{TITLE_B}</div>'
        f'<div class="h-sub">{SUBTITLE}</div></div>',
        unsafe_allow_html=True,
    )
    with st.container(key="hero_input"):
        prompt = st.chat_input(PLACEHOLDER, key="prompt")
    st.markdown(f'<div class="chip-row"><div class="chip">{BOLT}{PIPELINE_CHIP}</div></div>',
                unsafe_allow_html=True)
else:
    prompt = st.chat_input(PLACEHOLDER, key="prompt")

if prompt and prompt.strip():
    st.session_state.topic = prompt.strip()
    st.session_state.result = None
    st.session_state.error = None
    st.session_state.pending = True
    st.rerun()  # re-render immediately in chat layout (hero gone, input docked at bottom)


def stream_words(text):
    for chunk in re.split(r"(\s+)", text):
        yield chunk
        time.sleep(0.006)


def user_bubble(t):
    st.markdown(f'<div class="u-row"><div class="u-bubble">{html.escape(t)}</div></div>', unsafe_allow_html=True)


# ---- conversation -------------------------------------------------------------
fresh = False
if st.session_state.get("pending"):
    st.session_state.pending = False
    user_bubble(st.session_state.topic)
    loader = st.empty()

    def show_loader(label):
        loader.markdown(f'<div class="thinking" role="status">{SPARK}<span>{label}…</span></div>',
                        unsafe_allow_html=True)

    show_loader(STEPS[1])

    def on_step(i, _state):
        if i + 1 in STEPS:
            show_loader(STEPS[i + 1])

    try:
        st.session_state.result = research_pipeline(st.session_state.topic, on_step=on_step)
        fresh = True
    except Exception:
        st.session_state.error = traceback.format_exc()
    finally:
        loader.empty()
elif st.session_state.topic:
    user_bubble(st.session_state.topic)

if st.session_state.error:
    st.error(st.session_state.error)

res = st.session_state.result
if res:
    m = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", res["feedback"])
    v = re.search(r"verdict:?\s*(.+)", res["feedback"], re.I | re.S)
    verdict = html.escape(v.group(1).strip().split("\n")[0]) if v else ""

    with st.chat_message("assistant"):
        if m:
            off = 213.63 * (1 - min(float(m.group(1)), 10) / 10)
            st.markdown(
                f'<div class="score-card"><svg width="64" height="64" viewBox="0 0 80 80">'
                f'<circle class="trk" cx="40" cy="40" r="34"/>'
                f'<circle class="bar" cx="40" cy="40" r="34" style="--off:{off:.2f}"/></svg>'
                f'<div><div class="lbl">Critic score</div><div class="num">{m.group(1)}/10</div>'
                f'<div class="vrd">{verdict}</div></div></div>',
                unsafe_allow_html=True,
            )
        if fresh:
            st.write_stream(stream_words(res["report"]))
        else:
            st.markdown(res["report"])
        st.download_button("Download report (.md)", res["report"], file_name="report.md")

    with st.expander("Critic feedback"):
        st.markdown(res["feedback"])
    with st.expander("Search results"):
        st.text(res["search_results"])
    with st.expander("Scraped content"):
        st.text(res["scrape_results"])