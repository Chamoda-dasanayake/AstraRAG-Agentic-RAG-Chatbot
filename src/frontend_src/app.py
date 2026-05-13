import sys, os, time
import streamlit as st
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.frontend_src.config.frontend_settings import Settings
settings = Settings()

st.set_page_config(page_title="AstraRAG Document Intelligence", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
:root{
  --bg:#0a0e1a;--bg2:#111827;--card:#1a1f35;--brd:#1e2740;--brd2:#2d3555;
  --t1:#f1f5f9;--t2:#94a3b8;--t3:#64748b;
  --blue:#6366f1;--purple:#a855f7;--cyan:#22d3ee;--green:#34d399;
  --grad:linear-gradient(135deg,#6366f1 0%,#a855f7 50%,#ec4899 100%);
}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg)!important;color:var(--t1)}
.stApp{background:var(--bg)!important}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--brd2);border-radius:3px}

/* Sidebar */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1221,#111827)!important;border-right:1px solid var(--brd)!important}
section[data-testid="stSidebar"] .stMarkdown h3{font-size:.78rem!important;letter-spacing:.1em;text-transform:uppercase;color:var(--t3)!important;font-weight:600}

/* Brand */
.brand-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(99,102,241,.12);border:1px solid rgba(99,102,241,.25);border-radius:20px;padding:4px 14px;font-size:.7rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#818cf8;margin-bottom:10px}
.brand-title{font-size:2.2rem;font-weight:800;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.15;margin:0 0 6px;letter-spacing:-.02em}
.brand-sub{color:var(--t2);font-size:.95rem;margin:0 0 1.5rem}

/* Stat cards */
.stat-row{display:flex;gap:10px;margin-bottom:1rem}
.stat-card{flex:1;background:var(--card);border:1px solid var(--brd);border-radius:8px;padding:12px;text-align:center}
.stat-val{font-size:1.3rem;font-weight:700;color:var(--t1)}
.stat-lbl{font-size:.63rem;color:var(--t3);text-transform:uppercase;letter-spacing:.08em;margin-top:3px}

/* Doc items */
.doc-item{display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--card);border:1px solid var(--brd);border-radius:8px;margin-bottom:6px;transition:.2s}
.doc-item:hover{border-color:var(--blue);background:rgba(99,102,241,.06)}
.doc-icon{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,rgba(99,102,241,.15),rgba(168,85,247,.15));display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.doc-name{font-size:.8rem;font-weight:500;color:var(--t1);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* Chat messages */
[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--brd)!important;border-radius:16px!important;padding:1.2rem 1.4rem!important;margin-bottom:.7rem!important;animation:slideUp .35s cubic-bezier(.16,1,.3,1) forwards;box-shadow:0 2px 12px rgba(0,0,0,.15)}
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]){border-left:3px solid var(--blue)!important;background:linear-gradient(135deg,rgba(99,102,241,.05),var(--card))!important}
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]){border-left:3px solid var(--purple)!important}
div[data-testid="chatAvatarIcon-user"]{background:linear-gradient(135deg,#6366f1,#3b82f6)!important;border-radius:10px!important}
div[data-testid="chatAvatarIcon-assistant"]{background:linear-gradient(135deg,#a855f7,#ec4899)!important;border-radius:10px!important}
@keyframes slideUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}

/* Source chips */
.src-chip{display:inline-flex;align-items:center;gap:4px;background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.2);color:var(--cyan);border-radius:20px;padding:3px 11px;font-size:.73rem;font-weight:500;margin:2px 4px 2px 0;font-family:'JetBrains Mono',monospace}

/* Confidence badge */
.conf-badge{display:inline-flex;align-items:center;gap:5px;border-radius:20px;padding:4px 12px;font-size:.7rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin-bottom:10px}
.conf-high{background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.25);color:#34d399}
.conf-medium{background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.25);color:#fbbf24}
.conf-low{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.25);color:#ef4444}

/* Follow-up suggestion chips */
.followup-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.followup-chip{background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2);color:#818cf8;border-radius:20px;padding:6px 14px;font-size:.76rem;font-weight:500;cursor:pointer;transition:.25s cubic-bezier(.16,1,.3,1)}
.followup-chip:hover{background:rgba(99,102,241,.18);border-color:rgba(99,102,241,.4);transform:translateY(-1px)}

/* Insight panel */
.ins-panel{background:rgba(99,102,241,.04);border:1px solid var(--brd);border-radius:10px;padding:14px 16px;margin-top:8px}
.ins-lbl{font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--t3);margin-bottom:5px}
.ins-val{font-size:.83rem;color:var(--t2);line-height:1.6}

/* Buttons */
.stButton>button{background:var(--grad)!important;color:#fff!important;border:none!important;border-radius:8px!important;padding:.55rem 1.2rem!important;font-weight:600!important;font-size:.83rem!important;transition:.25s cubic-bezier(.16,1,.3,1)!important;box-shadow:0 4px 15px rgba(99,102,241,.25)!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 0 40px rgba(99,102,241,.15),0 0 80px rgba(168,85,247,.05)!important}

/* File uploader */
[data-testid="stFileUploader"]{background:var(--card)!important;border:2px dashed var(--brd2)!important;border-radius:12px!important;padding:1rem!important;transition:.3s}
[data-testid="stFileUploader"]:hover{border-color:var(--blue)!important}

/* Chat input */
[data-testid="stChatInput"]{background:var(--bg2)!important;border-radius:16px!important;border:1px solid var(--brd2)!important}
[data-testid="stChatInput"] textarea{background:transparent!important;color:var(--t1)!important;font-family:'Inter',sans-serif!important}

/* Status dot */
.status-on{display:inline-flex;align-items:center;gap:6px;font-size:.7rem;color:var(--green);font-weight:500}
.s-dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(52,211,153,.4)}50%{opacity:.7;box-shadow:0 0 0 6px rgba(52,211,153,0)}}

