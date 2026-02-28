import streamlit as st
import requests
import datetime
import os
import glob
import time
import sys
import shutil 
from dotenv import load_dotenv

# --- PAGE CONFIG MUST BE FIRST ---
st.set_page_config(page_title="Lab AgentX | Enterprise AI Orchestrator", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# --- FOLDER PATHS SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'Agents')
sys.path.append(agents_dir)
for dept in ['Marketing', 'Tech', 'Video', 'Oracle', 'SEO', 'Legal', 'Finance', 'OmniReader', 'Multiplier', 'Sales', 'sales', 'ImageGen', 'DeepResearch']:
    sys.path.append(os.path.join(agents_dir, dept))

# Load API Keys
load_dotenv()
INITIAL_GROQ_KEY = os.getenv("GROQ_API_KEY", "")

# --- ERROR 2 FIXED: VARIABLES DEFINED ---
MEMORY_FOLDER = "memory_logs"
UPLOAD_FOLDER = "uploads"
DELIVERABLES_FOLDER = "Deliverables"
SAVED_FILES_FOLDER = "Saved_Files" 

for folder in [MEMORY_FOLDER, UPLOAD_FOLDER, DELIVERABLES_FOLDER, SAVED_FILES_FOLDER]:
    if not os.path.exists(folder): 
        os.makedirs(folder)

# --- ERROR 1 FIXED: PERFECT INDENTATION ---
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# --- PDF GENERATOR ENGINE ---
def generate_pdf_bytes(text_content):
    if not HAS_FPDF: return None
    temp_pdf_path = f"uploads/temp_dl_{int(time.time())}.pdf"
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        safe_text = str(text_content).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=safe_text)
        pdf.output(temp_pdf_path)
        with open(temp_pdf_path, "rb") as pdf_file: pdf_bytes = pdf_file.read()
        if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)
        return pdf_bytes
    except:
        if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)
        return None

# --- STATE MANAGEMENT ---
if "current_page" not in st.session_state: st.session_state.current_page = "dashboard"
if "squad_chat" not in st.session_state:
    st.session_state.squad_chat = [
        {"agent": "System", "msg": "Enterprise Engine Initialized. Select a workflow or input a command.", "time": datetime.datetime.now().strftime("%H:%M")}
    ]
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Lab AgentX Enterprise Orchestrator online. What business process would you like to automate today?"}]
if "active_tasks" not in st.session_state: st.session_state.active_tasks = []
if "tokens_used" not in st.session_state: st.session_state.tokens_used = 124500

# Execution Logs Dialog
@st.dialog("📊 Workflow Execution Logs")
def show_squad_chat():
    st.markdown("<p style='color:#94a3b8; font-size:14px; margin-bottom:15px;'>Live monitoring of multi-agent collaboration and system verification.</p>", unsafe_allow_html=True)
    chat_html = "<div style='max-height: 350px; overflow-y: auto; padding-right: 10px;'>"
    for chat in st.session_state.squad_chat:
        agent_color = "#10b981" if chat['agent'] == "System" else "#38bdf8"
        chat_html += f"""
        <div style='background: #0f172a; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {agent_color};'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                <span style='color: {agent_color}; font-weight: 700; font-size: 12px; text-transform: uppercase;'>{chat['agent']}</span>
                <span style='color: #64748b; font-size: 10px; font-weight: 600;'>{chat['time']}</span>
            </div>
            <div style='color: #e2e8f0; font-size: 13px; line-height: 1.5;'>{chat['msg']}</div>
        </div>
        """
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

