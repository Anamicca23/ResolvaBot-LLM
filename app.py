"""
app.py — ResolvaBot LLM  (All 7 UI fixes applied)
"""
import os, sys, re, html, base64
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

SRC = os.path.join(os.path.dirname(__file__), "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
load_dotenv()

st.set_page_config(
    page_title="ResolvaBot LLM", page_icon="📚",
    layout="wide", initial_sidebar_state="collapsed",
)

# ── Themes ────────────────────────────────────────────────────────────────────
THEMES = {
    "dark":   {"name":"Dark",   "ac":"#58a6ff","ac2":"#8b5cf6","rgb":"88,166,255",
               "page":"#0d1117","card":"#161b22","panel":"#1c2333","inp":"#1f2937",
               "b1":"#30363d","b2":"#21262d","t1":"#e6edf3","t2":"#8b949e","t3":"#484f58",
               "green":"#3fb950","gbg":"rgba(63,185,80,.12)","shd":"0 8px 32px rgba(0,0,0,.5)"},
    "light":  {"name":"Light",  "ac":"#0969da","ac2":"#7c3aed","rgb":"9,105,218",
               "page":"#f6f8fa","card":"#ffffff","panel":"#f0f4f8","inp":"#f8fafc",
               "b1":"#d0d7de","b2":"#e2e8f0","t1":"#0d1117","t2":"#57606a","t3":"#9ca3af",
               "green":"#1a7f37","gbg":"rgba(26,127,55,.08)","shd":"0 4px 16px rgba(0,0,0,.1)"},
    "indigo": {"name":"Indigo", "ac":"#7c6af7","ac2":"#e86af7","rgb":"124,106,247",
               "page":"#0f0e17","card":"#16152a","panel":"#1c1b33","inp":"#211f3c",
               "b1":"#2e2b52","b2":"#3a3760","t1":"#fffffe","t2":"#a7a9be","t3":"#5c5a7e",
               "green":"#3ecf8e","gbg":"rgba(62,207,142,.1)","shd":"0 8px 32px rgba(0,0,0,.6)"},
    "teal":   {"name":"Teal",   "ac":"#2dd4bf","ac2":"#22d3ee","rgb":"45,212,191",
               "page":"#0a1628","card":"#0f2237","panel":"#122840","inp":"#163048",
               "b1":"#1e3d55","b2":"#254d6b","t1":"#e2f4ff","t2":"#7db3cc","t3":"#3d7090",
               "green":"#34d399","gbg":"rgba(52,211,153,.1)","shd":"0 8px 32px rgba(0,0,0,.5)"},
    "rose":   {"name":"Rose",   "ac":"#f43f5e","ac2":"#ec4899","rgb":"244,63,94",
               "page":"#0f0a0c","card":"#1a0f13","panel":"#22141a","inp":"#2a1820",
               "b1":"#3d1f28","b2":"#4d2535","t1":"#fff1f3","t2":"#fca5a5","t3":"#6b2737",
               "green":"#34d399","gbg":"rgba(52,211,153,.1)","shd":"0 8px 32px rgba(0,0,0,.6)"},
    "amber":  {"name":"Amber",  "ac":"#f59e0b","ac2":"#ef4444","rgb":"245,158,11",
               "page":"#0c0a04","card":"#1a1504","panel":"#221d06","inp":"#2a2408",
               "b1":"#3d3410","b2":"#4d4218","t1":"#fefce8","t2":"#fde68a","t3":"#713f12",
               "green":"#34d399","gbg":"rgba(52,211,153,.1)","shd":"0 8px 32px rgba(0,0,0,.6)"},
    "mono":   {"name":"Mono",   "ac":"#94a3b8","ac2":"#64748b","rgb":"148,163,184",
               "page":"#0a0a0a","card":"#111111","panel":"#1a1a1a","inp":"#222222",
               "b1":"#2d2d2d","b2":"#3d3d3d","t1":"#f8f8f8","t2":"#a0a0a0","t3":"#555555",
               "green":"#34d399","gbg":"rgba(52,211,153,.1)","shd":"0 8px 32px rgba(0,0,0,.7)"},
}

# ── Session state defaults ─────────────────────────────────────────────────────
for k, v in dict(
    view="upload", theme="dark", sidebar_open=False,
    indexed=False, retriever=None, history=[],
    last_file="", last_file_bytes=None,
    pages=0, chunks=0, nodes=0, file_size="", step=0,
    cur_passages=[],
    groq_key=os.getenv("GROQ_API_KEY",""),
    openai_key=os.getenv("OPENAI_API_KEY",""),
).items():
    if k not in st.session_state: st.session_state[k] = v

if st.session_state.groq_key:  os.environ["GROQ_API_KEY"]  = st.session_state.groq_key
if st.session_state.openai_key:os.environ["OPENAI_API_KEY"] = st.session_state.openai_key
has_groq   = bool(os.getenv("GROQ_API_KEY","").strip())
has_openai = bool(os.getenv("OPENAI_API_KEY","").strip())

T   = THEMES[st.session_state.theme]
ac  = T["ac"]; ac2 = T["ac2"]; rgb = T["rgb"]

def go(v): st.session_state.view = v; st.rerun()
def detect_lang(t):
    if re.search(r'#include|cout|cin|vector<|int main', t): return "cpp"
    if re.search(r'\bdef \b|\bimport \b|print\(', t):      return "python"
    if re.search(r'public class|System\.out', t):           return "java"
    return "text"
def pill(text, cls="ps"):
    return f'<span class="pill {cls}">{text}</span>'

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
 
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
 
html, body {{
    background: {T['page']} !important;
    height: 100vh !important;
    overflow: hidden !important;
}}
.stApp {{
    background: {T['page']} !important;
    font-family: 'Inter', -apple-system, sans-serif;
    color: {T['t1']};
}}
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="collapsedControl"],
.stDeployButton {{ display: none !important; }}
 
/* Zero all Streamlit default padding */
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
 
[data-testid="stAppViewContainer"] {{
    padding: 0 !important;
    padding-top: 56px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100vh !important;
    background: {T['page']} !important;
    scrollbar-width: thin;
    scrollbar-color: {T['b2']} transparent;
}}
[data-testid="stAppViewContainer"]::-webkit-scrollbar {{ width: 4px; }}
[data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb {{
    background: {T['b2']}; border-radius: 4px;
}}
 
[data-testid="stMain"] {{
    padding: 0 !important;
    overflow: visible !important;
    background: {T['page']} !important;
}}
 
[data-testid="stMainBlockContainer"] {{
    max-width: 860px !important;
    margin: 0 auto !important;
    padding: 1.5rem 1.5rem 4rem !important;
    min-width: 0 !important;
    background: {T['page']} !important;
}}
 
/* ── Fixed topbar ── */
.rb-topbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
    height: 56px; background: {T['card']}; border-bottom: 1px solid {T['b1']};
    display: flex; align-items: center; padding: 0 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.15);
}}
.rb-topbar-inner {{
    display: flex; align-items: center;
    width: 100%; max-width: 900px; margin: 0 auto;
}}
.rb-brand {{ display: flex; align-items: center; gap: 9px; flex-shrink: 0; }}
.rb-logo {{
    width: 30px; height: 30px; border-radius: 8px;
    background: linear-gradient(135deg, {ac}, {ac2});
    display: flex; align-items: center; justify-content: center;
    font-size: .9rem; box-shadow: 0 2px 8px rgba({rgb},.3);
}}
.rb-brand-name {{ font-size: .9rem; font-weight: 700; letter-spacing: -.02em; color: {T['t1']}; }}
.rb-brand-name span {{ font-weight: 300; color: {T['t3']}; font-size: .8rem; }}
.rb-breadcrumb {{ display: flex; align-items: center; gap: 6px; margin-left: 12px; }}
.rb-sep {{ color: {T['t3']}; font-size: .8rem; }}
.rb-page-name {{ font-size: .8rem; font-weight: 500; color: {T['t2']}; }}
.rb-topbar-right {{ display: flex; align-items: center; gap: 8px; margin-left: auto; }}
 
