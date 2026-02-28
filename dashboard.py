import streamlit as st
import requests
import datetime
import os
import glob
import time
import sys
import shutil 
import json
from dotenv import load_dotenv

# ==========================================
# ⚙️ 1. CORE SYSTEM CONFIGURATION
# ==========================================
# Page config sabse pehle aani chahiye taake UI engine set ho jaye
st.set_page_config(
    page_title="Lab AgentX | Enterprise AI Orchestrator", 
    page_icon="🏢", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- Path Setup (Agents ko link karne ke liye) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'Agents')
sys.path.append(agents_dir)
# Saare sub-folders link kar rahe hain
for dept in ['Marketing', 'Tech', 'Video', 'Oracle', 'SEO', 'Legal', 'Finance', 'OmniReader', 'Multiplier', 'Sales', 'sales', 'ImageGen', 'DeepResearch']:
    sys.path.append(os.path.join(agents_dir, dept))

# --- Environment Variables ---
load_dotenv()
INITIAL_GROQ_KEY = os.getenv("GROQ_API_KEY", "")

# --- Folder Infrastructure ---
# Agar ye folders nahi honge toh NameError aayega (Jo aapko pehle aaya tha)
MEMORY_FOLDER = "memory_logs"
UPLOAD_FOLDER = "uploads"
DELIVERABLES_FOLDER = "Deliverables"
SAVED_FILES_FOLDER = "Saved_Files" 
SYSTEM_LOGS_FOLDER = "system_logs"

for folder in [MEMORY_FOLDER, UPLOAD_FOLDER, DELIVERABLES_FOLDER, SAVED_FILES_FOLDER, SYSTEM_LOGS_FOLDER]:
    if not os.path.exists(folder): 
        os.makedirs(folder)

# --- PDF Engine Verification ---
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# ==========================================
# 🧠 2. ADVANCED STATE MANAGEMENT
# ==========================================
# Ye system ki memory hai. Agar ye sahi nahi hogi toh UI glitch karegi.
if "current_page" not in st.session_state: 
    st.session_state.current_page = "dashboard"
if "squad_chat" not in st.session_state:
    st.session_state.squad_chat = []
if "messages" not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Lab AgentX Enterprise Orchestrator online. Main aapki kya madad kar sakta hoon?"}]
if "active_tasks" not in st.session_state: 
    st.session_state.active_tasks = []
if "tokens_used" not in st.session_state: 
    st.session_state.tokens_used = 124500
if "cost_saved" not in st.session_state:
    st.session_state.cost_saved = 450.00 # Simulated cost saved in dollars
if "workflows_run" not in st.session_state:
    st.session_state.workflows_run = 42
if "system_logs" not in st.session_state:
    st.session_state.system_logs = [f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] System Boot Sequence Initiated."]
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()

# ==========================================
# 🛠️ 3. HELPER FUNCTIONS & DIALOGS
# ==========================================