/* Welcome */
.welcome{background:linear-gradient(145deg,rgba(99,102,241,.08),rgba(168,85,247,.04));border:1px solid var(--brd);border-radius:16px;padding:2.5rem;text-align:center;margin:2rem auto;max-width:580px}
.w-icon{font-size:3rem;margin-bottom:1rem;display:block}
.w-title{font-size:1.25rem;font-weight:700;color:var(--t1);margin-bottom:.5rem}
.w-text{font-size:.88rem;color:var(--t2);line-height:1.7;max-width:420px;margin:0 auto 1.2rem}
.feat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:1rem}
.feat-item{background:var(--card);border:1px solid var(--brd);border-radius:8px;padding:14px 10px;text-align:center;transition:.2s}
.feat-item:hover{border-color:var(--blue);transform:translateY(-2px)}
.feat-ico{font-size:1.3rem;margin-bottom:5px;display:block}
.feat-lbl{font-size:.7rem;color:var(--t2);font-weight:500}

.upload-ok{display:flex;align-items:center;gap:8px;background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2);border-radius:8px;padding:10px 16px;font-size:.8rem;color:var(--green);font-weight:500;animation:slideUp .3s ease}

hr{border:none;border-top:1px solid var(--brd);margin:1rem 0}
#MainMenu,footer{visibility:hidden}
.stAlert{border-radius:8px!important;font-size:.83rem!important}