/* Pills */
.pill {{ display: inline-flex; align-items: center; gap: 3px; padding: 2px 8px; border-radius: 20px; font-size: .63rem; font-weight: 600; }}
.pg {{ background: {T['gbg']}; color: {T['green']}; border: 1px solid rgba(63,185,80,.25); }}
.pb {{ background: rgba({rgb},.1); color: {ac}; border: 1px solid rgba({rgb},.25); }}
.pp {{ background: rgba(139,92,246,.1); color: #8b5cf6; border: 1px solid rgba(139,92,246,.2); }}
.py {{ background: rgba(245,158,11,.1); color: #d97706; border: 1px solid rgba(245,158,11,.2); }}
.ps {{ background: {T['panel']}; color: {T['t2']}; border: 1px solid {T['b1']}; }}
 
/* ── Sidebar overlay ── */
.rb-sidebar-overlay {{
    position: fixed; inset: 0; top: 56px;
    background: rgba(0,0,0,.45); z-index: 900; backdrop-filter: blur(2px);
}}
.rb-sidebar {{
    position: fixed; top: 56px; left: 0; bottom: 0; width: 240px; z-index: 950;
    background: {T['card']}; border-right: 1px solid {T['b1']};
    display: flex; flex-direction: column; padding: 1rem .75rem; gap: 2px;
    overflow-y: auto; box-shadow: 4px 0 24px rgba(0,0,0,.3);
    animation: slideIn .2s ease;
}}
@keyframes slideIn {{ from{{transform:translateX(-20px);opacity:0}} to{{transform:translateX(0);opacity:1}} }}
.sb-hdr {{ font-size:.62rem; font-weight:700; letter-spacing:.1em; color:{T['t3']}; text-transform:uppercase; padding:.5rem .4rem .25rem; margin-top:.3rem; }}
.sb-link {{ display:flex; align-items:center; gap:9px; padding:8px 10px; border-radius:9px; font-size:.82rem; font-weight:500; color:{T['t2']}; cursor:pointer; transition:all .15s; width:100%; border:none; background:transparent; white-space:nowrap; text-align:left; }}
.sb-link:hover  {{ background:rgba({rgb},.1);  color:{T['t1']}; }}
.sb-link.active {{ background:rgba({rgb},.15); color:{ac}; font-weight:600; }}
.sb-div {{ height:1px; background:{T['b1']}; margin:.6rem 0; }}
 
/* Theme swatches */
.sb-swatches {{ display:flex; gap:7px; padding:.3rem .4rem; flex-wrap:wrap; }}
.swatch {{ width:22px; height:22px; border-radius:50%; cursor:pointer; border:2.5px solid transparent; transition:transform .15s; box-shadow:0 1px 4px rgba(0,0,0,.3); }}
.swatch:hover {{ transform:scale(1.15); }}
.swatch.sel {{ border-color:{T['t1']}; box-shadow:0 0 0 2px {T['page']},0 0 0 4px {ac}; }}
 
/* ── Upload hero ── */
.up-hero {{
    text-align:center; padding:2rem 1.5rem 1.6rem;
    background:{T['card']}; border:1px solid {T['b1']};
    border-radius:18px; margin-bottom:1.2rem;
    position:relative; overflow:hidden;
}}
.up-hero::before {{
    content:''; position:absolute; top:-60px; right:-60px;
    width:220px; height:220px;
    background:radial-gradient(circle,rgba({rgb},.07),transparent 70%);
    border-radius:50%; pointer-events:none;
}}
.up-hero h1 {{ font-size:1.5rem; font-weight:800; letter-spacing:-.03em; color:{T['t1']}; margin-bottom:.35rem; }}
.up-hero h1 em {{ font-style:normal; color:{ac}; }}
.up-hero p {{ font-size:.82rem; color:{T['t2']}; max-width:400px; margin:0 auto; line-height:1.65; }}
.feat-row {{ display:flex; gap:5px; flex-wrap:wrap; justify-content:center; margin-top:.9rem; }}
.ftag {{ display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border-radius:20px; background:{T['panel']}; border:1px solid {T['b1']}; font-size:.67rem; font-weight:600; color:{T['t2']}; }}
 
/* ── Upload cards ── */
.up-card {{ background:{T['card']}; border:1px solid {T['b1']}; border-radius:18px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,.2); }}
.up-card-head {{ display:flex; align-items:center; gap:9px; padding:.8rem 1rem; border-bottom:1px solid {T['b1']}; background:{T['panel']}; }}
.up-card-ico {{ width:28px; height:28px; border-radius:7px; background:rgba({rgb},.15); border:1px solid rgba({rgb},.25); display:flex; align-items:center; justify-content:center; font-size:.85rem; }}
.up-card-lbl {{ font-size:.75rem; font-weight:700; color:{T['t1']}; }}
.up-card-sub {{ font-size:.62rem; color:{T['t3']}; margin-top:1px; }}
.up-card-body {{ padding:1rem; }}
 
/* ── Drop zone ── */
.dz {{ border:2px dashed {T['b2']}; border-radius:14px; padding:1.8rem 1rem; text-align:center; background:{T['panel']}; transition:all .2s; }}
.dz:hover {{ border-color:{ac}; background:rgba({rgb},.06); }}
.dz-ico {{ font-size:2.1rem; margin-bottom:.6rem; filter:drop-shadow(0 2px 8px rgba({rgb},.25)); }}
.dz-t {{ font-size:.9rem; font-weight:700; color:{T['t1']}; margin-bottom:.25rem; }}
.dz-s {{ font-size:.73rem; color:{T['t2']}; }}
.dz-br {{ color:{ac}; font-weight:600; }}
.file-ok {{ display:flex; align-items:center; gap:10px; padding:10px 13px; background:{T['gbg']}; border:1px solid rgba(63,185,80,.25); border-radius:11px; margin-bottom:.8rem; }}
.file-ok-n {{ font-size:.8rem; font-weight:700; color:{T['green']}; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.file-ok-m {{ font-size:.64rem; color:{T['t2']}; margin-top:1px; }}
 
/* ── Pipeline steps ── */
.pipe {{ display:flex; flex-direction:column; }}
.pstep {{ display:flex; align-items:center; gap:10px; padding:9px 11px; border-radius:10px; border:1px solid {T['b1']}; background:{T['panel']}; transition:all .2s; }}
.pstep.done {{ border-color:rgba(63,185,80,.3); background:{T['gbg']}; }}
.pstep.actv {{ border-color:rgba({rgb},.4); background:rgba({rgb},.06); box-shadow:0 0 0 3px rgba({rgb},.1); }}
.pconn {{ width:1.5px; height:7px; background:{T['b1']}; margin-left:17px; }}
.pconn.done {{ background:rgba(63,185,80,.4); }}
.pn {{ width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:.68rem; font-weight:700; flex-shrink:0; }}
.pn-i {{ background:{T['panel']}; color:{T['t3']}; border:1.5px solid {T['b1']}; }}
.pn-d {{ background:{T['gbg']}; color:{T['green']}; border:1.5px solid rgba(63,185,80,.4); }}
.pn-a {{ background:rgba({rgb},.15); color:{ac}; border:1.5px solid rgba({rgb},.4); animation:pb 1s infinite; }}
@keyframes pb {{ 0%,100%{{opacity:1}} 50%{{opacity:.35}} }}
.pi {{ flex:1; min-width:0; }}
.pn-lbl {{ font-size:.78rem; font-weight:600; color:{T['t1']}; }}
.pn-lbl.dn {{ color:{T['green']}; }}
.pn-lbl.av {{ color:{ac}; }}
.pd {{ font-size:.62rem; color:{T['t3']}; margin-top:1px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.pbdg {{ font-size:.6rem; font-weight:700; padding:2px 8px; border-radius:20px; flex-shrink:0; }}
.pbdg-i {{ background:{T['panel']}; color:{T['t3']}; }}
.pbdg-d {{ background:{T['gbg']}; color:{T['green']}; }}
.pbdg-a {{ background:rgba({rgb},.15); color:{ac}; }}
 
/* Meta stats */
.meta-g {{ display:grid; grid-template-columns:1fr 1fr; gap:7px; }}
.meta-i {{ background:{T['panel']}; border:1px solid {T['b1']}; border-radius:10px; padding:10px 12px; text-align:center; }}
.meta-v {{ font-size:1.25rem; font-weight:800; color:{ac}; font-family:'JetBrains Mono',monospace; line-height:1; }}
.meta-k {{ font-size:.6rem; font-weight:700; color:{T['t3']}; letter-spacing:.07em; margin-top:4px; text-transform:uppercase; }}
.meta-file {{ grid-column:1/-1; background:{T['panel']}; border:1px solid {T['b1']}; border-radius:10px; padding:9px 12px; display:flex; align-items:center; gap:9px; }}
.mfn {{ font-size:.78rem; font-weight:600; color:{T['t1']}; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.mfm {{ font-size:.63rem; color:{T['t3']}; margin-top:1px; }}
.ready-bar {{ display:flex; align-items:center; gap:12px; padding:12px 14px; background:linear-gradient(135deg,{T['gbg']},rgba(63,185,80,.04)); border:1.5px solid rgba(63,185,80,.3); border-radius:12px; margin-top:.75rem; }}
.rdot {{ width:8px; height:8px; border-radius:50%; background:{T['green']}; box-shadow:0 0 0 3px rgba(63,185,80,.2); animation:pb 2s infinite; flex-shrink:0; }}
.rtxt {{ font-size:.8rem; font-weight:700; color:{T['green']}; }}
.rsub {{ font-size:.63rem; color:{T['t2']}; margin-top:2px; }}
 
/* ── FIX 5: Chat page ── */
.chat-outer {{
    position: fixed; top: 56px; left: 0; right: 0; bottom: 0;
    display: flex; flex-direction: column; align-items: center;
    background: {T['page']}; padding: .75rem 1.5rem 0;
}}
.chat-shell {{
    width: 100%; max-width: 860px;
    display: flex; flex-direction: column;
    flex: 1; min-height: 0;
    background: {T['card']}; border: 1px solid {T['b1']};
    border-radius: 18px 18px 0 0; overflow: hidden;
    box-shadow: {T['shd']};
}}
.chat-top {{
    display: flex; align-items: center; justify-content: space-between;
    padding: .65rem 1.2rem; border-bottom: 1px solid {T['b1']};
    background: {T['panel']}; flex-shrink: 0;
}}
.chat-tname {{ font-size: .84rem; font-weight: 700; color: {T['t1']}; }}
.chat-tmeta {{ font-size: .67rem; color: {T['t2']}; margin-top: 1px; }}

.chat-msgs {{
    flex: 1; overflow-y: auto; overflow-x: hidden;
    padding: 1.5rem 2rem 1rem;
    display: flex; flex-direction: column; gap: 1.5rem;
    scroll-behavior: smooth; min-height: 0;
    scrollbar-width: thin; scrollbar-color: {T['b2']} transparent;
}}
.chat-msgs::-webkit-scrollbar {{ width: 4px; }}
.chat-msgs::-webkit-scrollbar-thumb {{ background: {T['b2']}; border-radius: 4px; }}

.mrow {{ display: flex; gap: 12px; animation: fadeUp .2s ease; }}
@keyframes fadeUp {{ from{{opacity:0;transform:translateY(6px)}} to{{opacity:1;transform:translateY(0)}} }}
.mrow.user {{ flex-direction: row-reverse; }}
.mav {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: .8rem; flex-shrink: 0; margin-top: 2px; }}
.mav-u {{ background: linear-gradient(135deg,{ac},{ac2}); box-shadow: 0 2px 8px rgba({rgb},.3); }}
.mav-b {{ background: {T['panel']}; border: 1px solid {T['b1']}; }}
.mbody {{ display: flex; flex-direction: column; max-width: 80%; }}
.mrow.user .mbody {{ align-items: flex-end; }}

.bub-u {{
    background: linear-gradient(135deg,{ac},{ac2}); color: #fff;
    border-radius: 18px 4px 18px 18px; padding: 10px 15px;
    font-size: .87rem; line-height: 1.65;
    box-shadow: 0 2px 10px rgba({rgb},.25);
}}
.bub-b {{
    background: {T['card']}; border: 1px solid {T['b1']};
    border-radius: 4px 18px 18px 18px; padding: 14px 16px;
    font-size: .875rem; line-height: 1.82;
    box-shadow: 0 1px 4px rgba(0,0,0,.1);
}}
.bub-b h2 {{ font-size: .9rem; font-weight: 700; color: {T['t1']}; margin: .9em 0 .35em; padding-bottom: .3em; border-bottom: 1px solid {T['b1']}; }}
.bub-b h3 {{ font-size: .84rem; font-weight: 600; color: {ac}; margin: .75em 0 .25em; }}
.bub-b p  {{ margin: 0 0 .65em; line-height: 1.82; color: {T['t1']}; }}
.bub-b p:last-child {{ margin-bottom: 0; }}
.bub-b ul, .bub-b ol {{ padding-left: 1.4em; margin: .3em 0 .7em; }}
.bub-b li {{ margin: .28em 0; line-height: 1.75; color: {T['t1']}; }}
.bub-b strong {{ font-weight: 600; color: {T['t1']}; }}
.bub-b code {{ background: {T['panel']}; border: 1px solid {T['b1']}; padding: 1px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: .78em; color: {ac}; }}
.bub-b pre {{ background: #0d1117; border: 1px solid {T['b2']}; border-radius: 10px; padding: 14px 16px; overflow-x: auto; margin: .6em 0 .9em; }}
.bub-b pre code {{ background: none; border: none; padding: 0; color: #7dd3fc; font-size: .78rem; line-height: 1.7; }}
.bub-b blockquote {{ border-left: 3px solid {ac}; padding-left: 12px; color: {T['t2']}; margin: .5em 0; font-style: italic; }}
.mmeta {{ display: flex; gap: 5px; margin-top: 6px; flex-wrap: wrap; }}

.chat-empty {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .6rem; opacity: .5; text-align: center; padding: 2rem; }}
.ce-ico {{ font-size: 2.8rem; margin-bottom: .2rem; }}
.ce-t {{ font-size: .95rem; font-weight: 700; color: {T['t1']}; }}
.ce-s {{ font-size: .78rem; color: {T['t2']}; max-width: 320px; line-height: 1.65; }}

/* ── FIX 6: Sources page ── */
.src-col {{
    background: {T['card']}; border: 1px solid {T['b1']};
    border-radius: 16px; overflow: hidden;
    box-shadow: {T['shd']};
    height: calc(100vh - 110px);
    display: flex; flex-direction: column;
}}
.src-head {{ display: flex; align-items: center; gap: 8px; padding: .7rem 1rem; border-bottom: 1px solid {T['b1']}; background: {T['panel']}; flex-shrink: 0; }}
.src-htitle {{ font-size: .7rem; font-weight: 700; letter-spacing: .09em; color: {T['t3']}; text-transform: uppercase; }}
.src-body {{ flex: 1; overflow-y: auto; padding: .75rem; min-height: 0; scrollbar-width: thin; scrollbar-color: {T['b2']} transparent; }}
.src-body::-webkit-scrollbar {{ width: 3px; }}
.src-body::-webkit-scrollbar-thumb {{ background: {T['b2']}; border-radius: 4px; }}
.pcard {{ background: {T['panel']}; border: 1px solid {T['b1']}; border-radius: 10px; overflow: hidden; margin-bottom: 8px; transition: box-shadow .15s; }}
.pcard:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,.25); }}
.pcard-h {{ display: flex; align-items: center; justify-content: space-between; padding: 6px 11px; background: {T['card']}; border-bottom: 1px solid {T['b1']}; }}
.pcard-n {{ font-size: .67rem; font-weight: 700; color: {ac}; font-family: 'JetBrains Mono', monospace; }}
.pcard-s {{ font-size: .62rem; color: {T['t3']}; font-family: 'JetBrains Mono', monospace; }}
.pcard-b {{ padding: 10px 11px; font-size: .78rem; line-height: 1.75; color: {T['t2']}; }}

/* FIX 7 — Button styles */
.stButton > button {{
    background: {T['panel']} !important; border: 1.5px solid {T['b2']} !important;
    color: {T['t2']} !important; border-radius: 9px !important;
    font-family: 'Inter', sans-serif !important; font-size: .79rem !important;
    font-weight: 500 !important; transition: all .15s !important;
    padding: 7px 16px !important;
}}
.stButton > button:hover {{
    border-color: {ac} !important; color: {ac} !important;
    background: rgba({rgb},.08) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg,{ac},{ac2}) !important;
    border-color: transparent !important; color: #fff !important;
    box-shadow: 0 2px 10px rgba({rgb},.3) !important;
}}
.stButton > button[kind="primary"]:hover {{ opacity: .9 !important; color: #fff !important; }}

/* Streamlit input overrides */
[data-testid="stFileUploader"] {{ background: transparent !important; border: none !important; padding: 0 !important; }}
.stProgress > div > div {{ background: linear-gradient(90deg,{ac},{ac2}) !important; border-radius: 4px !important; height: 3px !important; }}
[data-testid="stProgressBarMessage"] {{ font-size: .72rem !important; color: {T['t2']} !important; }}
[data-testid="stChatInput"] {{ padding: 0 !important; background: transparent !important; }}
[data-testid="stChatInput"] > div {{ background: transparent !important; border: none !important; box-shadow: none !important; }}
[data-testid="stChatInput"] textarea {{
    background: {T['inp']} !important; border: 1.5px solid {T['b2']} !important;
    border-radius: 12px !important; color: {T['t1']} !important;
    font-family: 'Inter', sans-serif !important; font-size: .86rem !important;
    padding: 10px 14px !important; resize: none !important;
}}
[data-testid="stChatInput"] textarea:focus {{ border-color: {ac} !important; box-shadow: 0 0 0 3px rgba({rgb},.12) !important; }}
[data-testid="stChatInput"] textarea::placeholder {{ color: {T['t3']} !important; }}
details summary {{ background: {T['panel']} !important; border: 1px solid {T['b1']} !important; border-radius: 9px !important; font-size: .77rem !important; color: {T['t2']} !important; padding: 7px 12px !important; }}
details > div {{ background: {T['panel']} !important; border: 1px solid {T['b1']} !important; border-top: none !important; border-radius: 0 0 9px 9px !important; padding: 10px !important; }}
.stTextInput input {{ background: {T['inp']} !important; border: 1.5px solid {T['b2']} !important; border-radius: 9px !important; color: {T['t1']} !important; font-family: 'JetBrains Mono', monospace !important; font-size: .77rem !important; padding: 8px 11px !important; }}
.stTextInput input:focus {{ border-color: {ac} !important; }}
label {{ color: {T['t2']} !important; font-size: .77rem !important; font-weight: 500 !important; }}
.stSelectbox [data-baseweb="select"] > div {{ background: {T['inp']} !important; border: 1.5px solid {T['b2']} !important; border-radius: 9px !important; font-size: .8rem !important; color: {T['t1']} !important; }}
.stAlert {{ border-radius: 10px !important; font-size: .78rem !important; }}
.stSuccess {{ background: {T['gbg']} !important; border: 1px solid rgba(63,185,80,.3) !important; color: {T['green']} !important; }}
.stError {{ background: rgba(248,113,113,.08) !important; border: 1px solid rgba(248,113,113,.25) !important; color: #f87171 !important; }}
[data-testid="stChatMessage"] {{ background: transparent !important; border: none !important; padding: 0 !important; }}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def mpill(model, src):
    if model.startswith("groq/"): return pill(f"🟢 {model.split('/')[1][:20]}", "pg")
    if model.startswith("openai/"): return pill("🤖 GPT-3.5", "pb")
    if "wiki" in src: return pill("🌐 Wikipedia", "py")
    return pill("📄 Context", "ps")
def spill(src):
    return pill("📗 Textbook", "pp") if "textbook" in src else pill("🌐 Wikipedia", "py")

# ═══════════════════════════════════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════════════════════════════════
v = st.session_state.view
idx = st.session_state.indexed
page_labels = {"upload":"📂 Upload & Index","chat":"💬 Chat","sources":"🔍 Sources & PDF"}
llm_badge = (pill("🟢 Groq","pg") if has_groq
             else pill("🤖 OpenAI","pb") if has_openai
             else pill("⚠ No LLM","py"))
idx_badge = pill("● Indexed","pg") if idx else pill("○ Not Indexed","ps")

st.markdown(f"""
<div class="rb-topbar">
  <div class="rb-topbar-inner">
    <div class="rb-brand">
      <div class="rb-logo">📚</div>
      <div class="rb-brand-name">ResolvaBot <span>LLM</span></div>
    </div>
    <div class="rb-breadcrumb">
      <span class="rb-sep">·</span>
      <span class="rb-page-name">{page_labels.get(v,'')}</span>
    </div>
    <div class="rb-topbar-right">
      {llm_badge}&nbsp;{idx_badge}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hamburger toggle ──────────────────────────────────────────────────────────
# FIX: marker div so CSS :has() can target ONLY the hamburger stHorizontalBlock
# (not the upload columns), avoiding the :first-of-type collision bug
st.markdown(
    '<div id="rb-hamb-before" style="display:none;height:0;overflow:hidden;'
    'margin:0;padding:0;line-height:0;font-size:0"></div>',
    unsafe_allow_html=True,
)
hamb_col = st.columns([1, 20])[0]
with hamb_col:
    hamb_label = "✕" if st.session_state.sidebar_open else "☰"
    if st.button(hamb_label, key="hamburger"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

st.markdown(f"""
<style>
/*
  HAMBURGER FIX:
  Streamlit wraps every widget in its own elementContainer div, which is a
  direct child of stVerticalBlock. So stMarkdownContainer and stHorizontalBlock
  are never direct siblings — the :has(marker) + stHorizontalBlock selector
  always fails. Correct approach: target the elementContainer SIBLINGS inside
  stVerticalBlock, then descend into the stHorizontalBlock inside.
*/
[data-testid="stVerticalBlock"] > div:has(#rb-hamb-before) + div [data-testid="stHorizontalBlock"] {{
    position: fixed; top: 0; left: 0; z-index: 1100;
    height: 56px; display: flex; align-items: center;
    padding: 0 1rem; background: transparent;
    pointer-events: auto;
}}
[data-testid="stVerticalBlock"] > div:has(#rb-hamb-before) + div [data-testid="stHorizontalBlock"] .stButton > button {{
    background: transparent !important; border: none !important;
    color: {T['t2']} !important; font-size: 1.1rem !important;
    padding: 4px 8px !important; border-radius: 6px !important;
    height: 32px !important; width: 36px !important;
    min-width: 0 !important;
}}
[data-testid="stVerticalBlock"] > div:has(#rb-hamb-before) + div [data-testid="stHorizontalBlock"] .stButton > button:hover {{
    background: rgba({rgb},.1) !important; color: {T['t1']} !important;
    border-color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)



# ── Sidebar overlay ────────────────────────────────────────────────────────────

# ── Sidebar overlay ────────────────────────────────────────────────────────────

if st.session_state.sidebar_open:

    cur = st.session_state.theme

    SWATCH_DATA = [
        ("dark",   "\U0001f535", "Dark"),
        ("light",  "\u2b1c",     "Light"),
        ("indigo", "\U0001f7e3", "Indigo"),
        ("teal",   "\U0001f7e2", "Teal"),
        ("rose",   "\U0001f534", "Rose"),
        ("amber",  "\U0001f7e0", "Amber"),
        ("mono",   "\u26ab",     "Mono"),
    ]
    _theme_list = list(t for t, *_ in SWATCH_DATA)
    _active_i   = _theme_list.index(cur) + 1  # 1-based nth-child

    st.markdown('<div class="rb-sidebar-overlay"></div>', unsafe_allow_html=True)

    st.markdown(f"""
<style>
/* ── Panel shell ── */
.rb-sidebar {{
    position:fixed;top:56px;left:0;bottom:0;width:240px;z-index:950;
    background:{T['card']};border-right:1px solid {T['b1']};
    box-shadow:10px 0 30px rgba(0,0,0,.45);
    animation:sbIn .18s cubic-bezier(.4,0,.2,1);pointer-events:none;
}}
@keyframes sbIn{{from{{transform:translateX(-240px);opacity:0}}to{{transform:translateX(0);opacity:1}}}}

/* ── Widget container ── */
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) {{
    position:fixed !important;top:56px !important;left:0 !important;
    width:240px !important;height:calc(100vh - 56px) !important;
    z-index:960 !important;padding:0 !important;margin:0 !important;
    background:{T['card']} !important;
    overflow-y:auto !important;overflow-x:hidden !important;
    scrollbar-width:thin;scrollbar-color:{T['b2']} transparent;
    pointer-events:auto !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root)::-webkit-scrollbar{{width:3px;}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root)::-webkit-scrollbar-thumb{{
    background:{T['b2']};border-radius:4px;
}}

/* ── Section label ── */
.sb-sec {{
    display:block;font-size:.58rem;font-weight:800;letter-spacing:.14em;
    text-transform:uppercase;color:{T['t3']};padding:.85rem 12px .3rem;
}}
/* ── Divider ── */
.sb-hr{{height:1px;background:{T['b1']};margin:.3rem 12px;}}

/* ── Navigation buttons ── */
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-nav .stButton>button {{
    width:calc(100% - 16px) !important;
    margin:4px 8px !important;
    padding:0 12px !important;
    border-radius:8px !important;
    height:36px !important;
    font-size:.82rem !important;
    font-weight:500 !important;
    text-align:left !important;
    justify-content:flex-start !important;
    border:1px solid {T['b1']} !important;
    background:transparent !important;
    color:{T['t2']} !important;
    transition:all .14s !important;
    line-height:1 !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-nav .stButton>button:hover{{
    background:rgba({rgb},.1) !important;
    color:{ac} !important;
    border-color:rgba({rgb},.3) !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-nav .stButton>button[kind="primary"]{{
    background:linear-gradient(135deg,{ac},{ac2}) !important;
    color:#fff !important;
    font-weight:600 !important;
    border-color:transparent !important;
    box-shadow:0 2px 10px rgba({rgb},.3) !important;
}}

/* ── Swatch row: 7 circles, all inside 240px ── */
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-sw [data-testid="stHorizontalBlock"] {{
    display:flex !important;
    flex-wrap:nowrap !important;
    justify-content:space-between !important;
    align-items:center !important;
    padding:4px 12px 8px !important;
    margin:0 !important;
    gap:0 !important;
    max-width:240px !important;
    overflow:hidden !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-sw [data-testid="column"] {{
    flex:0 0 26px !important;
    width:26px !important;
    min-width:0 !important;
    max-width:26px !important;
    padding:0 !important;
    overflow:hidden !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-sw .stButton>button {{
    width:22px !important;
    height:22px !important;
    padding:0 !important;
    min-width:0 !important;
    border-radius:50% !important;
    font-size:.85rem !important;
    border:2px solid transparent !important;
    background:transparent !important;
    line-height:22px !important;
    transition:transform .12s !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    overflow:hidden !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-sw .stButton>button > div {{
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    padding:0 !important;
    margin:0 !important;
    line-height:1 !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-sw .stButton>button p {{
    margin:0 !important;
    padding:0 !important;
    line-height:1 !important;
    font-size:.85rem !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-sw .stButton>button:hover{{
    transform:scale(1.25) !important;
}}
/* Active swatch ring */
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-sw [data-testid="column"]:nth-child({_active_i}) .stButton>button {{
    border-color:{T['t1']} !important;
    box-shadow:0 0 0 2px {T['page']},0 0 0 4px {ac} !important;
    transform:scale(1.15) !important;
}}

/* ── File info card ── */
.sb-file {{
    margin:.2rem 8px .35rem;
    padding:8px 11px;
    background:rgba({rgb},.07);
    border:1px solid rgba({rgb},.18);
    border-radius:9px;
    font-size:.7rem;
    color:{T['t2']};
    line-height:1.55;
}}
.sb-file b{{color:{T['t1']};font-weight:600;}}

/* ── Action buttons (Unload / Clear Chat) ── */
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-act .stButton>button {{
    width:calc(100% - 16px) !important;
    margin:4px 8px !important;
    padding:0 12px !important;
    border-radius:8px !important;
    height:32px !important;
    font-size:.76rem !important;
    font-weight:500 !important;
    text-align:left !important;
    justify-content:flex-start !important;
    border:1px solid {T['b1']} !important;
    background:{T['panel']} !important;
    color:{T['t2']} !important;
    transition:all .12s !important;
    line-height:1 !important;
}}
div[data-testid="stVerticalBlock"]:has(.rb-sb-root) .sb-act .stButton>button:hover{{
    background:rgba(248,113,113,.1) !important;
    border-color:rgba(248,113,113,.35) !important;
    color:#f87171 !important;
}}

/* ── Bottom padding ── */
.sb-bottom-pad{{height:1rem;}}
</style>
<div class="rb-sidebar"></div>
""", unsafe_allow_html=True)

    # ── Widget layer ──────────────────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="rb-sb-root"></div>', unsafe_allow_html=True)

        # Small top gap so content doesn't touch the very top of the panel
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

        # Navigation
        st.markdown('<span class="sb-sec">Navigation</span>', unsafe_allow_html=True)
        st.markdown('<div class="sb-nav">', unsafe_allow_html=True)

        if st.button("\U0001f4c2  Upload & Index", key="sb_upload",
                     use_container_width=True,
                     type="primary" if v=="upload" else "secondary"):
            st.session_state.sidebar_open = False; go("upload")

        _cdot = " \u25cf" if v == "chat" else ""
        if st.button(f"\U0001f4ac  Chat{_cdot}", key="sb_chat",
                     use_container_width=True,
                     type="primary" if v=="chat" else "secondary",
                     disabled=not idx):
            st.session_state.sidebar_open = False; go("chat")

        if st.button("\U0001f50d  Sources & PDF", key="sb_src",
                     use_container_width=True,
                     type="primary" if v=="sources" else "secondary",
                     disabled=not idx):
            st.session_state.sidebar_open = False; go("sources")

        st.markdown('</div>', unsafe_allow_html=True)

        # Theme swatches
        st.markdown('<div class="sb-hr"></div>', unsafe_allow_html=True)
        st.markdown('<span class="sb-sec">Color Theme</span>', unsafe_allow_html=True)
        st.markdown('<div class="sb-sw">', unsafe_allow_html=True)

        _swcols = st.columns(7, gap="small")
        for _i, (_tk, _emoji, _name) in enumerate(SWATCH_DATA):
            with _swcols[_i]:
                if st.button(_emoji, key=f"sw_{_tk}", help=_name):
                    st.session_state.theme = _tk
                    st.session_state.sidebar_open = False
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Document info + action buttons
        if idx:
            st.markdown('<div class="sb-hr"></div>', unsafe_allow_html=True)
            st.markdown('<span class="sb-sec">Document</span>', unsafe_allow_html=True)

            _fn = st.session_state.last_file[:22]+("\u2026" if len(st.session_state.last_file)>22 else "")
            st.markdown(
                f'<div class="sb-file">'
                f'<b>\U0001f4c4 {_fn}</b><br>'
                f'{st.session_state.pages}p \u00b7 {st.session_state.chunks} chunks \u00b7 {st.session_state.file_size}'
                f'</div>',
                unsafe_allow_html=True
            )

            # Space between file card and first action button
            st.markdown('<div style="height:.25rem"></div>', unsafe_allow_html=True)

            st.markdown('<div class="sb-act">', unsafe_allow_html=True)
            if st.button("\U0001f4c2  Unload PDF", key="sb_unload",
                         use_container_width=True):
                for _k in ("indexed","step","history","cur_passages"):
                    st.session_state[_k] = False if _k=="indexed" else 0 if _k=="step" else []
                st.session_state.last_file_bytes=None
                st.session_state.view="upload"
                st.session_state.sidebar_open=False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.history:
            st.markdown('<div class="sb-act">', unsafe_allow_html=True)
            if st.button("\U0001f5d1  Clear Chat", key="sb_clear",
                         use_container_width=True):
                st.session_state.history=[]
                st.session_state.cur_passages=[]
                st.session_state.sidebar_open=False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sb-bottom-pad"></div>', unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  VIEW 1: UPLOAD                                          ║
# ║  FIX: Removed rb-page/rb-center wrapper divs.           ║
# ║  stMainBlockContainer already centers to 860px.          ║
# ║  All content now flows top-to-bottom in the same DOM.   ║
# ╚══════════════════════════════════════════════════════════╝
if v == "upload":

    # Hero — rendered as pure HTML block, flows first
    st.markdown(f"""
<div class="up-hero">
  <h1>Upload your <em>Textbook</em></h1>
  <p>Drop any PDF — algorithms, CS, math, science — and ResolvaBot will extract, chunk, and index it for AI-powered Q&amp;A.</p>
  <div class="feat-row">
    <span class="ftag">⚡ RAPTOR Index</span>
    <span class="ftag">🔍 BM25 + FAISS</span>
    <span class="ftag">🤖 Llama 3.3 70B</span>
    <span class="ftag">🌲 Hierarchical</span>
    <span class="ftag">📖 Wikipedia fallback</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # API keys (compact, only when no key)
    if not (has_groq or has_openai):
        with st.expander("🔑 Set LLM API Key (required for answers)", expanded=True):
            k1, k2 = st.columns(2)
            with k1:
                gk = st.text_input("Groq Key (free)", value=st.session_state.groq_key,
                                   type="password", placeholder="gsk_...", help="console.groq.com")
                if gk != st.session_state.groq_key:
                    st.session_state.groq_key=gk; os.environ["GROQ_API_KEY"]=gk; st.rerun()
            with k2:
                ok = st.text_input("OpenAI Key", value=st.session_state.openai_key,
                                   type="password", placeholder="sk-...")
                if ok != st.session_state.openai_key:
                    st.session_state.openai_key=ok; os.environ["OPENAI_API_KEY"]=ok; st.rerun()

    # Two-column layout — placed AFTER hero in the same flow
    lc, rc = st.columns([1.1, 0.9], gap="medium")

    with lc:
        st.markdown("""<div class="up-card">
  <div class="up-card-head">
    <div class="up-card-ico">📄</div>
    <div><div class="up-card-lbl">PDF Textbook</div><div class="up-card-sub">Drag & drop or browse</div></div>
  </div>
  <div class="up-card-body">""", unsafe_allow_html=True)

        if st.session_state.indexed:
            st.markdown(f"""<div class="file-ok">
  <div style="font-size:1.4rem">📄</div>
  <div style="flex:1;min-width:0">
    <div class="file-ok-n">{st.session_state.last_file}</div>
    <div class="file-ok-m">{st.session_state.file_size} · {st.session_state.pages} pages</div>
  </div>
  <div style="font-size:1.2rem">✅</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="dz">
  <div class="dz-ico">☁️</div>
  <div class="dz-t">Drop PDF here</div>
  <div class="dz-s">or <span class="dz-br">browse files</span></div>
</div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("", type=["pdf"],
                                    label_visibility="collapsed",
                                    key="pdf_uploader")
        st.markdown('</div></div>', unsafe_allow_html=True)

        if st.session_state.indexed:
            if st.button("💬 Start Chatting →", type="primary", use_container_width=True):
                go("chat")

    with rc:
        STEPS = [
            ("📝","Extract Text","PyMuPDF page reader"),
            ("✂️","Chunk Text","NLTK sentence chunking"),
            ("🌲","RAPTOR Index","GMM clustering hierarchy"),
            ("⚡","FAISS Store","Dense vector embeddings"),
            ("📑","BM25 Index","Keyword inverted index"),
        ]
        s = st.session_state.step

        st.markdown("""<div class="up-card">
  <div class="up-card-head">
    <div class="up-card-ico">⚙️</div>
    <div><div class="up-card-lbl">Indexing Pipeline</div><div class="up-card-sub">5-step workflow</div></div>
  </div>
  <div class="up-card-body"><div class="pipe">""", unsafe_allow_html=True)

        step_placeholders = []
        for i, (icon, name, desc) in enumerate(STEPS, 1):
            is_last = (i == len(STEPS))
            if s >= i:      sc,nc,bc,bl,nl = "done","pn-d","pbdg-d","✓ Done","dn"
            elif s==i-1 and uploaded and not st.session_state.indexed:
                            sc,nc,bc,bl,nl = "actv","pn-a","pbdg-a","Running…","av"
            else:           sc,nc,bc,bl,nl = "","pn-i","pbdg-i",str(i),""
            conn = "" if is_last else f'<div class="pconn {"done" if s>=i else ""}"></div>'
            ph = st.empty()
            ph.markdown(f"""<div class="pstep {sc}">
  <div class="pn {nc}">{icon if s>=i else str(i)}</div>
  <div class="pi"><div class="pn-lbl {nl}">{name}</div><div class="pd">{desc}</div></div>
  <div class="pbdg {bc}">{bl}</div>
</div>{conn}""", unsafe_allow_html=True)
            step_placeholders.append(ph)

        st.markdown('</div></div></div>', unsafe_allow_html=True)

    # Meta stats card
    if st.session_state.indexed:
        fname = st.session_state.last_file[:36]+("…" if len(st.session_state.last_file)>36 else "")
        st.markdown(f"""
<div class="up-card" style="margin-top:.9rem">
  <div class="up-card-head">
    <div class="up-card-ico">📊</div>
    <div style="flex:1"><div class="up-card-lbl">Document Summary</div><div class="up-card-sub">Indexing complete</div></div>
    {pill("✓ Ready to Chat","pg")}
  </div>
  <div class="up-card-body">
    <div class="meta-g">
      <div class="meta-i"><div class="meta-v">{st.session_state.pages}</div><div class="meta-k">Pages</div></div>
      <div class="meta-i"><div class="meta-v">{st.session_state.chunks}</div><div class="meta-k">Chunks</div></div>
      <div class="meta-i"><div class="meta-v">{st.session_state.nodes}</div><div class="meta-k">Nodes</div></div>
      <div class="meta-i"><div class="meta-v">{st.session_state.file_size}</div><div class="meta-k">Size</div></div>
      <div class="meta-file">
        <div style="font-size:1.3rem">📄</div>
        <div style="flex:1;min-width:0">
          <div class="mfn">{fname}</div>
          <div class="mfm">SBERT all-MiniLM-L6-v2 · 384-dim</div>
        </div>
      </div>
    </div>
    <div class="ready-bar">
      <div class="rdot"></div>
      <div><div class="rtxt">Ready to chat!</div><div class="rsub">{st.session_state.chunks} chunks · {st.session_state.pages} pages</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Indexing with real-time step updates
    if uploaded and not st.session_state.indexed:
        def update_step(i, placeholders, steps_data, current_step):
            for j, (icon, name, desc) in enumerate(steps_data, 1):
                is_last = (j == len(steps_data))
                if current_step >= j:   sc,nc,bc,bl,nl = "done","pn-d","pbdg-d","✓ Done","dn"
                elif current_step==j-1: sc,nc,bc,bl,nl = "actv","pn-a","pbdg-a","Running…","av"
                else:                   sc,nc,bc,bl,nl = "","pn-i","pbdg-i",str(j),""
                conn = "" if is_last else f'<div class="pconn {"done" if current_step>=j else ""}"></div>'
                placeholders[j-1].markdown(f"""<div class="pstep {sc}">
  <div class="pn {nc}">{icon if current_step>=j else str(j)}</div>
  <div class="pi"><div class="pn-lbl {nl}">{name}</div><div class="pd">{desc}</div></div>
  <div class="pbdg {bc}">{bl}</div>
</div>{conn}""", unsafe_allow_html=True)

        prog = st.progress(0)
        try:
            from extraction   import extract_text_from_pdf_bytes
            from chunking     import chunk_pages
            from raptor_index import build_raptor_index
            from vector_store import VectorStore
            from retrieval    import BM25Index, HybridRetriever

            raw = uploaded.read()
            sz  = f"{len(raw)/1024:.0f} KB" if len(raw)<1024*1024 else f"{len(raw)/1024/1024:.1f} MB"
            st.session_state.file_size=sz; st.session_state.last_file_bytes=raw

            st.session_state.step=0; update_step(0,step_placeholders,STEPS,0)
            prog.progress(5, text="📄 Extracting text…")
            try: pages = extract_text_from_pdf_bytes(raw)
            except ValueError as e: st.error(str(e)); st.stop()
            if not any(pg["text"].strip() for pg in pages):
                st.error("No readable text found."); st.stop()

            st.session_state.step=1; update_step(0,step_placeholders,STEPS,1)
            prog.progress(22, text="✂️ Chunking text…")
            chunks = chunk_pages(pages, chunk_size=100)
            if not chunks: st.error("Chunking returned 0 results."); st.stop()

            st.session_state.step=2; update_step(0,step_placeholders,STEPS,2)
            prog.progress(42, text="🌲 Building RAPTOR…")
            nodes = build_raptor_index(chunks, max_levels=2, use_llm=False)

            st.session_state.step=3; update_step(0,step_placeholders,STEPS,3)
            prog.progress(65, text="⚡ Indexing FAISS…")
            vs = VectorStore(); vs.add_nodes(nodes)

            st.session_state.step=4; update_step(0,step_placeholders,STEPS,4)
            prog.progress(83, text="📑 Building BM25…")
            bm25 = BM25Index()
            bm25.build([{"chunk_id":n.node_id,"page":n.page,"level":n.level,"text":n.text} for n in nodes])

            st.session_state.step=5; prog.progress(100, text="✅ Done!")
            from retrieval import HybridRetriever
            st.session_state.retriever = HybridRetriever(bm25, vs)
            st.session_state.indexed   = True
            st.session_state.last_file = uploaded.name
            st.session_state.pages     = len(pages)
            st.session_state.chunks    = len(chunks)
            st.session_state.nodes     = len(nodes)
            st.rerun()
        except Exception as e:
            import traceback; st.error(f"Error: {e}")
            with st.expander("Details"): st.code(traceback.format_exc())

# ╔══════════════════════════════════════════════════════════╗
# ║  VIEW 2: CHAT  (FIX 5)                                   ║
# ╚══════════════════════════════════════════════════════════╝
elif v == "chat":
    if not st.session_state.indexed:
        st.warning("Upload and index a PDF first.")
        if st.button("← Go to Upload"): go("upload")
    else:
        llm_lbl = ("Groq · Llama 3.3 70B" if has_groq
                   else "OpenAI · GPT-3.5" if has_openai
                   else "Wikipedia fallback")
        n = st.session_state.chunks

        st.markdown(f'<div class="chat-outer">', unsafe_allow_html=True)
        st.markdown(f"""
<div class="chat-shell">
  <div class="chat-top">
    <div>
      <div class="chat-tname">💬 {st.session_state.last_file}</div>
      <div class="chat-tmeta">{n} chunks indexed · {llm_lbl}</div>
    </div>
    <div style="display:flex;gap:6px;align-items:center">
      {pill("🟢 Groq","pg") if has_groq else pill("⚠ No LLM","py")}
      {pill(f"{n} chunks","ps")}
    </div>
  </div>
  <div class="chat-msgs" id="chatbox">
""", unsafe_allow_html=True)

        if not st.session_state.history:
            st.markdown("""<div class="chat-empty">
  <div class="ce-ico">💬</div>
  <div class="ce-t">Start a conversation</div>
  <div class="ce-s">Ask anything about your textbook. I'll retrieve the most relevant passages and synthesize a complete, structured answer.</div>
</div>""", unsafe_allow_html=True)

        for msg in st.session_state.history:
            if msg["role"] == "user":
                st.markdown(f"""
<div class="mrow user">
  <div class="mav mav-u">🙋</div>
  <div class="mbody">
    <div class="bub-u">{html.escape(msg["content"])}</div>
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                err = msg.get("llm_error")
                if err:
                    st.markdown(f'<div style="background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.2);border-radius:8px;padding:8px 12px;font-size:.72rem;color:#f87171;margin-bottom:6px">⚠ {html.escape(str(err))}</div>', unsafe_allow_html=True)
                sp = spill(msg.get("source","")); mp = mpill(msg.get("model",""),msg.get("source",""))

                st.markdown('<div class="mrow"><div class="mav mav-b">🤖</div><div class="mbody" style="max-width:88%"><div class="bub-b">', unsafe_allow_html=True)
                st.markdown(msg["content"])
                st.markdown(f'</div><div class="mmeta">{sp}&nbsp;{mp}</div></div></div>', unsafe_allow_html=True)

                if msg.get("passages"):
                    with st.expander(f"📋 {len(msg['passages'])} source passages", expanded=False):
                        for j, r in enumerate(msg["passages"][:6], 1):
                            pg  = f"Page {r['page']}" if r.get("page",-1)>0 else "Summary"
                            scr = r.get("rrf_score",0)
                            txt = r["text"]
                            cr  = sum(1 for c in txt if c in "{}()<>;=") / max(len(txt),1)
                            st.markdown(f'<div class="pcard"><div class="pcard-h"><span class="pcard-n">#{j} · {pg}</span><span class="pcard-s">{scr:.4f}</span></div>', unsafe_allow_html=True)
                            if cr > 0.06: st.code(txt, language=detect_lang(txt))
                            else: st.markdown(f'<div class="pcard-b">{html.escape(txt)}</div>', unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
<div style="border-top:1px solid {T['b1']};padding:.85rem 1.2rem;background:{T['card']};flex-shrink:0;">
""", unsafe_allow_html=True)

        question = st.chat_input("Ask anything about the textbook…")

        st.markdown(f'<div style="font-size:.64rem;color:{T["t3"]};text-align:center;margin-top:.3rem">Enter to send</div>', unsafe_allow_html=True)
        st.markdown('</div></div></div>', unsafe_allow_html=True)

        if question:
            st.session_state.history.append({"role":"user","content":question})
            with st.spinner(""):
                from question_answering import answer_question
                results = st.session_state.retriever.retrieve(question, top_k=8)
                result  = answer_question(question, results, use_llm=True)
            st.session_state.cur_passages = results
            st.session_state.history.append({
                "role":"assistant","content":result["answer"],
                "source":result["source"],"model":result["model"],
                "llm_error":result.get("llm_error"),"passages":results,
            })
            st.rerun()

# ╔══════════════════════════════════════════════════════════╗
# ║  VIEW 3: SOURCES & PDF  (FIX 6)                          ║
# ║  FIX: Removed fixed-position outer container.            ║
# ║  Content now flows directly in stMainBlockContainer.     ║
# ║  PDF iframe uses full column width and tall height.      ║
# ╚══════════════════════════════════════════════════════════╝
elif v == "sources":
    if not st.session_state.indexed:
        st.warning("Upload and index a PDF first.")
        if st.button("← Go to Upload"): go("upload")
    else:
        passages = (
            st.session_state.history[-1].get("passages",[])
            if st.session_state.history and st.session_state.history[-1]["role"]=="assistant"
            else st.session_state.cur_passages
        )
        fname  = st.session_state.last_file or "document.pdf"
        n_pages = st.session_state.pages

        # Sources page: PDF viewer takes full width, passages shown below
        st.markdown(f"""
<div style="background:{T['card']};border:1px solid {T['b1']};border-radius:16px;
  overflow:hidden;box-shadow:{T['shd']};">
  <div class="src-head">
    <span style="font-size:1rem">📄</span>
    <span class="src-htitle">PDF Viewer · {n_pages} pages</span>
    <span style="margin-left:auto;font-size:.63rem;color:{T['t3']};
      font-family:'JetBrains Mono',monospace">{fname}</span>
  </div>
""", unsafe_allow_html=True)

        if st.session_state.last_file_bytes:
            b64 = base64.b64encode(st.session_state.last_file_bytes).decode()
            st.markdown(f"""
<iframe
  src="data:application/pdf;base64,{b64}#toolbar=1&navpanes=0&scrollbar=1&view=FitH"
  width="100%"
  height="720"
  style="display:block;border:none;width:100%;"
></iframe>
""", unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:center;'
                f'padding:4rem;flex-direction:column;gap:.5rem;opacity:.4">'
                f'<div style="font-size:2.5rem">📄</div>'
                f'<div style="font-size:.82rem;color:{T["t3"]}">PDF not available</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)