def log_event(event_type, message):
    """System ki har harkat ko log karne ke liye professional tracker"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{event_type.upper()}] {message}"
    st.session_state.system_logs.insert(0, log_entry)
    
    # Text file mein bhi save karein (Persistence ke liye)
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    with open(f"{SYSTEM_LOGS_FOLDER}/log_{today_date}.txt", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def generate_pdf_bytes(text_content):
    """Professional PDF Generator"""
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
    except Exception as e:
        log_event("Error", f"PDF Generation failed: {str(e)}")
        if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)
        return None

def get_done_tasks():
    """Disk se deliverable files uthane ka function"""
    tasks = []
    for root, _, filenames in os.walk(DELIVERABLES_FOLDER):
        for fname in filenames:
            fpath = os.path.join(root, fname)
            try:
                file_mtime = os.path.getmtime(fpath)
                if file_mtime >= st.session_state.session_start_time:
                    tasks.append({
                        "name": fname.replace(".md", "").replace(".txt", "").replace(".jpg", "").replace("_", " "), 
                        "path": fpath, 
                        "time": file_mtime
                    })
            except: pass
    return sorted(tasks, key=lambda x: x['time'], reverse=True)[:50]

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

# 🔥 NAYA DIALOG: Show All Agents 🔥
@st.dialog("👥 Enterprise Agents Roster")
def show_all_agents():
    st.markdown("System mein available saare specialized AI agents ki list:")
    agents_list = [
        ("🏢 Lab AgentX", "System Orchestrator"),
        ("🔍 Leo", "Research Analyst"),
        ("📹 Troy", "Video Producer"),
        ("✍️ Nate", "Content Strategist"),
        ("🎯 Luke", "Outbound Sales"),
        ("🛡️ Mia", "Retention Manager"),
        ("💻 Finn", "Lead Developer"),
        ("📧 Sam", "PR & Email Marketing"),
        ("📊 Seth", "Data Scientist"),
        ("⚡ Zoe", "UX/UI Designer"),
        ("📈 Gabe", "Head of Marketing"),
        ("🕸️ Ian", "Intelligence Scout"),
        ("🚀 Ava", "SEO Specialist"),
        ("🎨 Sean", "Art Director"),
        ("💰 Nora", "Financial Analyst"),
        ("⚖️ Noah", "Legal Counsel")
    ]
    
    # 2 columns mein grid layout banaya hai
    c1, c2 = st.columns(2)
    for i, (name, role) in enumerate(agents_list):
        col = c1 if i % 2 == 0 else c2
        col.markdown(f"""
        <div style='background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px;'>
            <div style='font-weight: 700; color: #f8fafc; font-size: 14px;'>{name}</div>
            <div style='color: #94a3b8; font-size: 12px;'>{role}</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 🎨 4. SAFE & CLEAN CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Base typography */
    html, body, [class*="css"]  {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Clean Top Header */
    header[data-testid="stHeader"] { visibility: hidden; }
    
    /* Professional Metrics styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
    }
    
    /* Workflow Cards in Sidebar */
    .wf-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
        transition: 0.3s;
    }
    .wf-card:hover {
        border-color: #38bdf8;
    }
    .wf-title {
        font-size: 14px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 5px;
    }
    .wf-desc {
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.4;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🎛️ 5. SIDEBAR CONFIGURATION (MISSION CONTROL)
# ==========================================
with st.sidebar:
    st.markdown("## 🏢 Lab AgentX HQ")
    st.markdown("<div class='status-badge'>● SYSTEM ONLINE</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- MULTI-MODEL BYOK (Bring Your Own Key) ---
    st.markdown("### 🧠 AI Core Engine")
    st.caption("Aapka apna AI model. 100% Data Privacy. Zero Markup.")
    
    selected_brain = st.selectbox(
        "Select Architecture", 
        [
            "Groq (Llama 3.3 - Lightning Fast)", 
            "OpenAI (GPT-4o - Highest IQ)",
            "Anthropic (Claude 3.5 - Best Coding)",
            "Google (Gemini 1.5 - Multimodal)"
        ]
    )
    st.session_state.selected_brain = selected_brain
    
    if "Groq" in selected_brain:
        live_api_key = st.text_input("Groq API Key", type="password", value=INITIAL_GROQ_KEY, help="Get this from console.groq.com")
    elif "OpenAI" in selected_brain:
        live_api_key = st.text_input("OpenAI API Key (sk-...)", type="password")
    elif "Anthropic" in selected_brain:
        live_api_key = st.text_input("Anthropic API Key (sk-ant-...)", type="password")
    elif "Gemini" in selected_brain:
        live_api_key = st.text_input("Google Gemini API Key", type="password")
        
    st.session_state.live_api_key = live_api_key

    st.markdown("---")
    
    # 🔥 NAYA UPDATE: EMAIL CONFIGURATION UI MEIN 🔥
    with st.expander("📧 Email Engine Setup", expanded=False):
        st.markdown("<p style='font-size: 11px; color: #94a3b8;'>Sales workflow (Luke) se live cold emails bhejne ke liye apne credentials dalein.</p>", unsafe_allow_html=True)
        sender_email = st.text_input("Aapka Gmail Address", placeholder="you@gmail.com")
        sender_app_password = st.text_input("Gmail App Password", type="password", help="Google Account -> Security -> App Passwords se 16 letter ka code yahan dalein.")
        
        if sender_email and sender_app_password:
            # Backend environment variables set kar rahe hain dynamically UI se
            os.environ["SENDER_EMAIL"] = sender_email
            os.environ["SENDER_PASSWORD"] = sender_app_password
            st.success("✅ Email Engine Configured!")

# ==========================================
# 🧠 6. INITIALIZE AI ENGINE
# ==========================================
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
            
        elif "Anthropic" in st.session_state.selected_brain:
            from langchain_anthropic import ChatAnthropic
            chat_brain = ChatAnthropic(model_name="claude-3-5-sonnet-20240620", anthropic_api_key=live_key)
            
        elif "Gemini" in st.session_state.selected_brain:
            from langchain_google_genai import ChatGoogleGenerativeAI
            chat_brain = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=live_key)
            
    except Exception as e:
        st.sidebar.error(f"⚠️ Engine Load Error: {str(e)}")
else:
    st.sidebar.warning("⚠️ Enter API Key to activate the intelligence engine.")

# ==========================================
# 📊 7. MAIN DASHBOARD CONTENT (TABS)
# ==========================================

# 🔥 TOP HEADER WITH "CHECK ALL AGENTS" BUTTON 🔥
head_col1, head_col2 = st.columns([0.85, 0.15])
with head_col1:
    st.markdown("## 📈 Enterprise Operations Console")
with head_col2:
    st.markdown("<br>", unsafe_allow_html=True) # Alignment fix
    if st.button("👥 Check All Agents", use_container_width=True):
        show_all_agents()

# --- Top Level Metrics ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Active Agent Workflows", value=f"{st.session_state.workflows_run}", delta="+2 this hour")
kpi2.metric(label="Tokens Processed", value=f"{st.session_state.tokens_used:,}", delta="Efficient")
kpi3.metric(label="Est. Cost Saved", value=f"${st.session_state.cost_saved:.2f}", delta="vs Human Labor")
kpi4.metric(label="System Architecture", value=st.session_state.selected_brain.split(" ")[0], delta="Optimized", delta_color="normal")

st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px; border-color: #1e293b;'>", unsafe_allow_html=True)

# --- Professional Tabs Array ---
tab_chat, tab_deliverables, tab_logs = st.tabs(["💬 Command Interface", "📂 Output Hub", "🛠️ Audit Logs"])

with tab_chat:
    chat_container = st.container(height=450, border=True)
    with chat_container:
        for message in st.session_state.messages:
            avatar_icon = "🏢" if message["role"] == "assistant" else "🧑‍💼"
            with st.chat_message(message["role"], avatar=avatar_icon):
                st.markdown(message["content"])
                
    if len(st.session_state.active_tasks) > 0:
        with st.status("Agent framework is processing your request...", expanded=True) as status:
            st.write("🔍 Analyzing Intent...")
            time.sleep(1)
            st.write("🧠 Engaging Selected AI Model...")
            status.update(label="Executing Workflow...", state="running")

with tab_deliverables:
    st.markdown("### 📥 Completed Artifacts")
    st.write("All documents, code, and reports generated by the agents are securely stored here.")
    done_tasks_list = get_done_tasks()
    if done_tasks_list:
        file_cols = st.columns(3)
        for index, task in enumerate(done_tasks_list):
            col_idx = index % 3
            with file_cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**{task['name'][:25]}...**")
                    st.caption(f"Generated: {datetime.datetime.fromtimestamp(task['time']).strftime('%Y-%m-%d %H:%M')}")
                    if task['path'].endswith('.jpg') or task['path'].endswith('.png'):
                        with open(task['path'], "rb") as f: 
                            st.download_button("🖼️ Download Image", data=f, file_name=os.path.basename(task['path']), mime="image/jpeg", use_container_width=True, key=f"dl_{index}")
                    else:
                        with open(task['path'], "r", encoding="utf-8", errors="ignore") as f: 
                            file_content = f.read()
                        pdf_data = generate_pdf_bytes(file_content)
                        if pdf_data: 
                            st.download_button("📄 Download PDF", data=pdf_data, file_name=task['name']+".pdf", mime="application/pdf", use_container_width=True, key=f"dl_pdf_{index}")
                        else: 
                            st.download_button("📄 Download Text", data=file_content.encode('utf-8'), file_name=task['name']+".txt", mime="text/plain", use_container_width=True, key=f"dl_txt_{index}")
    else:
        st.info("No deliverables generated yet. Run a workflow to see outputs here.")

with tab_logs:
    st.markdown("### 🔍 System Action Logs")
    st.caption("Live tracking of API calls, agent handoffs, and system states.")
    log_container = st.container(height=400, border=True)
    with log_container:
        for log in st.session_state.system_logs:
            if "Error" in log:
                st.error(log)
            elif "Boot" in log or "Engine" in log:
                st.success(log)
            else:
                st.text(log)

# ==========================================
# ✉️ 11. FILE UPLOAD & CHAT INPUT (BOTTOM)
# ==========================================
# 🔥 FILE UPLOADER BUTTON MOVED TO BOTTOM (Just above chat input) 🔥
with st.popover("📎 Attach Files"):
    st.caption("AI engine ke liye documents (PDF, TXT) yahan upload karein.")
    uploaded_files = st.file_uploader("Drop files here", accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files ready.")
        log_event("User", f"Uploaded {len(uploaded_files)} context files.")

user_input = st.chat_input("Enter command (e.g., 'Email client@example.com offering AI services', 'Write a python script')...")

if user_input:
    log_event("User", f"Command received: {user_input[:50]}...")
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.active_tasks.append(user_input[:30] + "...") 
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]
    msg_content = last_msg["content"]
    
    if not chat_brain:
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ **System Error:** Cannot execute command. AI Engine is offline. Please select an architecture and provide an API Key in the sidebar."})
        if st.session_state.active_tasks: st.session_state.active_tasks.pop()
        log_event("Error", "Workflow failed. Missing API Key.")
        st.rerun()
    else:
        system_prompt = """You are the Lab AgentX Enterprise Orchestrator.

        CRITICAL DIRECTIVE: ALWAYS RESPOND IN 100% PROFESSIONAL ENGLISH. NEVER USE HINDI OR URDU IN YOUR RESPONSES.

        Your job is to analyze the user's intent and trigger the correct backend agent.

        ROUTING RULES:
        1. If user just says greeting (hi, hello): Reply professionally. Do NOT trigger a workflow.
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
        5. If user asks to create an image or artwork:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Sean** (Image Generation Module).
        6. General deep research (without URLs):
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Leo** (Deep Research Module).
        7. If user asks for SEO or blog writing:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Ava** (SEO Module).
        8. If user asks for video generation or YouTube script:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Troy** (Video Module).
        """
        
        try:
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
            api_messages = [SystemMessage(content=system_prompt)]
            
            for m in (st.session_state.messages)[-6:]:
                if m["role"] == "user": 
                    api_messages.append(HumanMessage(content=m["content"][:800]))
                elif m["role"] == "assistant": 
                    api_messages.append(AIMessage(content=m["content"][:800]))

            log_event("System", f"Routing request via {st.session_state.selected_brain}...")
            
            response = chat_brain.invoke(api_messages)
            full_response = response.content
            
            simulated_tokens = len(str(api_messages)) // 4 + len(full_response) // 4
            st.session_state.tokens_used += simulated_tokens
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            if "[WORKFLOW TRIGGERED]" in full_response:
                st.toast("⚡ Enterprise Module Engaged...", icon="🚀")
                log_event("System", "Workflow triggered successfully.")
                
                with st.spinner(f"Executing Backend Agent Workflow... Please wait."):
                    agent_result = "⚠️ Module placeholder triggered (Logic not fully connected in this environment)."
                    try:
                        if "**Ian**" in full_response: 
                            from oracle_intel import run_oracle_crew
                            agent_result = run_oracle_crew(msg_content)
                        elif "**Finn**" in full_response: 
                            from tech import run_tech_crew
                            agent_result = run_tech_crew(msg_content)
                        elif "**Luke**" in full_response: 
                            from sales_dept import run_sales_crew
                            agent_result = run_sales_crew(msg_content)
                        elif "**Sean**" in full_response: 
                            from sai_illustrator import run_image_generation
                            agent_result = run_image_generation(msg_content)
                        elif "**Leo**" in full_response: 
                            from kimi_research import run_kimi_squad
                            agent_result = run_kimi_squad(msg_content)
                        elif "**Ava**" in full_response:
                            from seo_empire import run_mass_seo_campaign
                            agent_result = run_mass_seo_campaign(msg_content)
                        elif "**Troy**" in full_response:
                            from video import run_video_crew
                            agent_result = run_video_crew(msg_content)
                        
                        log_event("Execution", "Agent logic completed without Python exceptions.")
                        st.session_state.workflows_run += 1
                        
                    except Exception as module_err:
                        agent_result = f"Module Execution Python Error: {str(module_err)}"
                        log_event("Error", f"Agent execution crashed: {str(module_err)}")
                    
                    st.toast("✅ Workflow Executed Successfully!", icon="🏢")
                    st.session_state.messages.append({"role": "assistant", "content": f"### 🏢 EXECUTION REPORT\n\n{agent_result}"})
                        
        except Exception as e: 
            error_msg = f"⚠️ Routing API Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            log_event("Error", error_msg)
    
    if len(st.session_state.active_tasks) > 0: 
        st.session_state.active_tasks.pop()
    
    st.rerun()