# ==========================================
# 🧪 MAIN DASHBOARD (ENTERPRISE MISSION CONTROL)
# ==========================================
if st.session_state.current_page == "dashboard":

    # 🔥 SAFE CSS - NO HACKS TO BREAK THE UI 🔥
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        .stApp, .stAppViewContainer { background-color: #020617 !important; font-family: 'Plus Jakarta Sans', sans-serif; color: #f8fafc; }
        
        section[data-testid="stSidebar"] { display: block !important; background-color: #0f172a !important; border-right: 1px solid #1e293b !important; }
        .block-container { padding-top: 2rem !important; max-width: 1400px !important; }
        .stMarkdown, .stText, p, span, h1, h2, h3, h4, h5, h6, label { color: #f8fafc !important; }
        
        /* Stats */
        .top-stats { display: flex; justify-content: space-between; background: #0f172a; padding: 15px 20px; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 20px; gap: 15px; }
        .stat-box { flex: 1; border-right: 1px solid #1e293b; padding-right: 15px; }
        .stat-box:last-child { border-right: none; padding-right: 0; }
        .stat-value { font-size: 22px; font-weight: 700; color: #f8fafc !important; } 
        .stat-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8 !important; margin-top: 2px;}
        
        /* Workflow Cards */
        .workflow-card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 4px solid #38bdf8;}
        .w-title { font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;}
        .w-desc { font-size: 11px; color: #94a3b8; line-height: 1.4;}
        
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    def get_done_tasks():
        tasks = []
        for root, _, filenames in os.walk(DELIVERABLES_FOLDER):
            for fname in filenames:
                fpath = os.path.join(root, fname)
                try:
                    file_mtime = os.path.getmtime(fpath)
                    if file_mtime >= st.session_state.session_start_time:
                        tasks.append({"name": fname.replace(".md", "").replace(".txt", "").replace(".jpg", "").replace("_", " "), "path": fpath, "time": file_mtime})
                except: pass
        return sorted(tasks, key=lambda x: x['time'], reverse=True)[:50]

    st.markdown(f"""
    <div class="top-stats">
        <div class="stat-box"><div class="stat-value">{len(st.session_state.active_tasks)}</div><div class="stat-label">Active Workflows</div></div>
        <div class="stat-box"><div class="stat-value" style="color:#f59e0b !important;">BYOK Engine</div><div class="stat-label">Architecture</div></div>
        <div class="stat-box"><div class="stat-value">{format(st.session_state.tokens_used, ',')}</div><div class="stat-label">Tokens Audited</div></div>
        <div class="stat-box"><div class="stat-value" style="color:#10b981 !important;">100% SLA</div><div class="stat-label">System Health</div></div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<h3 style='color: #f8fafc; font-size: 16px; margin-bottom: 15px;'>🏢 Mission Control</h3>", unsafe_allow_html=True)
        
        if st.button("📊 Execution Logs", use_container_width=True): show_squad_chat()
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.messages = [{"role": "assistant", "content": "Session reset. Ready for new workflows."}]
                st.rerun()
        with col_c2:
            if st.button("🛑 Halt", use_container_width=True):
                st.session_state.active_tasks = []; st.session_state.messages.append({"role": "assistant", "content": "🛑 Execution Halted."})
                st.rerun()
        
        # 🔥 THE SAFE ATTACHMENT UPLOADER 🔥
        st.markdown("---")
        with st.expander("📎 Attach Documents", expanded=False):
            st.caption("Provide context files (PDF, TXT) here:")
            uploaded_files = st.file_uploader("Upload Files", type=["pdf", "png", "txt", "csv"], accept_multiple_files=True, label_visibility="collapsed")
            if uploaded_files: st.success(f"✅ {len(uploaded_files)} file(s) ready.")
                
        st.markdown("---")
        st.markdown("<h3 style='color: #f8fafc; font-size: 14px; margin-bottom: 10px;'>⚡ Available Workflows</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='workflow-card' style='border-color: #f59e0b;'><div class='w-title'>Competitor Takedown</div><div class='w-desc'>Deep scans URLs and generates business attack plans.</div></div>
        <div class='workflow-card' style='border-color: #8b5cf6;'><div class='w-title'>Closed-Loop Tech</div><div class='w-desc'>Generates Python/Web code and audits it internally.</div></div>
        <div class='workflow-card' style='border-color: #ef4444;'><div class='w-title'>Autonomous Sales (Live Email)</div><div class='w-desc'>Finds leads and ACTUALLY SENDS cold emails via Gmail.</div></div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        # BYOK SELECTION
        with st.expander("🔑 BYOK (Bring Your Own Key)", expanded=True):
            st.markdown("<p style='font-size: 11px; color: #94a3b8;'>Enterprise 100% Margin Model.</p>", unsafe_allow_html=True)
            selected_brain = st.selectbox("🧠 Select Engine", ["Groq (Llama 3.3 - Fastest)", "OpenAI (GPT-4o - Deepest)"])
            st.session_state.selected_brain = selected_brain
            if "Groq" in selected_brain: live_api_key = st.text_input("Groq API Key", type="password", value=INITIAL_GROQ_KEY)
            else: live_api_key = st.text_input("OpenAI API Key", type="password")
            st.session_state.live_api_key = live_api_key

    # Initialize Engine
    chat_brain = None
    if st.session_state.get("live_api_key"):
        live_key = st.session_state.live_api_key
        os.environ["OPENAI_API_KEY"] = live_key
        try:
            if "Groq" in st.session_state.selected_brain:
                os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
                os.environ["GROQ_API_KEY"] = live_key
                from langchain_openai import ChatOpenAI
                chat_brain = ChatOpenAI(model="llama-3.3-70b-versatile", base_url="https://api.groq.com/openai/v1", api_key=live_key)
            elif "OpenAI" in st.session_state.selected_brain:
                os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
                from langchain_openai import ChatOpenAI
                chat_brain = ChatOpenAI(model="gpt-4o", api_key=live_key)
        except: pass

    col_main, col_files = st.columns([2.5, 1])
    
    with col_main:
        with st.container(height=550, border=False):
            for message in st.session_state.messages:
                with st.chat_message(message["role"], avatar="🏢" if message["role"] == "assistant" else "🧑‍💼"): st.markdown(message["content"])

    with col_files:
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #f8fafc; margin-bottom: 10px; border-bottom: 1px solid #334155; padding-bottom: 5px;'>📂 Deliverables</div>", unsafe_allow_html=True)
        done_tasks_list = get_done_tasks()
        if done_tasks_list:
            for task in done_tasks_list:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size: 12px; font-weight: 600; color: #f8fafc;'>{task['name'][:20]}...</div>", unsafe_allow_html=True)
                    if task['path'].endswith('.jpg') or task['path'].endswith('.png'):
                        with open(task['path'], "rb") as f: st.download_button(label="Download Media", data=f, file_name=os.path.basename(task['path']), mime="image/jpeg", key=task['path']+"_img", use_container_width=True)
                    else:
                        with open(task['path'], "r", encoding="utf-8", errors="ignore") as f: 
                            file_content = f.read()
                        pdf_data = generate_pdf_bytes(file_content)
                        if pdf_data: st.download_button(label="Download Report (PDF)", data=pdf_data, file_name=task['name']+".pdf", mime="application/pdf", key=task['path']+"_pdf", use_container_width=True)
                        else: st.download_button(label="Download Raw", data=file_content.encode('utf-8'), file_name=task['name']+".txt", mime="text/plain", key=task['path']+"_txt", use_container_width=True)
        else:
            st.caption("No deliverables generated yet.")

    st.markdown("---")
    
    # 🔥 SAFE CHAT INPUT - NATIVE STREAMLIT 🔥
    user_input = st.chat_input("Enter outcome requirement (e.g., 'Email investor@example.com about my AI tool')...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.active_tasks.append(user_input[:30] + "...") 
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]
        msg_content = last_msg["content"]
        
        # 🔥 PURE ENGLISH ENTERPRISE ROUTER PROMPT 🔥
        system_prompt = """You are the Lab AgentX Enterprise Orchestrator. 
        CRITICAL: ALWAYS RESPOND IN 100% PROFESSIONAL ENGLISH. NO OTHER LANGUAGES.

        RULES:
        1. For greetings: Reply professionally. No workflow triggers.
        2. If user provides a URL or asks for competitor analysis:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Ian** (Web Intelligence Module).
        3. If user asks for code, programming, or software development:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Finn** (Closed-Loop Tech Module).
        4. If user asks to SEND AN EMAIL, find leads, or do sales outreach:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Luke** (Autonomous Sales & Email Module).
        5. If user asks to create an image:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Sean** (Image Generation Module).
        6. General research without URLs:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Leo** (Deep Research Module).
        """
        
        if not chat_brain:
            st.session_state.messages.append({"role": "assistant", "content": "⚠️ Enterprise Engine Offline. Please configure BYOK API Key."})
            if st.session_state.active_tasks: st.session_state.active_tasks.pop()
            st.rerun()
        else:
            try:
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
                api_messages = [SystemMessage(content=system_prompt)]
                for m in (st.session_state.full_memory + st.session_state.messages)[-8:]:
                    if m["role"] == "user": api_messages.append(HumanMessage(content=m["content"][:800]))
                    elif m["role"] == "assistant": api_messages.append(AIMessage(content=m["content"][:800]))

                response = chat_brain.invoke(api_messages)
                full_response = response.content
                st.session_state.tokens_used += len(full_response) * 3 
                
                try:
                    if "Initiating:" in full_response:
                        st.session_state.squad_chat.append({"agent": "System Orchestrator", "msg": f"Routing user intent to appropriate backend module.", "time": datetime.datetime.now().strftime("%H:%M")})
                except: pass
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                if "[WORKFLOW TRIGGERED]" in full_response:
                    st.toast("⚡ Enterprise Module Engaged...", icon="🚀")
                    
                    with st.spinner(f"Executing Multi-Agent Workflow... Please wait."):
                        agent_result = "⚠️ Module integrated but running in safe mode."
                        
                        try:
                            if "**Gabe**" in full_response: from marketing import run_marketing_crew; agent_result = run_marketing_crew(msg_content)
                            elif "**Sean**" in full_response: from sai_illustrator import run_image_generation; agent_result = run_image_generation(msg_content)
                            elif "**Ian**" in full_response: from oracle_intel import run_oracle_crew; agent_result = run_oracle_crew(msg_content)
                            elif "**Finn**" in full_response: from tech import run_tech_crew; agent_result = run_tech_crew(msg_content)
                            elif "**Leo**" in full_response: from kimi_research import run_kimi_squad; agent_result = run_kimi_squad(msg_content)
                            elif "**Luke**" in full_response: 
                                # Route to Sales Email Agent
                                from sales_dept import run_sales_crew
                                agent_result = run_sales_crew(msg_content)
                        except Exception as module_err:
                            agent_result = f"Module Execution Error: {str(module_err)}"
                        
                        if len(st.session_state.active_tasks) > 0:
                            st.toast("✅ Workflow Executed Successfully!", icon="🏢")
                            st.session_state.messages.append({"role": "assistant", "content": f"### 🏢 EXECUTION REPORT\n\n{agent_result}"})
                            
            except Exception as e: st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Execution Error: {str(e)}"})
        
        if len(st.session_state.active_tasks) > 0: st.session_state.active_tasks.pop()
        st.rerun()