/* ─── Mobile / responsive ─── */
@media (max-width:768px){
  html{-webkit-text-size-adjust:100%}
  .brand-title{font-size:1.65rem!important;line-height:1.2!important}
  .brand-sub{font-size:.875rem!important;margin-bottom:1rem!important}
  .brand-badge{font-size:.62rem!important;padding:3px 10px!important}
  .welcome{padding:1.25rem 1rem!important;margin:1rem .25rem!important;max-width:100%!important}
  .w-icon{font-size:2.25rem!important}
  .w-title{font-size:1.08rem!important}
  .w-text{font-size:.82rem!important}
  .feat-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
  .feat-item{padding:12px 8px!important}
  .feat-ico{font-size:1.15rem!important}
  .feat-lbl{font-size:.65rem!important}
  .stat-row{flex-wrap:wrap;gap:8px}
  .stat-card{min-width:calc(50% - 6px);padding:10px 8px!important}
  .stat-val{font-size:1.1rem!important}
  .doc-item{padding:9px 12px!important}
  .doc-name{white-space:normal!important;word-break:break-word!important;font-size:.78rem!important}
  [data-testid="stChatMessage"]{padding:.85rem 1rem!important;margin-bottom:.55rem!important;border-radius:14px!important}
  [data-testid="stChatInput"] textarea{font-size:16px!important}
  .stButton>button{min-height:44px!important;padding:.65rem 1rem!important;font-size:.82rem!important}
  section[data-testid="stSidebar"]{width:min(100vw - 8px,320px)!important}
}
@media (max-width:480px){
  .brand-title{font-size:1.38rem!important}
  .welcome{padding:1rem .75rem!important}
  .feat-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .stat-card{flex:1 1 100%;min-width:100%}
  .src-chip{font-size:.68rem!important;padding:4px 9px!important;word-break:break-word;white-space:normal}
  .conf-badge{font-size:.63rem!important;padding:5px 10px!important}
}
@media (max-width:768px){
  .main .block-container{padding-left:max(.75rem, env(safe-area-inset-left))!important;padding-right:max(.75rem, env(safe-area-inset-right))!important;padding-top:.75rem!important;max-width:100%!important}
}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
        <div style="text-align:center;padding:.5rem 0 1.2rem">
            <div style="font-size:2rem;margin-bottom:4px">🔮</div>
            <div style="font-size:1.1rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent">AstraRAG</div>
            <div style="font-size:.66rem;color:#64748b;margin-top:2px">Agentic Document Intelligence</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 📤 Upload Document")
    uploaded_file = st.file_uploader("Drag & drop PDF", type=["pdf"], label_visibility="collapsed", help="Upload a PDF to index")

    if uploaded_file is not None:
        sz = len(uploaded_file.getvalue()) / 1024
        sz_str = f"{sz:.0f} KB" if sz < 1024 else f"{sz/1024:.1f} MB"
        st.markdown(f'<div class="doc-item"><div class="doc-icon">📄</div><div><div class="doc-name">{uploaded_file.name}</div><div style="font-size:.68rem;color:#64748b">{sz_str}</div></div></div>', unsafe_allow_html=True)

        if st.button("⚡ Process & Index", use_container_width=True, key="upload_btn"):
            with st.spinner("Analyzing document structure..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    resp = requests.post(f"{settings.API_BASE_URL}/documents/upload", files=files, timeout=120)
                    if resp.status_code == 200:
                        d = resp.json()
                        st.markdown(f'<div class="upload-ok">✅ Indexed — {d.get("node_count","N/A")} chunks, {d.get("text_length",0):,} chars</div>', unsafe_allow_html=True)
                        time.sleep(1); st.rerun()
                    else:
                        st.error(f"❌ {resp.json().get('detail','Unknown error')}")
                except requests.ConnectionError:
                    st.error("⚠️ Backend offline — start the API server first.")
                except Exception as e:
                    st.error(f"⚠️ {e}")

    st.markdown("---")
    st.markdown("### 📚 Knowledge Base")

    docs, api_on = [], False
    try:
        r = requests.get(f"{settings.API_BASE_URL}/documents/list", timeout=5)
        if r.status_code == 200:
            docs = r.json().get("documents", []); api_on = True
    except: pass

    if api_on:
        st.markdown('<div class="status-on"><div class="s-dot"></div>System Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="display:inline-flex;align-items:center;gap:6px;font-size:.7rem;color:#ef4444;font-weight:500"><div style="width:7px;height:7px;border-radius:50%;background:#ef4444"></div>Backend Offline</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="stat-row"><div class="stat-card"><div class="stat-val">{len(docs)}</div><div class="stat-lbl">Documents</div></div><div class="stat-card"><div class="stat-val">4</div><div class="stat-lbl">AI Agents</div></div></div>', unsafe_allow_html=True)

    if docs:
        for doc_idx, doc in enumerate(docs):
            dn = doc if len(doc) <= 30 else doc[:27] + "..."
            left_col, right_col = st.columns([0.8, 0.2])
            with left_col:
                st.markdown(
                    f'<div class="doc-item"><div class="doc-icon">📄</div><div class="doc-name" title="{doc}">{dn}</div></div>',
                    unsafe_allow_html=True
                )
            with right_col:
                if st.button("🗑️", key=f"delete_doc_{doc_idx}", help=f"Remove {doc}"):
                    try:
                        del_resp = requests.delete(
                            f"{settings.API_BASE_URL}/documents/delete",
                            params={"document_name": doc},
                            timeout=30
                        )
                        if del_resp.status_code == 200:
                            st.success(f"Removed: {dn}")
                            time.sleep(0.6)
                            st.rerun()
                        else:
                            msg = "Delete failed"
                            try:
                                msg = del_resp.json().get("detail", msg)
                            except Exception:
                                pass
                            st.error(f"❌ {msg}")
                    except requests.ConnectionError:
                        st.error("⚠️ Backend offline — start the API server first.")
                    except Exception as e:
                        st.error(f"⚠️ {e}")
    else:
        st.caption("No documents indexed yet.")

    if st.button("🔄 Refresh", use_container_width=True, key="refresh_btn"):
        st.rerun()

    st.markdown("---")
    st.markdown('<div style="text-align:center;padding:.5rem 0"><div style="font-size:.63rem;color:#475569;line-height:1.6">Powered by <strong style="color:#818cf8">CrewAI</strong> · <strong style="color:#818cf8">ChromaDB</strong> · <strong style="color:#818cf8">OpenAI</strong><br>Multi-Agent RAG Pipeline v3.0 · 4 Agents</div></div>', unsafe_allow_html=True)

st.markdown("""
<div style="padding:1.2rem 0 .6rem">
    <div class="brand-badge">🔮 Multi-Agent RAG System</div>
    <h1 class="brand-title">AstraRAG Assistant</h1>
    <p class="brand-sub">Upload documents. Ask questions. Get fact-checked, source-grounded answers.</p>
</div>""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_followup_prompt" not in st.session_state:
    st.session_state.selected_followup_prompt = None

_, cc = st.columns([.88, .12])
with cc:
    if st.button("🗑️ Clear", key="clear_btn", help="Clear chat history"):
        st.session_state.chat_history = []; st.rerun()

if not st.session_state.chat_history:
    st.markdown("""
    <div class="welcome">
        <span class="w-icon">🔮</span>
        <div class="w-title">Welcome to AstraRAG</div>
        <p class="w-text">AI-powered document assistant with a 4-agent pipeline — retrieval, summarization, fact-checking, and conversational formatting. Upload a PDF and start asking questions.</p>
        <div class="feat-grid">
            <div class="feat-item"><span class="feat-ico">📄</span><div class="feat-lbl">PDF Analysis</div></div>
            <div class="feat-item"><span class="feat-ico">🤖</span><div class="feat-lbl">4 AI Agents</div></div>
            <div class="feat-item"><span class="feat-ico">✅</span><div class="feat-lbl">Fact-Checked</div></div>
            <div class="feat-item"><span class="feat-ico">💬</span><div class="feat-lbl">Smart Format</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

for msg_idx, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("role") == "assistant":
            conf = msg.get("confidence_level", "N/A")
            if conf and conf != "N/A":
                conf_class = {"High": "conf-high", "Medium": "conf-medium", "Low": "conf-low"}.get(conf, "conf-medium")
                conf_icon = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(conf, "⚪")
                st.markdown(f'<div class="conf-badge {conf_class}">{conf_icon} Confidence: {conf}</div>', unsafe_allow_html=True)

            srcs = msg.get("sources", [])
            tool = msg.get("tool_used")
            rat = msg.get("rationale")
            if srcs and srcs != ["No sources provided"] and srcs != []:
                chips = "".join(f'<span class="src-chip">📎 {s}</span>' for s in srcs)
                st.markdown(f'<div style="margin-top:10px"><div style="font-size:.68rem;color:#64748b;font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:5px">Sources Referenced</div>{chips}</div>', unsafe_allow_html=True)

            suggestions = msg.get("follow_up_suggestions", [])
            if suggestions:
                st.markdown(
                    '<div style="margin-top:10px;font-size:.68rem;color:#64748b;font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:5px">Try Asking</div>',
                    unsafe_allow_html=True
                )
                for s_idx, suggestion in enumerate(suggestions):
                    if st.button(
                        f"💡 {suggestion}",
                        key=f"followup_{msg_idx}_{s_idx}",
                        use_container_width=True
                    ):
                        st.session_state.selected_followup_prompt = suggestion
                        st.rerun()

            if rat and rat != "N/A":
                with st.expander("🔍 Auditor Insights & Reasoning"):
                    if tool and tool != "N/A":
                        st.markdown(f'<div class="ins-panel"><div class="ins-lbl">Agent Pipeline</div><div class="ins-val">{tool}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="ins-panel"><div class="ins-lbl">Fact-Check Rationale</div><div class="ins-val">{rat}</div></div>', unsafe_allow_html=True)

prompt_from_input = st.chat_input("Ask a question about your documents...")
prompt = st.session_state.selected_followup_prompt or prompt_from_input
if prompt:
    if st.session_state.selected_followup_prompt:
        st.session_state.selected_followup_prompt = None
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🔮 4 Agents analyzing your query..."):
            try:
                resp = requests.post(settings.CHAT_ENDPOINT_URL, json={"chat_history": st.session_state.chat_history}, timeout=180)
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("answer", data.get("formatted_answer", data.get("summary", "(No response)")))
                tool_used = data.get("tool_used", "N/A")
                rationale = data.get("rationale", "N/A")
                sources = data.get("sources", data.get("original_sources", []))
                follow_up_suggestions = data.get("follow_up_suggestions", [])
                confidence_level = data.get("confidence_level", "N/A")
            except requests.ConnectionError:
                answer = "⚠️ **Backend Offline** — Start the API server with `python -m src.backend_src.main`"
                tool_used, rationale, sources = "N/A", "N/A", []
                follow_up_suggestions, confidence_level = [], "N/A"
            except requests.HTTPError as e:
                answer = "⏳ **Rate Limited** — Please wait and retry." if e.response.status_code == 429 else f"❌ **Error {e.response.status_code}**"
                tool_used, rationale, sources = "N/A", "N/A", []
                follow_up_suggestions, confidence_level = [], "N/A"
            except Exception as e:
                answer = f"⚠️ **Error** — {e}"
                tool_used, rationale, sources = "N/A", "N/A", []
                follow_up_suggestions, confidence_level = [], "N/A"
        st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer, "tool_used": tool_used, "rationale": rationale, "sources": sources, "follow_up_suggestions": follow_up_suggestions, "confidence_level": confidence_level})
    st.rerun()
