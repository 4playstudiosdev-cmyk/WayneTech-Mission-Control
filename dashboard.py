import streamlit as st
import requests
import datetime
import os
import glob
import time
import sys
import shutil 
from dotenv import load_dotenv

# --- CLOUD MATE FOLDER PATHS FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'Agents')
sys.path.append(agents_dir)
for dept in ['Marketing', 'Tech', 'Video', 'Oracle', 'SEO', 'Legal', 'Finance', 'OmniReader', 'Multiplier', 'sales', 'ImageGen']:
    sys.path.append(os.path.join(agents_dir, dept))

# API Keys load karna
load_dotenv()
INITIAL_GROQ_KEY = os.getenv("GROQ_API_KEY", "")

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# Global Config
st.set_page_config(page_title="Lab AgentX | AI Agency", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")

# 🔥 FOLDER DEFINITIONS
MEMORY_FOLDER = "memory_logs"
UPLOAD_FOLDER = "uploads"
DELIVERABLES_FOLDER = "Deliverables"
SAVED_FILES_FOLDER = "Saved_Files" 

for folder in [MEMORY_FOLDER, UPLOAD_FOLDER, DELIVERABLES_FOLDER, SAVED_FILES_FOLDER]:
    if not os.path.exists(folder): os.makedirs(folder)

# 🧠 PAGE ROUTING & MEMORY SYSTEM
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"
if "selected_plan" not in st.session_state:
    st.session_state.selected_plan = None
if "plan_price" not in st.session_state:
    st.session_state.plan_price = 0.0

# 🤖 SQUAD CHAT MEMORY (For Inter-Agent Communication)
if "squad_chat" not in st.session_state:
    st.session_state.squad_chat = [
        {"agent": "Lab AgentX", "msg": "System initialized. All 16 agents are online and synced. Standing by for Commander's orders.", "time": datetime.datetime.now().strftime("%H:%M")}
    ]

def go_to_checkout(plan_name, price):
    st.session_state.selected_plan = plan_name
    st.session_state.plan_price = price
    st.session_state.final_price = price
    st.session_state.current_page = "checkout"

def go_to_dashboard():
    st.session_state.current_page = "dashboard"

# 💬 THE VIP SQUAD CHAT MODAL
@st.dialog("💬 Daily Standup & Squad Chat")
def show_squad_chat():
    st.markdown("<p style='color:#94a3b8; font-size:14px; margin-bottom:15px; border-bottom: 1px solid #1e293b; padding-bottom: 10px;'>Secure channel. Monitoring live agent collaboration and task handoffs.</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #334155; display: flex; align-items: center; justify-content: space-between;'>
            <div>
                <div style='color: #f8fafc; font-weight: 700; font-size: 14px;'>🎙️ Latest Standup Audio</div>
                <div style='color: #94a3b8; font-size: 12px;'>Synthesized AI Voices (Gojo, Franky, Nanami)</div>
            </div>
            <button style='background: #38bdf8; color: #0f172a; border: none; padding: 8px 15px; border-radius: 8px; font-weight: 800; cursor: pointer;'>▶ Play Audio</button>
        </div>
    """, unsafe_allow_html=True)

    chat_html = "<div style='max-height: 350px; overflow-y: auto; padding-right: 10px;'>"
    for chat in st.session_state.squad_chat:
        agent_color = "#38bdf8" if chat['agent'] == "Lab AgentX" else "#10b981" if chat['agent'] == "System" else "#f59e0b"
        chat_html += f"""
        <div style='background: #0f172a; padding: 12px 16px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid {agent_color};'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                <span style='color: {agent_color}; font-weight: 800; font-size: 13px; text-transform: uppercase;'>{chat['agent']}</span>
                <span style='color: #64748b; font-size: 11px; font-weight: 600;'>{chat['time']}</span>
            </div>
            <div style='color: #f8fafc; font-size: 14px; line-height: 1.5;'>{chat['msg']}</div>
        </div>
        """
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

# ==========================================
# 🌟 VIP SAAS LANDING PAGE
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
        .nav-links { font-size: 14px; font-weight: 600; color: #94a3b8; cursor: pointer; transition: 0.3s; }
        .nav-links:hover { color: #38bdf8; }
        .hero-section { text-align: center; padding: 5rem 1rem 3rem 1rem; }
        .badge { background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 6px 16px; border-radius: 30px; font-size: 13px; font-weight: 700; letter-spacing: 1.5px; display: inline-block; margin-bottom: 25px; border: 1px solid rgba(56, 189, 248, 0.2); }
        .hero-title { font-size: 4rem; font-weight: 800; color: #f8fafc; margin-bottom: 1.5rem; line-height: 1.15; letter-spacing: -1.5px; }
        .hero-title span { background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-subtitle { font-size: 1.2rem; color: #94a3b8; max-width: 650px; margin: 0 auto 3rem auto; line-height: 1.7; }
        .section-title { font-size: 2.2rem; font-weight: 800; text-align: center; margin: 5rem 0 2.5rem 0; color: #f8fafc; }
        .section-title span { color: #38bdf8; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(15, 23, 42, 0.6) !important; border-radius: 16px !important; border: 1px solid rgba(255,255,255,0.05) !important;
            padding: 1.5rem !important; transition: all 0.3s ease !important; backdrop-filter: blur(10px); height: 100%;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-5px); border-color: rgba(56, 189, 248, 0.4) !important; box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4) !important; background: rgba(30, 41, 59, 0.8) !important;
        }
        div[data-testid="stButton"] > button { 
            border-radius: 10px !important; padding: 0.6rem 0 !important; font-weight: 700 !important; 
            background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%) !important; color: #ffffff !important; 
            border: none !important; transition: all 0.3s ease !important; font-size: 15px !important; margin-top: 10px !important;
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.2) !important;
        }
        div[data-testid="stButton"] > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.4) !important; }
        .footer { text-align: center; padding: 3rem 0 2rem 0; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 4rem; color: #64748b; font-size: 14px;}
        @media (max-width: 768px) { .hero-title { font-size: 2.5rem; } .hero-section { padding-top: 3rem; } }
    </style>
    
    <div class="custom-navbar"><div class="nav-brand">🧪 Lab AgentX</div><div class="nav-links">Sign In →</div></div>
    <div class="hero-section">
        <div class="badge">🚀 VERSION 2.0 LIVE</div>
        <div class="hero-title">Hire The Ultimate AI Squad.<br><span>Automate Everything.</span></div>
        <div class="hero-subtitle">Stop relying on boring tools. Lab AgentX replaces your entire team. Access 16 super-intelligent anime agents for Marketing, Sales, Tech, and Research working 24/7.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>16+</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Elite AI Agents</p>", unsafe_allow_html=True)
    with c2: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>24/7</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Cron Jobs & Execution</p>", unsafe_allow_html=True)
    with c3: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>10x</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Faster Delivery</p>", unsafe_allow_html=True)
    with c4: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>0%</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Human Error</p>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>⚙️ How It <span>Works</span></div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True): st.markdown("<h1 style='color:#38bdf8; margin-top:0;'>01</h1><h3 style='margin-bottom:10px;'>Give Commands</h3><p style='color:#94a3b8; font-size:14px; line-height:1.6;'>Just write your task. Lab AgentX automatically routes it to the correct department.</p>", unsafe_allow_html=True)
    with f2:
        with st.container(border=True): st.markdown("<h1 style='color:#38bdf8; margin-top:0;'>02</h1><h3 style='margin-bottom:10px;'>Squad Standups</h3><p style='color:#94a3b8; font-size:14px; line-height:1.6;'>Agents hold internal audio standups to collaborate and execute flawlessly.</p>", unsafe_allow_html=True)
    with f3:
        with st.container(border=True): st.markdown("<h1 style='color:#38bdf8; margin-top:0;'>03</h1><h3 style='margin-bottom:10px;'>Overnight Logs</h3><p style='color:#94a3b8; font-size:14px; line-height:1.6;'>Wake up to finished work. Review automated tasks done while you slept.</p>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>💎 Choose Your <span>Plan</span></div>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        with st.container(border=True):
            st.markdown("### Starter")
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$19<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 5 AI Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Content Multiplier<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Standard Dashboard</div>", unsafe_allow_html=True)
            if st.button("Start Free Trial", key="btn1", use_container_width=True): go_to_checkout("Starter", 19.99); st.rerun()
    with p2:
        with st.container(border=True):
            st.markdown("### Growth")
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$39<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 10 AI Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Sales Outreach<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> SEO Empire</div>", unsafe_allow_html=True)
            if st.button("Get Growth", key="btn2", use_container_width=True): go_to_checkout("Growth", 39.99); st.rerun()
    with p3:
        with st.container(border=True):
            st.markdown("<div style='background:linear-gradient(135deg, #38bdf8, #818cf8); color:white; padding:3px 10px; border-radius:20px; font-size:10px; display:inline-block; font-weight:bold; margin-bottom:5px;'>MOST POPULAR</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-bottom:0; color:#38bdf8;'>Elite Agency</h3>")
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$54<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 16 Premium AI Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Audio Standups<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Overnight Cron Jobs</div>", unsafe_allow_html=True)
            if st.button("Get Elite Access", key="btn3", use_container_width=True): go_to_checkout("Elite Agency", 54.99); st.rerun()
    with p4:
        with st.container(border=True):
            st.markdown("### Enterprise")
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$89<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 25+ Custom Bots<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Dedicated API Keys<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> White-label OS</div>", unsafe_allow_html=True)
            if st.button("Contact Sales", key="btn4", use_container_width=True): go_to_checkout("Enterprise", 89.99); st.rerun()

    st.markdown("<div class='footer'>Backed by Groq Technology ⚡ • © 2026 Lab AgentX | Built for Scale</div>", unsafe_allow_html=True)

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
    if st.button("← Return to Lab AgentX HQ", key="back_to_landing"): st.session_state.current_page = "landing"; st.rerun()

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
            coupon = st.text_input("Add discount code (Use FUNDERVIP)", placeholder="Enter code...")
            
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
# 🧪 MAIN DASHBOARD (DARK VIBE WORKSPACE)
# ==========================================
elif st.session_state.current_page == "dashboard":

    # 🔥 THE CLEAN & SAFE UI CSS 🔥
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        /* Force complete dark background on all main containers to kill white gaps */
        .stApp, .stAppViewContainer, .stAppScrollToBottomContainer { 
            background-color: #020617 !important; 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            color: #f8fafc;
        }
        
        section[data-testid="stSidebar"] { display: block !important; background-color: #0f172a !important; border-right: 1px solid #1e293b !important; }
        .block-container { padding-top: 3rem !important; max-width: 1400px !important; }
        .stMarkdown, .stText, p, span, h1, h2, h3, h4, h5, h6, label { color: #f8fafc !important; }
        
        /* 1. SAFE SIDEBAR BUTTONS FIX */
        [data-testid="stSidebar"] button { 
            background-color: #1e293b !important; 
            border: 1px solid #334155 !important; 
            border-radius: 8px !important; 
        }
        [data-testid="stSidebar"] button * { 
            color: #ffffff !important; 
            font-weight: 700 !important; 
        }
        [data-testid="stSidebar"] button:hover { 
            border-color: #38bdf8 !important; 
            background-color: #0f172a !important; 
        }
        [data-testid="stSidebar"] button:hover * { 
            color: #38bdf8 !important; 
        }
        
        .squad-btn button { background-color: #38bdf8 !important; border: none !important; }
        .squad-btn button * { color: #020617 !important; font-weight: 800 !important; }
        .squad-btn button:hover { background-color: #0ea5e9 !important; }
        
        /* General Stats and Kanban */
        .top-stats { display: flex; justify-content: space-around; background: #0f172a; padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); margin-bottom: 15px; border: 1px solid #1e293b; flex-wrap: wrap; gap: 15px; }
        .stat-box { text-align: center; flex: 1; min-width: 120px;} 
        .stat-value { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: #f8fafc !important; } 
        .stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-top: 4px; color: #94a3b8 !important; }
        .kanban-header { font-size: 13px; font-weight: 800; color: #94a3b8 !important; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 3px solid #1e293b; text-transform: uppercase; letter-spacing: 1px; }
        .k-assigned { border-bottom-color: #f59e0b; } .k-progress { border-bottom-color: #3b82f6; } .k-review { border-bottom-color: #8b5cf6; } .k-done { border-bottom-color: #10b981; }
        .k-card { background: #0f172a !important; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); transition: all 0.2s ease; word-wrap: break-word; }
        .k-card:hover { border-color: #38bdf8; transform: translateY(-2px); }
        .k-title { font-size: 14px; font-weight: 700; margin-bottom: 8px; color: #f8fafc !important;} 
        .k-agent { font-size: 12px; color: #94a3b8 !important; display: flex; align-items: center; gap: 6px; font-weight: 600;} 
        .agent-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 12px; margin-bottom: 10px; border-radius: 12px; background: #1e293b !important; border: 1px solid #334155; cursor: pointer;}
        .agent-row:hover { border-color: #38bdf8; }
        .agent-name-container { display: flex; flex-direction: column; gap: 4px; }
        .agent-name { font-size: 14px; font-weight: 800; display: flex; align-items: center; gap: 8px; color: #f8fafc !important; } 
        .agent-role { font-size: 10px; color: #94a3b8 !important; font-weight: 700; margin-left: 28px; text-transform: uppercase; letter-spacing: 0.5px;}
        .status-badge { font-size: 10px; padding: 4px 10px; border-radius: 20px; font-weight: 800; letter-spacing: 0.5px;}
        .st-working { background: rgba(34, 197, 94, 0.15) !important; color: #4ade80 !important; border: 1px solid #22c55e !important; box-shadow: 0 0 10px rgba(34, 197, 94, 0.2); } 
        .st-standby { background: rgba(148, 163, 184, 0.1) !important; color: #94a3b8 !important; border: 1px solid #334155 !important; }
        .stChatMessage { background-color: #0f172a !important; border: 1px solid #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
        
        /* 🔥 FIX 2: Kill the White Bottom Bar & Force White Text inside Chat */
        /* This completely removes the white background at the bottom of the screen */
        div[data-testid="stBottom"], 
        div[data-testid="stBottom"] > div { 
            background-color: #020617 !important; 
            background-image: none !important;
        }
        
        div[data-testid="stChatInput"] { 
            background-color: transparent !important; 
        }
        div[data-testid="stChatInput"] > div, 
        div[data-testid="stChatInput"] .stChatInput { 
            background-color: #1e293b !important; 
            border: 1px solid #334155 !important; 
            border-radius: 12px !important; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
        }
        
        /* Explicitly forcing white text no matter what Streamlit tries to do */
        div[data-testid="stChatInput"] textarea { 
            color: #ffffff !important; 
            -webkit-text-fill-color: #ffffff !important; 
            caret-color: #ffffff !important;
            font-size: 15px !important;
            background-color: transparent !important;
        }
        div[data-testid="stChatInput"] textarea::placeholder { 
            color: #9ca3af !important; 
            -webkit-text-fill-color: #9ca3af !important; 
        }
        div[data-testid="stChatInput"] svg { fill: #9ca3af !important; }
        
        div[data-testid="stTabs"] button { color: #94a3b8 !important; font-weight: 700 !important; font-size: 15px !important; padding-bottom: 10px !important;}
        div[data-testid="stTabs"] button[aria-selected="true"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }
        
        /* ORG CHART SPECIFIC CSS (MUDDY OS CLONE) */
        .org-tree-wrapper { padding: 40px 0; display: flex; flex-direction: column; align-items: center; }
        .org-node { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px 25px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3); min-width: 280px; z-index: 2; position: relative;}
        .org-node.ceo { border-top: 4px solid #f59e0b; }
        .org-node.coo { border-top: 4px solid #10b981; margin-top: 30px; }
        .org-node h3 { font-size: 16px; margin: 0 0 5px 0; color: #f8fafc; display: flex; align-items: center; justify-content: center; gap: 8px;}
        .org-node p { font-size: 12px; color: #94a3b8; margin: 0; }
        .line-vertical { width: 2px; height: 30px; background: #334155; }
        .line-horizontal { width: 80%; height: 2px; background: #334155; margin-top: 30px; position: relative; display: flex; justify-content: space-between;}
        .line-horizontal::before { content: ''; position: absolute; left: 0; top: 0; width: 2px; height: 30px; background: #334155; }
        .line-horizontal::after { content: ''; position: absolute; right: 0; top: 0; width: 2px; height: 30px; background: #334155; }
        .line-horizontal .mid-drop { position: absolute; left: 50%; top: 0; width: 2px; height: 30px; background: #334155; transform: translateX(-50%); }
        .dept-container { display: flex; justify-content: space-between; width: 100%; gap: 20px; margin-top: 30px;}
        .dept-col { flex: 1; display: flex; flex-direction: column; gap: 15px; }
        .dept-head { background: #0f172a; border-radius: 12px; padding: 20px; border: 1px solid #334155; text-align: left;}
        .dept-head.tech { border-left: 4px solid #3b82f6; }
        .dept-head.mkt { border-left: 4px solid #f59e0b; }
        .dept-head.rev { border-left: 4px solid #10b981; }
        .dept-head h3 { font-size: 15px; margin: 0 0 5px 0; display: flex; justify-content: space-between; align-items: center;}
        .dept-head p { font-size: 11px; color: #94a3b8; margin: 0; line-height: 1.4;}
        .agent-box { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 15px; display: flex; flex-direction: column; gap: 10px;}
        .agent-box-top { display: flex; justify-content: space-between; align-items: center;}
        .agent-box-title { font-size: 14px; font-weight: 700; color: #f8fafc; display: flex; align-items: center; gap: 6px;}
        .agent-box-role { font-size: 11px; color: #94a3b8; margin-bottom: 5px;}
        .agent-tags { display: flex; gap: 8px; flex-wrap: wrap;}
        .tag-active { background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid #22c55e; }
        .tag-model { background: #334155; color: #cbd5e1; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }
        .tag-special { background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid #0ea5e9;}
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    AGENTS_INFO = {
        "Lab AgentX": {"name": "Lab AgentX", "role": "Squad Lead", "icon": "🧪", "desc": "The mastermind CEO.", "stat": "System Commander"},
        "Orihime": {"name": "Orihime Inoue", "role": "Retention Specialist", "icon": "🛡️", "desc": "Monitors churn.", "stat": "Support"},
        "Franky": {"name": "Franky", "role": "Developer Agent", "icon": "🦾", "desc": "Writes PRs and bug fixes.", "stat": "Tech"},
        "L": {"name": "L Lawliet", "role": "Customer Research", "icon": "🍰", "desc": "Deep web research.", "stat": "Intel"},
        "Light": {"name": "Light Yagami", "role": "Outbound Scout", "icon": "📓", "desc": "Hunts leads and outreach.", "stat": "Sales"},
        "Naruto": {"name": "Naruto Uzumaki", "role": "Content Writer", "icon": "🦊", "desc": "Generates content.", "stat": "Content"},
        "Sebastian": {"name": "Sebastian", "role": "Email Marketing", "icon": "🎩", "desc": "Drafts cold email sequences.", "stat": "Communications"},
        "Senku": {"name": "Senku Ishigami", "role": "Data Agent", "icon": "🧫", "desc": "Analyzes big data.", "stat": "Knowledge"},
        "Bulma": {"name": "Bulma", "role": "Conversion Optimizer", "icon": "💡", "desc": "Tests website flows.", "stat": "UX/UI"},
        "Gojo": {"name": "Satoru Gojo", "role": "Marketing Head", "icon": "♾️", "desc": "Ad strategies.", "stat": "Ads"},
        "Itachi": {"name": "Itachi Uchiha", "role": "Web Scraper", "icon": "👁️", "desc": "Spies on competitors.", "stat": "Scraping"},
        "Akatsuki": {"name": "The Akatsuki", "role": "SEO Empire", "icon": "☁️", "desc": "Mass blogs generator.", "stat": "Blogger"},
        "Tengen": {"name": "Tengen Uzui", "role": "Video Producer", "icon": "✨", "desc": "Viral video scripts.", "stat": "Media"},
        "Sai": {"name": "Sai", "role": "Chief Illustrator", "icon": "🖌️", "desc": "Draws images.", "stat": "Visuals"},
        "Nami": {"name": "Nami", "role": "Finance Analyst", "icon": "🍊", "desc": "Crunches VC data.", "stat": "Wall St"},
        "Nanami": {"name": "Kento Nanami", "role": "Legal Expert", "icon": "👔", "desc": "Reviews contracts.", "stat": "Lawyer"}
    }

    def get_all_deliverables():
        files = []
        for root, _, filenames in os.walk(DELIVERABLES_FOLDER):
            for fname in filenames:
                files.append(os.path.normpath(os.path.join(root, fname)))
        return set(files)

    if "hidden_files" not in st.session_state: st.session_state.hidden_files = get_all_deliverables()
    if "session_start_time" not in st.session_state: st.session_state.session_start_time = time.time() - 5
    if "full_memory" not in st.session_state: st.session_state.full_memory = []
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": f"Lab AgentX Online. Welcome to the **{st.session_state.selected_plan} Workspace**. Your elite squad is ready."}]
    if "active_tasks" not in st.session_state: st.session_state.active_tasks = []
    if "assigned_tasks" not in st.session_state: st.session_state.assigned_tasks = []
    if "review_tasks" not in st.session_state: st.session_state.review_tasks = []
    if "tokens_used" not in st.session_state: st.session_state.tokens_used = 124500

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

    done_tasks_list = get_done_tasks()
    current_active_agent = "Lab AgentX"
    agent_keywords_map = { "Sai": ["sai", "draw", "image"], "Naruto": ["naruto", "multiplier"], "Light": ["light", "leadbooker", "booking", "sales"], "Orihime": ["orihime", "retentionbot", "churn"], "Gojo": ["gojo", "marketing", "superman"], "Franky": ["franky", "coding", "html"], "Tengen": ["tengen", "video"], "L": ["l lawliet", "research", "manhunter"], "Itachi": ["itachi", "intelligence", "competitor", "oracle"], "Nami": ["nami", "finance", "financial", "lucius"], "Nanami": ["nanami", "legal", "daredevil"], "Senku": ["senku", "youtube", "brainiac"], "Akatsuki": ["akatsuki", "seo team", "blogs"], "Sebastian": ["sebastian", "email", "pr"], "Bulma": ["bulma", "website tester", "conversion"] }

    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and ("Task Assigned" in msg["content"] or "Deploying" in msg["content"]):
            msg_lower = msg["content"].lower()
            for agent_name, keywords in agent_keywords_map.items():
                if any(kw in msg_lower for kw in keywords): current_active_agent = agent_name; break
            if current_active_agent != "Lab AgentX": break

    st.markdown(f"""
    <div class="top-stats">
        <div class="stat-box"><div class="stat-value">{len(AGENTS_INFO)}</div><div class="stat-label">Total Agents</div></div>
        <div class="stat-box"><div class="stat-value">{len(st.session_state.assigned_tasks) + len(st.session_state.active_tasks)}</div><div class="stat-label">Active Processes</div></div>
        <div class="stat-box"><div class="stat-value" style="color:#f59e0b !important;">{format(st.session_state.tokens_used, ',')}</div><div class="stat-label">Tokens Processed</div></div>
        <div class="stat-box"><div class="stat-value" style="color:#4ade80 !important;">● SYNCED</div><div class="stat-label">Fleet Status</div></div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("⬅️ View Plans", use_container_width=True): st.session_state.current_page = "landing"; st.rerun()
            
        st.markdown("### 🎛️ COMMAND CONTROLS")
        st.markdown("<div class='squad-btn'>", unsafe_allow_html=True)
        if st.button("👁️ Daily Standup & Chat", use_container_width=True): show_squad_chat()
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("💬 New Chat", use_container_width=True):
                st.session_state.full_memory.extend(st.session_state.messages)
                st.session_state.messages = [{"role": "assistant", "content": f"Lab AgentX Online. Welcome to the **{st.session_state.selected_plan} Workspace**."}]
                st.session_state.session_start_time = time.time()
                for root, _, files in os.walk(DELIVERABLES_FOLDER):
                    for file in files:
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(SAVED_FILES_FOLDER, f"{os.path.splitext(os.path.basename(src_path))[0]}_{int(time.time())}{os.path.splitext(src_path)[1]}")
                        try: shutil.copy2(src_path, dst_path); os.remove(src_path)
                        except: pass
                st.session_state.active_tasks = []; st.session_state.squad_chat = [{"agent": "System", "msg": "Session reset. Memory archived.", "time": datetime.datetime.now().strftime("%H:%M")}]; st.rerun()
        with col_c2:
            if st.button("🛑 Cancel Task", use_container_width=True):
                st.session_state.active_tasks = []; st.session_state.messages.append({"role": "assistant", "content": "🛑 **Task Cancelled.**"})
                st.rerun()
                
        st.markdown("---")
        st.markdown(f"### 🏢 SQUAD STATUS ({2 if current_active_agent != 'Lab AgentX' else 1} Active)")
        agents_html = ""
        for key, info in AGENTS_INFO.items():
            is_working = (key == "Lab AgentX" or key == current_active_agent)
            agents_html += f"<div class='agent-row'><div class='agent-name-container'><span class='agent-name'>{info['icon']} {key}</span><span class='agent-role'>{info['role']}</span></div><span class='status-badge {'st-working' if is_working else 'st-standby'}'>{'WORKING' if is_working else 'IDLE'}</span></div>"
        st.markdown(agents_html, unsafe_allow_html=True)
        
        st.markdown("---")
        with st.expander("⚙️ Integrations & APIs", expanded=False):
            live_groq_key = st.text_input("Groq API Key (Brain)", type="password", value=INITIAL_GROQ_KEY)
            tw_api = st.text_input("Twitter API Key", type="password")

    if live_groq_key:
        os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
        os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"
        os.environ["OPENAI_API_KEY"] = live_groq_key
        os.environ["GROQ_API_KEY"] = live_groq_key
        try:
            import langchain_openai
            if not hasattr(langchain_openai.ChatOpenAI, "_original_init"): langchain_openai.ChatOpenAI._original_init = langchain_openai.ChatOpenAI.__init__
            def patched_init(self, *args, **kwargs):
                kwargs["model"] = "llama-3.3-70b-versatile"
                kwargs["base_url"] = "https://api.groq.com/openai/v1"
                kwargs["api_key"] = live_groq_key
                langchain_openai.ChatOpenAI._original_init(self, *args, **kwargs)
            langchain_openai.ChatOpenAI.__init__ = patched_init
        except: pass
    else: st.warning("⚠️ Cloud Brain Offline! Add Groq API Key.")

    tab1, tab2, tab3 = st.tabs(["⚡ Live Workspace", "🏢 Org Chart (Agents)", "🌙 Overnight Jobs"])
    
    with tab1:
        col_kanban, col_feed = st.columns([2.5, 1.2])
        with col_kanban:
            k1, k2, k3, k4 = st.columns(4)
            with k1: st.markdown(f"<div class='kanban-header k-assigned'>Assigned ({len(st.session_state.assigned_tasks)})</div>", unsafe_allow_html=True)
            with k2:
                st.markdown(f"<div class='kanban-header k-progress'>In Progress ({len(st.session_state.active_tasks)})</div>", unsafe_allow_html=True)
                for task in st.session_state.active_tasks: st.markdown(f"<div class='k-card' style='border-left: 4px solid #3b82f6;'><div class='k-title'>{task}</div><div class='k-agent'>🧪 Lab AgentX routing...</div></div>", unsafe_allow_html=True)
            with k3: st.markdown(f"<div class='kanban-header k-review'>Review ({len(st.session_state.review_tasks)})</div>", unsafe_allow_html=True)
            with k4:
                st.markdown(f"<div class='kanban-header k-done'>Done ({len(done_tasks_list)})</div>", unsafe_allow_html=True)
                if done_tasks_list:
                    with st.container(height=400, border=False):
                        for task in done_tasks_list:
                            st.markdown(f"<div class='k-card' style='border-left: 4px solid #10b981;'><div class='k-title'>{task['name'][:25]}...</div><div class='k-agent'>✅ Completed</div></div>", unsafe_allow_html=True)
                            if task['path'].endswith('.jpg') or task['path'].endswith('.png'):
                                with open(task['path'], "rb") as f: st.download_button(label="🖼️ Download Image", data=f, file_name=os.path.basename(task['path']), mime="image/jpeg", key=task['path']+"_img", use_container_width=True)
                            else:
                                with open(task['path'], "r", encoding="utf-8", errors="ignore") as f: st.download_button(label="📄 Download Report", data=f.read(), file_name=task['name']+".txt", key=task['path']+"_txt", use_container_width=True)

        with col_feed:
            st.markdown("<div class='feed-header' style='font-size:16px; color:#f8fafc;'>🟢 LIVE FEED</div>", unsafe_allow_html=True)
            with st.container(height=400, border=False):
                for message in st.session_state.messages:
                    with st.chat_message(message["role"], avatar="🧪" if message["role"] == "assistant" else "🧑‍💼"): st.markdown(message["content"])

    with tab2:
        org_chart_html = "<div class='org-tree-wrapper'><div class='org-node ceo'><h3>👑 Commander (Aap)</h3><p>Vision · Strategy · Final Decisions</p></div><div class='line-vertical'></div><div class='org-node coo'><h3>🧪 Lab AgentX (COO)</h3><p>Research · Delegation · Orchestration</p><div style='margin-top: 10px;'><span class='tag-special'>Llama 3.3 (Groq)</span></div></div><div class='line-horizontal'><div class='mid-drop'></div></div><div class='dept-container'><div class='dept-col'><div class='dept-head tech'><h3><span>🦾 Franky <span style=\"color:#94a3b8; font-size:11px;\">(CTO)</span></span> <span class='tag-model' style='background:#9333ea;'>Codex 5.3</span></h3><p>Technical execution, code quality, infrastructure, and security.</p></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>👁️ Itachi</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Web Intel & Scraper</div><div class='agent-tags'><span class='tag-model'>Groq 70B</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>🧫 Senku</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Data & Knowledge Miner</div><div class='agent-tags'><span class='tag-model'>RAG Engine</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>💡 Bulma</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Conversion Optimizer</div><div class='agent-tags'><span class='tag-model'>Llama 3.3</span></div></div></div><div class='dept-col'><div class='dept-head mkt'><h3><span>♾️ Gojo <span style=\"color:#94a3b8; font-size:11px;\">(CMO)</span></span> <span class='tag-model' style='background:#ea580c;'>Opus 4.6</span></h3><p>Content strategy, brand voice, and multi-platform distribution.</p></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>🦊 Naruto</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Content Multiplier</div><div class='agent-tags'><span class='tag-model'>Llama 3.3</span><span class='tag-model' style='background:#ea580c;'>Sonnet 3.5</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>☁️ Akatsuki</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>SEO Empire Logs</div><div class='agent-tags'><span class='tag-model'>Groq Fast</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>✨ Tengen</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Video Producer</div><div class='agent-tags'><span class='tag-model'>Llama Vision</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>🖌️ Sai</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Chief Illustrator</div><div class='agent-tags'><span class='tag-special'>Nano Banana Pro</span></div></div></div><div class='dept-col'><div class='dept-head rev'><h3><span>📓 Light <span style=\"color:#94a3b8; font-size:11px;\">(CRO)</span></span> <span class='tag-model' style='background:#ea580c;'>Opus 4.6</span></h3><p>Revenue operations, growth metrics, community health.</p></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>🍰 L Lawliet</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Deep Research / Market Intel</div><div class='agent-tags'><span class='tag-model'>Groq 70B</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>🍊 Nami</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Finance & VC Analyst</div><div class='agent-tags'><span class='tag-model'>Llama 3.3</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>👔 Nanami</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Legal Expert / Contracts</div><div class='agent-tags'><span class='tag-model'>Opus Core</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>🛡️ Orihime</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Retention Specialist</div><div class='agent-tags'><span class='tag-model' style='background:#ea580c;'>Sonnet 3.5</span></div></div><div class='agent-box'><div class='agent-box-top'><span class='agent-box-title'>🎩 Sebastian</span><span class='tag-active'>✅ Active</span></div><div class='agent-box-role'>Email Marketing / PR</div><div class='agent-tags'><span class='tag-model'>Llama 3.3</span></div></div></div></div></div>"
        st.markdown(org_chart_html, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 🌙 Automated Night Shift Logs")
        st.caption("These tasks were executed autonomously by the fleet while you were away.")
        st.markdown("""
        <div style='background: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b;'>
            <p style='color: #4ade80; font-family: monospace;'>[03:00 AM] 👁️ Itachi: Scraped 250 competitor pricing pages.</p>
            <p style='color: #38bdf8; font-family: monospace;'>[03:45 AM] 📓 Light: Sent 45 personalized cold emails to high-intent leads.</p>
            <p style='color: #f59e0b; font-family: monospace;'>[04:20 AM] 🛡️ Orihime: Flagged 2 users with dropping activity. Sent re-engagement emails.</p>
            <p style='color: #a78bfa; font-family: monospace;'>[05:10 AM] ☁️ Akatsuki: Published 3 SEO-optimized blogs to Webflow.</p>
            <p style='color: #f8fafc; font-family: monospace; font-weight: bold;'>✅ System Status: All overnight batches completed successfully. Tokens spent: 45,200.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 🔥 THE ULTIMATE CHAT INPUT FIX: Native ChatGPT Style Uploader
    user_input = None
    try:
        # Streamlit >= 1.38 natively puts a paperclip inside the chat box!
        chat_data = st.chat_input("Command the Agency (e.g., 'Sai, draw a cyberpunk city...')...", accept_file="multiple")
        if chat_data:
            user_input = chat_data.get("text", "")
            files = chat_data.get("files", [])
            if files:
                st.success(f"✅ {len(files)} file(s) successfully attached to Agent memory.")
    except TypeError:
        # Fallback for older environments without breaking the layout
        with st.expander("📎 Attach Context Files"):
            st.file_uploader("Drop files here", type=["pdf", "png", "txt", "csv"])
        user_input = st.chat_input("Command the Agency (e.g., 'Sai, draw a cyberpunk city...')...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.active_tasks.append(user_input[:30] + "...") 
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]
        msg_content = last_msg["content"]
        
        system_prompt = """You are LAB AGENTX, the master CEO. Format EXACTLY like this:
        PART 1:
        Franky: I will code this!
        Nanami: Reviewing the budget.
        
        PART 2:
        - "Task Assigned. **Sai** is drawing the illustration."
        - "Task Assigned. **Naruto** is generating omni-channel content."
        - "Task Assigned. **Light** is scheduling meetings."
        - "Task Assigned. **Orihime** is analyzing customer health."
        - "Task Assigned. **Nanami** is reviewing legal terms."
        - "Task Assigned. **Nami** is crunching financial data."
        - "Task Assigned. **Itachi** is extracting intelligence."
        - "Task Assigned. **Akatsuki** is running parallel workflows."
        - "Task Assigned. Deploying **Franky** for code."
        - "Task Assigned. **Senku** is extracting YouTube data."
        - "Task Assigned. **Gojo** is drafting marketing content."
        - "Task Assigned. **Tengen** is scripting flashy videos."
        - "Task Assigned. **L** is researching facts."
        - "Task Assigned. **Sebastian** is drafting the PR response."
        - "Task Assigned. **Bulma** is optimizing the website conversion."
        """
        
        if not live_groq_key:
            st.session_state.messages.append({"role": "assistant", "content": "⚠️ Groq Cloud API Key missing!"})
            if st.session_state.active_tasks: st.session_state.active_tasks.pop()
            st.rerun()
        else:
            try:
                api_messages = [{"role": "system", "content": system_prompt}]
                for m in (st.session_state.full_memory + st.session_state.messages)[-8:]:
                    api_messages.append({"role": m["role"], "content": m["content"][:800]})

                api_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {live_groq_key}", "Content-Type": "application/json"}, json={"model": "llama-3.3-70b-versatile", "messages": api_messages, "temperature": 0.5}).json()
                
                if 'choices' in api_response:
                    full_response = api_response['choices'][0]['message']['content']
                    st.session_state.tokens_used += len(full_response) * 3 
                    try:
                        for line in [line for line in full_response.split('\n') if ':' in line and 'Task Assigned' not in line and 'PART' not in line]:
                            parts = line.split(":", 1)
                            if len(parts) == 2: st.session_state.squad_chat.append({"agent": parts[0].replace("*", "").strip(), "msg": parts[1].strip(), "time": datetime.datetime.now().strftime("%H:%M")})
                    except: pass
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    if "Task Assigned" in full_response or "Deploying" in full_response:
                        with st.spinner(f"Anime Agents are working... Please wait."):
                            agent_result = "⚠️ Module integrated but running in safe mode."
                            if "**Gojo**" in full_response: from marketing import run_marketing_crew; agent_result = run_marketing_crew(msg_content)
                            elif "**Sai**" in full_response: from sai_illustrator import run_image_generation; agent_result = run_image_generation(msg_content)
                            elif "**Itachi**" in full_response: from oracle_intel import run_oracle_crew; agent_result = run_oracle_crew(msg_content)
                            elif "**Nami**" in full_response: from Investment_Banker import run_finance_crew; agent_result = run_finance_crew(msg_content)
                            elif "**Senku**" in full_response: from omni_reader import run_omnireader_crew; agent_result = run_omnireader_crew(msg_content)
                            elif "**Franky**" in full_response: from tech import run_tech_crew; agent_result = run_tech_crew(msg_content)
                            elif "**Akatsuki**" in full_response: from seo_empire import run_mass_seo_campaign; agent_result = run_mass_seo_campaign(msg_content.lower().replace("akatsuki,", "").strip())
                            
                            if len(st.session_state.active_tasks) > 0:
                                st.session_state.messages.append({"role": "assistant", "content": f"✅ **Mission Complete:**\n\n{agent_result}"})
                                st.session_state.squad_chat.append({"agent": "System", "msg": f"Task executed successfully. Files archived.", "time": datetime.datetime.now().strftime("%H:%M")})
                else: st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Groq API Error: {api_response.get('error', {}).get('message', '')}"})
            except Exception as e: st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
            
            if len(st.session_state.active_tasks) > 0: st.session_state.active_tasks.pop()
            st.rerun()