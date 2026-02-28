import streamlit as st
import requests
import datetime
import os
import time
import sys
from dotenv import load_dotenv

# --- FOLDER PATHS SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'Agents')
sys.path.append(agents_dir)
for dept in ['Marketing', 'Tech', 'Video', 'Oracle', 'SEO', 'Legal', 'Finance', 'OmniReader', 'Multiplier', 'Sales', 'ImageGen', 'DeepResearch']:
    sys.path.append(os.path.join(agents_dir, dept))

# API keys load karein
load_dotenv()
INITIAL_GROQ_KEY = os.getenv("GROQ_API_KEY", "")

# FPDF library check (PDF generate karne ke liye)
try:
# Global Config
st.set_page_config(page_title="Lab AgentX | Enterprise AI Orchestrator", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# 🔥 BUG FIXED: Folder variables properly defined
MEMORY_FOLDER = "memory_logs"
UPLOAD_FOLDER = "uploads"
DELIVERABLES_FOLDER = "Deliverables"
SAVED_FILES_FOLDER = "Saved_Files"

for folder in [MEMORY_FOLDER, UPLOAD_FOLDER, DELIVERABLES_FOLDER, SAVED_FILES_FOLDER]:
    if not os.path.exists(folder): os.makedirs(folder)

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
if "current_page" not in st.session_state: st.session_state.current_page = "landing"
if "squad_chat" not in st.session_state:
    st.session_state.squad_chat = [
        {"agent": "System", "msg": "Enterprise Engine Initialized. Select a workflow or input a command.", "time": datetime.datetime.now().strftime("%H:%M")}
    ]
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Lab AgentX Enterprise Orchestrator online. What business process would you like to automate today?"}]
if "active_tasks" not in st.session_state: st.session_state.active_tasks = []
if "tokens_used" not in st.session_state: st.session_state.tokens_used = 124500

# Function for changing pages
def go_to_checkout(plan_name, price):
    st.session_state.selected_plan = plan_name
    st.session_state.plan_price = price
    st.session_state.final_price = price
    st.session_state.current_page = "checkout"

def go_to_dashboard():
    st.session_state.current_page = "dashboard"

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
# 🌟 LANDING PAGE (Enterprise Focus)
# ==========================================
if st.session_state.current_page == "landing":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        header[data-testid="stHeader"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        .block-container { padding-top: 0rem !important; max-width: 1100px !important; padding-left: 1rem !important; padding-right: 1rem !important;}
        footer {display: none !important;}
        .stApp { background-color: #020617; font-family: 'Plus Jakarta Sans', sans-serif; color: white; background-image: radial-gradient(circle at 50% -20%, #1e293b 0%, #020617 60%); }
        .custom-navbar { display: flex; justify-content: space-between; align-items: center; padding: 20px 0px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .nav-brand { font-size: 24px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px; }
        .nav-brand span { color: #38bdf8; }
        .nav-links { font-size: 14px; font-weight: 600; color: #94a3b8; cursor: pointer; transition: 0.3s; }
        .nav-links:hover { color: #38bdf8; }
        .hero-section { text-align: center; padding: 5rem 1rem 3rem 1rem; }
        .badge { background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 6px 16px; border-radius: 30px; font-size: 13px; font-weight: 700; letter-spacing: 1.5px; display: inline-block; margin-bottom: 25px; border: 1px solid rgba(56, 189, 248, 0.2); }
        .hero-title { font-size: 4.5rem; font-weight: 800; color: #f8fafc; margin-bottom: 1.5rem; line-height: 1.1; letter-spacing: -1.5px; }
        .hero-title span { background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-subtitle { font-size: 1.25rem; color: #94a3b8; max-width: 700px; margin: 0 auto 3rem auto; line-height: 1.7; font-weight: 500;}
        .section-title { font-size: 2.2rem; font-weight: 800; text-align: center; margin: 5rem 0 2.5rem 0; color: #f8fafc; }
        .section-title span { color: #38bdf8; }
        [data-testid="stVerticalBlockBorderWrapper"] { background: rgba(15, 23, 42, 0.6) !important; border-radius: 16px !important; border: 1px solid rgba(255,255,255,0.05) !important; padding: 2rem !important; transition: all 0.3s ease !important; backdrop-filter: blur(10px); height: 100%; }
        [data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-5px); border-color: rgba(56, 189, 248, 0.4) !important; box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4) !important; background: rgba(30, 41, 59, 0.8) !important; }
        div[data-testid="stButton"] > button { border-radius: 10px !important; padding: 0.6rem 0 !important; font-weight: 700 !important; background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%) !important; color: #ffffff !important; border: none !important; transition: all 0.3s ease !important; font-size: 15px !important; margin-top: 10px !important; box-shadow: 0 4px 14px rgba(56, 189, 248, 0.2) !important; }
        div[data-testid="stButton"] > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.4) !important; }
        .footer { text-align: center; padding: 3rem 0 2rem 0; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 4rem; color: #64748b; font-size: 14px;}
        @media (max-width: 768px) { .hero-title { font-size: 2.8rem; } .hero-section { padding-top: 3rem; } }
    </style>
    
    <div class="custom-navbar"><div class="nav-brand">Lab<span>AgentX</span></div><div class="nav-links">1-Click Demo ⚡</div></div>
    <div class="hero-section">
        <div class="badge">⚡ MULTI-MODEL AI ARCHITECTURE</div>
        <div class="hero-title">The Real-Time AI Workforce <br><span>For Creators & Agencies.</span></div>
        <div class="hero-subtitle">Stop managing 10 different tools. Connect your preferred AI Model (Claude, GPT-4, Gemini), state your intent, and let our agents execute the workflow.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>Autonomous</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Workflows</p>", unsafe_allow_html=True)
    with c2: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>16</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Enterprise Agents</p>", unsafe_allow_html=True)
    with c3: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>BYOK</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Bring Your Own Key</p>", unsafe_allow_html=True)
    with c4: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>0</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Human Intervention</p>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>💰 Simple, Scalable <span>Pricing</span></div>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        with st.container(border=True):
            st.markdown("### Starter")
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$19<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:14px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> <b>50</b> AI Workflows / mo<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> 5 Core Front-line Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Standard Speed</div>", unsafe_allow_html=True)
            if st.button("Start Free Trial", key="btn1", use_container_width=True): go_to_checkout("Starter", 19.99); st.rerun()
    with p2:
        with st.container(border=True):
            st.markdown("<div style='background:linear-gradient(135deg, #38bdf8, #818cf8); color:white; padding:4px 12px; border-radius:20px; font-size:11px; display:inline-block; font-weight:bold; margin-bottom:5px; letter-spacing:1px;'>MOST POPULAR</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-bottom:0; color:#38bdf8;'>Pro Creator</h3>", unsafe_allow_html=True)
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$49<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:14px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> <b>500</b> AI Workflows / mo<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> <b>Autonomous Mode Included</b><br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Full 16 Agent Roster</div>", unsafe_allow_html=True)
            if st.button("Upgrade to Pro", key="btn3", use_container_width=True): go_to_checkout("Pro Creator", 49.99); st.rerun()
    with p3:
        with st.container(border=True):
            st.markdown("### Agency")
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$99<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:14px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> <b>Custom</b> Volume Limits<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Dedicated API Keys<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Team Collaboration</div>", unsafe_allow_html=True)
            if st.button("Contact Sales", key="btn4", use_container_width=True): go_to_checkout("Agency", 99.99); st.rerun()

    st.markdown("<div class='footer'>Powered by Multi-Model Orchestration ⚡ • © 2026 Lab AgentX</div>", unsafe_allow_html=True)

# ==========================================
# 💳 CHECKOUT PAGE
# ==========================================
elif st.session_state.current_page == "checkout":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        header[data-testid="stHeader"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        .stApp { background-color: #ffffff !important; font-family: 'Inter', sans-serif; color: #111827 !important; }
        .block-container { max-width: 1100px !important; padding-top: 2rem !important; }
        .stMarkdown, .stText, p, span, h1, h2, h3, h4, h5, h6, label { color: #111827 !important; }
        .summary-card { background: #f9fafb; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e5e7eb;}
        .summary-price { font-size: 32px; font-weight: 700; color: #111827 !important; margin: 0; display: flex; align-items: baseline; gap: 8px;}
        .summary-price span { font-size: 14px; font-weight: 400; color: #6b7280 !important;}
        .summary-plan { font-size: 14px; color: #4b5563 !important; margin-top: 15px; margin-bottom: 5px; font-weight: 500;}
        .summary-plan-bold { font-weight: 700; font-size: 16px; margin-bottom: 20px;}
        .divider { border-top: 1px solid #e5e7eb; margin: 20px 0; }
        .bill-row { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 12px; color: #4b5563 !important;}
        .bill-row.total { font-weight: 700; color: #111827 !important; font-size: 16px; margin-top: 10px;}
        div[data-testid="stTextInput"] label { color: #4b5563 !important; font-size: 14px !important; font-weight: 500 !important; }
        div[data-testid="stTextInput"] input { background-color: #ffffff !important; color: #111827 !important; border: 1px solid #d1d5db !important; border-radius: 6px !important; padding: 12px !important;}
        div[data-testid="stTextInput"] input:focus { border-color: #d97706 !important; box-shadow: 0 0 0 1px #d97706 !important; }
        .payment-tabs { display: flex; gap: 10px; margin-bottom: 20px;}
        .pay-tab { flex: 1; border: 1px solid #d1d5db; border-radius: 6px; padding: 10px; text-align: center; font-size: 14px; font-weight: 500; display: flex; flex-direction: column; align-items: center; gap: 5px; background: white;}
        .pay-tab.active { border: 2px solid #d97706; background: #fffbeb;}
        div[data-testid="stForm"] div[data-testid="stButton"] > button { width: 100%; border-radius: 6px !important; padding: 14px 0 !important; font-weight: 600 !important; background-color: #d97706 !important; color: #ffffff !important; border: none !important; font-size: 16px !important; margin-top: 10px !important;}
        div[data-testid="stForm"] div[data-testid="stButton"] > button:hover { background-color: #b45309 !important; }
        [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    if "final_price" not in st.session_state: st.session_state.final_price = st.session_state.plan_price
    if st.button("← Go Back", key="back_to_landing"): st.session_state.current_page = "landing"; st.rerun()

    col_left, col_space, col_right = st.columns([1, 0.2, 1.2])
    with col_left:
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-price">${st.session_state.final_price:.2f} <span>inc. VAT</span></div>
            <div class="summary-plan">Lab AgentX Subscription</div>
            <div class="summary-plan-bold">{st.session_state.selected_plan} Plan / month</div>
            <div class="divider"></div>
            <div class="bill-row"><span>Subtotal</span><span>${st.session_state.final_price:.2f}</span></div>
            <div class="bill-row"><span>VAT</span><span>$0.00</span></div>
            <div class="bill-row total"><span>Total</span><span>${st.session_state.final_price:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='payment-tabs'><div class='pay-tab active'>💳 Card</div><div class='pay-tab'>🅿️ PayPal</div></div>", unsafe_allow_html=True)
        with st.form("stripe_checkout_simulation"):
            st.text_input("Card number", placeholder="XXXX XXXX XXXX XXXX")
            c_exp, c_cvc = st.columns(2)
            with c_exp: st.text_input("Expiration date", placeholder="MM / YY")
            with c_cvc: st.text_input("Security code", placeholder="CVC", type="password")
            st.text_input("Name on card", placeholder="Bruce Wayne")
            coupon = st.text_input("Add discount code (Use FUNDERVIP)", placeholder="Enter code here...")
            
            submit_label = "Complete VIP Setup" if st.session_state.final_price == 0.0 else "Subscribe now"
            if st.form_submit_button(submit_label):
                if coupon.strip().upper() == "FUNDERVIP":
                    st.success("🎉 VIP Code Applied! Activating your Agent Workspace...")
                    time.sleep(1); st.session_state.final_price = 0.0; go_to_dashboard(); st.rerun()
                elif st.session_state.final_price > 0:
                    with st.spinner("Processing payment securely with Stripe..."):
                        time.sleep(2); st.success("✅ Payment Successful! Redirecting to Workspace...")
                        time.sleep(1); go_to_dashboard(); st.rerun()

# ==========================================
# 🧪 MAIN DASHBOARD (ENTERPRISE MISSION CONTROL)
# ==========================================
elif st.session_state.current_page == "dashboard":

    # 🔥 STRICTLY CLEAN UI CSS - COMPLETELY SAFE 🔥
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        .stApp, .stAppViewContainer { background-color: #020617 !important; font-family: 'Plus Jakarta Sans', sans-serif; color: #f8fafc; }
        
        /* Removing hacky overrides to keep standard Streamlit layout stable */
        section[data-testid="stSidebar"] { display: block !important; background-color: #0f172a !important; border-right: 1px solid #1e293b !important; }
        .block-container { padding-top: 2.5rem !important; max-width: 1400px !important; }
        .stMarkdown, .stText, p, span, h1, h2, h3, h4, h5, h6, label { color: #f8fafc !important; }
        
        /* Premium Buttons */
        [data-testid="stSidebar"] button { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 6px !important; }
        [data-testid="stSidebar"] button * { color: #ffffff !important; font-weight: 600 !important; font-size: 14px !important;}
        [data-testid="stSidebar"] button:hover { border-color: #38bdf8 !important; background-color: #0f172a !important; }
        
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

    # 🔥 UPDATED AGENTS WITH PROFESSIONAL REAL NAMES 🔥
    AGENTS_INFO = {
        "Lab AgentX": {"name": "Lab AgentX", "role": "System Orchestrator", "icon": "🏢", "desc": "The mastermind CEO.", "stat": "System Commander"},
        "Leo": {"name": "Leo", "role": "Research Analyst", "icon": "🔍", "desc": "Deep web research.", "stat": "Intel"},
        "Troy": {"name": "Troy", "role": "Video Producer", "icon": "📹", "desc": "Viral video scripts.", "stat": "Media"},
        "Nate": {"name": "Nate", "role": "Content Strategist", "icon": "✍️", "desc": "Generates content.", "stat": "Content"},
        "Luke": {"name": "Luke", "role": "Outbound Sales", "icon": "🎯", "desc": "Hunts leads and outreach.", "stat": "Sales"},
        
        "Mia": {"name": "Mia", "role": "Retention Manager", "icon": "🛡️", "desc": "Monitors churn.", "stat": "Support"},
        "Finn": {"name": "Finn", "role": "Lead Developer", "icon": "💻", "desc": "Writes PRs and bug fixes.", "stat": "Tech"},
        "Sam": {"name": "Sam", "role": "PR & Email Marketing", "icon": "📧", "desc": "Drafts cold email sequences.", "stat": "Communications"},
        "Seth": {"name": "Seth", "role": "Data Scientist", "icon": "📊", "desc": "Analyzes big data.", "stat": "Knowledge"},
        "Zoe": {"name": "Zoe", "role": "UX/UI Designer", "icon": "⚡", "desc": "Tests website flows.", "stat": "UX/UI"},
        "Gabe": {"name": "Gabe", "role": "Head of Marketing", "icon": "📈", "desc": "Ad strategies.", "stat": "Ads"},
        "Ian": {"name": "Ian", "role": "Intelligence Scout", "icon": "🕸️", "desc": "Spies on competitors.", "stat": "Scraping"},
        "Ava": {"name": "Ava", "role": "SEO Specialist", "icon": "🚀", "desc": "Mass blogs generator.", "stat": "Blogger"},
        "Sean": {"name": "Sean", "role": "Art Director", "icon": "🎨", "desc": "Draws images.", "stat": "Visuals"},
        "Nora": {"name": "Nora", "role": "Financial Analyst", "icon": "💰", "desc": "Crunches VC data.", "stat": "Wall St"},
        "Noah": {"name": "Noah", "role": "Legal Counsel", "icon": "⚖️", "desc": "Reviews contracts.", "stat": "Lawyer"}
    }

    FRONT_LINE_AGENTS = ["Lab AgentX", "Leo", "Troy", "Nate", "Luke"]
    BACKEND_AGENTS = [key for key in AGENTS_INFO.keys() if key not in FRONT_LINE_AGENTS]
    
    current_active_agent = "Lab AgentX"
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and ("Task Assigned" in msg["content"] or "Initiating" in msg["content"]):
            msg_lower = msg["content"].lower()
            if "sean" in msg_lower: current_active_agent = "Sean"
            elif "nate" in msg_lower: current_active_agent = "Nate"
            elif "luke" in msg_lower: current_active_agent = "Luke"
            elif "leo" in msg_lower or "**leo**" in msg_lower: current_active_agent = "Leo"
            elif "finn" in msg_lower: current_active_agent = "Finn"
            elif "troy" in msg_lower: current_active_agent = "Troy"
            elif "ian" in msg_lower: current_active_agent = "Ian"
            elif "gabe" in msg_lower: current_active_agent = "Gabe"
            elif "ava" in msg_lower: current_active_agent = "Ava"
            elif "nora" in msg_lower: current_active_agent = "Nora"
            elif "noah" in msg_lower: current_active_agent = "Noah"
            elif "seth" in msg_lower: current_active_agent = "Seth"
            elif "autonomous" in msg_lower: current_active_agent = "System"
            if current_active_agent != "Lab AgentX": break

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
                
        st.markdown("---")
        st.markdown("<h3 style='color: #f8fafc; font-size: 14px; margin-bottom: 10px;'>⚡ Available Workflows</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='workflow-card' style='border-color: #f59e0b;'><div class='w-title'>Competitor Takedown</div><div class='w-desc'>Deep scans URLs and generates business attack plans.</div></div>
        <div class='workflow-card' style='border-color: #8b5cf6;'><div class='w-title'>Closed-Loop Tech</div><div class='w-desc'>Generates Python/Web code and audits it internally.</div></div>
        <div class='workflow-card' style='border-color: #10b981;'><div class='w-title'>Content Empire</div><div class='w-desc'>Repurposes YouTube URLs into Omni-channel content.</div></div>
        <div class='workflow-card' style='border-color: #ef4444;'><div class='w-title'>Autonomous Sales</div><div class='w-desc'>Finds leads and ACTUALLY SENDS cold emails via Gmail.</div></div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        # 🔥 SAFELY MOVED ATTACHMENT TO SIDEBAR TO PREVENT UI BUGS 🔥
        with st.expander("📎 Attach Documents", expanded=False):
            st.caption("AI Engine ke liye files upload karein")
            uploaded_files = st.file_uploader("Drop context files here", type=["pdf", "png", "txt", "csv"], accept_multiple_files=True)
            if uploaded_files: st.success(f"✅ {len(uploaded_files)} file(s) ready.")

        st.markdown("---")
        # BYOK SELECTION
        with st.expander("🔑 BYOK (Bring Your Own Key)", expanded=True):
            st.markdown("<p style='font-size: 11px; color: #94a3b8;'>Enterprise 100% Margin Model. User provides API.</p>", unsafe_allow_html=True)
            
            selected_brain = st.selectbox("🧠 Select Engine", [
                "Groq (Llama 3.3 - Fastest)", 
                "OpenAI (GPT-4o - Deepest)",
                "Anthropic (Claude 3.5 Sonnet)",
                "Google (Gemini 1.5 Pro)"
            ])
            st.session_state.selected_brain = selected_brain
            
            if "Groq" in selected_brain:
                live_api_key = st.text_input("Groq API Key", type="password", value=INITIAL_GROQ_KEY)
            elif "OpenAI" in selected_brain:
                live_api_key = st.text_input("OpenAI API Key (sk-...)", type="password")
            elif "Anthropic" in selected_brain:
                live_api_key = st.text_input("Anthropic API Key", type="password")
            elif "Gemini" in selected_brain:
                live_api_key = st.text_input("Google Gemini API Key", type="password")
                
            st.session_state.live_api_key = live_api_key

    # Initialize Engine (Model Agnostic)
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
        except Exception as mod_err: 
            st.sidebar.error("⚠️ Requirements update needed for this model.")
    else: 
        st.warning("⚠️ API Key required to boot Enterprise Engine.")

    # UI Columns
    col_main, col_files = st.columns([2.5, 1])
    
    with col_main:
        with st.container(height=500, border=False):
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
    
    # 🔥 COMPLETELY NATIVE CHAT INPUT (No overlapping, no crashes) 🔥
    user_input = st.chat_input("Enter outcome requirement (e.g., 'Email test@example.com offering AI services')...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.active_tasks.append(user_input[:30] + "...") 
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]
        msg_content = last_msg["content"]
        
        # 🔥 ENGLISH STRICT PROMPT WITH REAL HUMAN NAMES 🔥
        system_prompt = """You are the Lab AgentX Enterprise Orchestrator. 

        CRITICAL RULE 0: ALWAYS RESPOND IN 100% PROFESSIONAL ENGLISH. NO OTHER LANGUAGES.

        RULES:
        1. For greetings: Reply professionally in English. No workflow triggers.
        2. If user provides a URL or asks for competitor analysis:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Ian** (Web Intelligence & Scraping Module).
        3. If user asks for code, programming, or software development:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Finn** (Closed-Loop Tech & QA Module).
        4. If user asks for marketing, ads, or sales content:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Gabe** (Direct Response Marketing Module).
        5. If user provides a YouTube link or asks for repurposing:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Nate** (Content Multiplier Module).
        6. General research without URLs:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Leo** (Deep Research Module).
        7. If user asks to create, draw, or generate an image:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Sean** (Image Generation Module).
        8. If user asks for financial or market size data:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Nora** (Finance Analyst Module).
        9. If user asks to review legal contracts:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Noah** (Legal Review Module).
        10. If user asks to generate a video or script:
           FORMAT EXACTLY:
           [WORKFLOW TRIGGERED]
           - Initiating: **Troy** (Video Production Module).

        Available Agents:
        - Ian (Web scraping, URLs, and competitor analysis)
        - Gabe (Writing Ad Copy and Marketing Campaigns)
        - Sean (Images)
        - Nate (Repurposing)
        - Luke (Sales)
        - Mia (Retention)
        - Noah (Legal)
        - Nora (Finance)
        - Ava (SEO blogs)
        - Finn (Coding)
        - Seth (YouTube extraction)
        - Troy (Video)
        - Leo (Deep research without URLs)
        - Sam (PR/emails)
        - Zoe (UX/UI)
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

                # Running selected AI Model
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
                        
                        # Mapping the new Real Names to the respective logic
                        if "**Gabe**" in full_response: from marketing import run_marketing_crew; agent_result = run_marketing_crew(msg_content)
                        elif "**Sean**" in full_response: from sai_illustrator import run_image_generation; agent_result = run_image_generation(msg_content)
                        elif "**Ian**" in full_response: from oracle_intel import run_oracle_crew; agent_result = run_oracle_crew(msg_content)
                        elif "**Nora**" in full_response: from lucius_finance import run_finance_crew; agent_result = run_finance_crew(msg_content)
                        elif "**Seth**" in full_response: from omni_reader import run_omnireader_crew; agent_result = run_omnireader_crew(msg_content)
                        elif "**Finn**" in full_response: from tech import run_tech_crew; agent_result = run_tech_crew(msg_content)
                        elif "**Ava**" in full_response: from seo_empire import run_mass_seo_campaign; agent_result = run_mass_seo_campaign(msg_content.lower().replace("ava,", "").strip())
                        elif "**Leo**" in full_response: from kimi_research import run_kimi_squad; agent_result = run_kimi_squad(msg_content)
                        elif "**Luke**" in full_response: from sales_dept import run_sales_crew; agent_result = run_sales_crew(msg_content)
                        elif "**Nate**" in full_response: from content_multiplier import run_multiplier_crew; agent_result = run_multiplier_crew(msg_content)
                        elif "**Noah**" in full_response: from daredevil_legal import run_legal_crew; agent_result = run_legal_crew(msg_content)
                        elif "**Troy**" in full_response: from video import run_video_crew; agent_result = run_video_crew(msg_content)
                        
                        if len(st.session_state.active_tasks) > 0:
                            st.toast("✅ Workflow Executed Successfully!", icon="🏢")
                            st.session_state.messages.append({"role": "assistant", "content": f"### 🏢 EXECUTION REPORT\n\n{agent_result}"})
                            
            except Exception as e: st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Execution Error: {str(e)}"})
        
        if len(st.session_state.active_tasks) > 0: st.session_state.active_tasks.pop()
        st.rerun()