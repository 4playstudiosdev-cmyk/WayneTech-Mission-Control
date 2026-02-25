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

# 🧠 PAGE ROUTING SYSTEM (landing -> checkout -> dashboard)
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"
if "selected_plan" not in st.session_state:
    st.session_state.selected_plan = None
if "plan_price" not in st.session_state:
    st.session_state.plan_price = 0.0

def go_to_checkout(plan_name, price):
    st.session_state.selected_plan = plan_name
    st.session_state.plan_price = price
    st.session_state.current_page = "checkout"

def go_to_dashboard():
    st.session_state.current_page = "dashboard"

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
            background: rgba(15, 23, 42, 0.6) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            padding: 1.5rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px);
            height: 100%;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-5px);
            border-color: rgba(56, 189, 248, 0.4) !important;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4) !important;
            background: rgba(30, 41, 59, 0.8) !important;
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
    
    <div class="custom-navbar">
        <div class="nav-brand">🧪 Lab AgentX</div>
        <div class="nav-links">Sign In →</div>
    </div>
    
    <div class="hero-section">
        <div class="badge">🚀 VERSION 2.0 LIVE</div>
        <div class="hero-title">Hire The Ultimate AI Squad.<br><span>Automate Everything.</span></div>
        <div class="hero-subtitle">Stop relying on boring tools. Lab AgentX replaces your entire team. Access 14 super-intelligent anime agents for Marketing, Sales, Tech, and Research working 24/7.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>14+</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Elite AI Agents</p>", unsafe_allow_html=True)
    with c2: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>24/7</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Non-stop Execution</p>", unsafe_allow_html=True)
    with c3: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>10x</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Faster Delivery</p>", unsafe_allow_html=True)
    with c4: st.markdown("<h2 style='text-align:center; color:#38bdf8; margin:0;'>0%</h2><p style='text-align:center; color:#94a3b8; font-size: 14px;'>Human Error</p>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>⚙️ How It <span>Works</span></div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True): st.markdown("<h1 style='color:#38bdf8; margin-top:0;'>01</h1><h3 style='margin-bottom:10px;'>Give Commands</h3><p style='color:#94a3b8; font-size:14px; line-height:1.6;'>Just write your task in simple English. Lab AgentX automatically understands which department to assign.</p>", unsafe_allow_html=True)
    with f2:
        with st.container(border=True): st.markdown("<h1 style='color:#38bdf8; margin-top:0;'>02</h1><h3 style='margin-bottom:10px;'>Squad Execution</h3><p style='color:#94a3b8; font-size:14px; line-height:1.6;'>Agents collaborate. Franky writes code, Gojo handles marketing, and Itachi scrapes competitor data.</p>", unsafe_allow_html=True)
    with f3:
        with st.container(border=True): st.markdown("<h1 style='color:#38bdf8; margin-top:0;'>03</h1><h3 style='margin-bottom:10px;'>Download Result</h3><p style='color:#94a3b8; font-size:14px; line-height:1.6;'>In a matter of seconds, your work is completed and ready to download as a VIP Markdown report or code file.</p>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>💎 Choose Your <span>Plan</span></div>", unsafe_allow_html=True)
    
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        with st.container(border=True):
            st.markdown("<h3 style='margin-bottom:0;'>Starter</h3>", unsafe_allow_html=True)
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$19<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:13px; border-bottom:1px solid #334155; padding-bottom:15px; margin-bottom:15px;'>Best for solopreneurs.</p>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 5 AI Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Content Multiplier<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Deep Research<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Standard Dashboard</div>", unsafe_allow_html=True)
            if st.button("Start Free Trial", key="btn1", use_container_width=True): go_to_checkout("Starter", 19.99); st.rerun()

    with p2:
        with st.container(border=True):
            st.markdown("<h3 style='margin-bottom:0;'>Growth</h3>", unsafe_allow_html=True)
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$39<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:13px; border-bottom:1px solid #334155; padding-bottom:15px; margin-bottom:15px;'>Scale your startup quickly.</p>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 10 AI Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Sales Outreach<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> SEO Empire<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Finance Analyst</div>", unsafe_allow_html=True)
            if st.button("Get Growth", key="btn2", use_container_width=True): go_to_checkout("Growth", 39.99); st.rerun()

    with p3:
        with st.container(border=True):
            st.markdown("<div style='background:linear-gradient(135deg, #38bdf8, #818cf8); color:white; padding:3px 10px; border-radius:20px; font-size:10px; display:inline-block; font-weight:bold; margin-bottom:5px;'>MOST POPULAR</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-bottom:0; color:#38bdf8;'>Elite Agency</h3>", unsafe_allow_html=True)
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$54<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:13px; border-bottom:1px solid #334155; padding-bottom:15px; margin-bottom:15px;'>Full agency power in your hands.</p>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 16 Premium AI Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Image Generation<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Tech Dev Team<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Legal Audits</div>", unsafe_allow_html=True)
            if st.button("Get Elite Access", key="btn3", use_container_width=True): go_to_checkout("Elite Agency", 54.99); st.rerun()

    with p4:
        with st.container(border=True):
            st.markdown("<h3 style='margin-bottom:0;'>Enterprise</h3>", unsafe_allow_html=True)
            st.markdown("<h1 style='font-size:2.8rem; margin:10px 0;'>$89<span style='font-size:1rem; color:#94a3b8;'>.99/mo</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:13px; border-bottom:1px solid #334155; padding-bottom:15px; margin-bottom:15px;'>Custom automation for big teams.</p>", unsafe_allow_html=True)
            st.markdown("<div style='color:#cbd5e1; font-size:13px; line-height:2.2; min-height: 140px;'><span style='color:#38bdf8; font-weight:bold;'>✓</span> 25+ AI Agents<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> Custom Character Bots<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> White-label Workspace<br><span style='color:#38bdf8; font-weight:bold;'>✓</span> 1-on-1 Onboarding</div>", unsafe_allow_html=True)
            if st.button("Contact Sales", key="btn4", use_container_width=True): go_to_checkout("Enterprise", 89.99); st.rerun()

    st.markdown("<div class='footer'>Backed by Groq Technology ⚡ • © 2026 Lab AgentX | Built for Scale</div>", unsafe_allow_html=True)

# ==========================================
# 💳 CHECKOUT & AUTHENTICATION PAGE
# ==========================================
elif st.session_state.current_page == "checkout":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        header[data-testid="stHeader"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        .stApp { background-color: #020617; font-family: 'Plus Jakarta Sans', sans-serif; color: white; }
        .block-container { max-width: 600px !important; padding-top: 4rem !important; }
        
        /* Payment styling */
        .auth-card { background: #0f172a; padding: 3rem; border-radius: 20px; border: 1px solid #1e293b; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
        .auth-title { font-size: 24px; font-weight: 800; color: #f8fafc; margin-bottom: 5px; text-align: center; }
        .auth-sub { color: #94a3b8; text-align: center; margin-bottom: 30px; font-size: 14px; }
        .price-tag { font-size: 36px; font-weight: 800; color: #38bdf8; text-align: center; margin-bottom: 30px; }
        
        div[data-testid="stTextInput"] input { background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 8px; }
        
        div[data-testid="stButton"] > button { width: 100%; border-radius: 8px !important; padding: 12px 0 !important; font-weight: 700 !important; background: #38bdf8 !important; color: #0f172a !important; border: none !important; transition: all 0.3s ease !important; }
        div[data-testid="stButton"] > button:hover { background: #0ea5e9 !important; transform: translateY(-2px) !important; }
        
        /* Cancel Button override */
        .cancel-btn div[data-testid="stButton"] > button { background: transparent !important; border: 1px solid #334155 !important; color: #94a3b8 !important; }
        .cancel-btn div[data-testid="stButton"] > button:hover { border-color: #f87171 !important; color: #f87171 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='auth-title'>Checkout: {st.session_state.selected_plan} Plan</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-sub'>Create your account and complete payment to access the workspace.</div>", unsafe_allow_html=True)
    
    # 💰 Dynamic Price display based on coupon
    if "final_price" not in st.session_state:
        st.session_state.final_price = st.session_state.plan_price
        
    st.markdown(f"<div class='price-tag'>Total: ${st.session_state.final_price:.2f}</div>", unsafe_allow_html=True)
    
    with st.form("checkout_form"):
        st.text_input("Full Name", placeholder="Bruce Wayne")
        st.text_input("Email Address", placeholder="bruce@wayneenterprises.com")
        st.text_input("Password", type="password", placeholder="••••••••")
        
        st.markdown("### Payment Method")
        payment_method = st.radio("Select Provider", ["Stripe (Credit/Debit Card)", "PayPal", "Easypaisa"], label_visibility="collapsed")
        
        coupon = st.text_input("Promo Code / Coupon", placeholder="Enter code here...")
        
        submit_btn = st.form_submit_button("Complete Payment & Launch Dashboard")
        
        if submit_btn:
            # 🎁 FUNDER VIP COUPON LOGIC
            if coupon.strip().upper() == "FUNDERVIP":
                st.success("🎉 VIP Coupon Applied! Payment bypassed. Loading workspace...")
                time.sleep(1)
                go_to_dashboard()
                st.rerun()
            elif st.session_state.final_price > 0:
                with st.spinner(f"Processing payment via {payment_method}..."):
                    time.sleep(2) # Simulating payment processing
                    st.success("✅ Payment successful! Setting up your AI Agency...")
                    time.sleep(1)
                    go_to_dashboard()
                    st.rerun()
            else:
                go_to_dashboard()
                st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='cancel-btn'>", unsafe_allow_html=True)
    if st.button("← Go Back"):
        st.session_state.current_page = "landing"
        st.session_state.final_price = st.session_state.plan_price # reset price
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 🧪 MAIN DASHBOARD (DARK VIBE WORKSPACE)
# ==========================================
elif st.session_state.current_page == "dashboard":

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp { background-color: #020617 !important; font-family: 'Plus Jakarta Sans', sans-serif; color: #f8fafc;}
        
        section[data-testid="stSidebar"] { display: block !important; background-color: #0f172a !important; border-right: 1px solid #1e293b !important; }
        button[data-testid="collapsedControl"] { display: block !important; }
        .block-container { padding-top: 3rem !important; max-width: 1400px !important; }
        
        /* Make all text in main container light */
        .stMarkdown, .stText, p, span, h1, h2, h3, h4, h5, h6 { color: #f8fafc !important; }
        
        .top-stats { 
            display: flex; justify-content: space-around; 
            background: #0f172a; 
            padding: 20px; border-radius: 16px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
            margin-bottom: 25px; border: 1px solid #1e293b; 
            flex-wrap: wrap; gap: 15px;
        }
        
        .stat-box { text-align: center; flex: 1; min-width: 120px; transition: transform 0.2s; } 
        .stat-box:hover { transform: translateY(-2px); }
        .stat-value { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: #f8fafc !important; } 
        .stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-top: 4px; color: #94a3b8 !important; }
        
        .kanban-header { font-size: 13px; font-weight: 800; color: #94a3b8 !important; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 3px solid #1e293b; text-transform: uppercase; letter-spacing: 1px; }
        .k-assigned { border-bottom-color: #f59e0b; } .k-progress { border-bottom-color: #3b82f6; } .k-review { border-bottom-color: #8b5cf6; } .k-done { border-bottom-color: #10b981; }
        
        .k-card { 
            background: #0f172a !important; border: 1px solid #1e293b; border-radius: 12px; 
            padding: 16px; margin-bottom: 14px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.2); 
            transition: all 0.2s ease; word-wrap: break-word;
        }
        .k-card:hover { border-color: #38bdf8; transform: translateY(-2px); }
        .k-title { font-size: 14px; font-weight: 700; margin-bottom: 8px; color: #f8fafc !important;} 
        .k-agent { font-size: 12px; color: #94a3b8 !important; display: flex; align-items: center; gap: 6px; font-weight: 600;} 
        
        /* Dashboard Agents List in Sidebar */
        .agent-row { 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 14px 12px; margin-bottom: 10px; border-radius: 12px; 
            background: #1e293b !important; 
            border: 1px solid #334155; cursor: pointer; 
            transition: all 0.2s ease; 
        }
        .agent-row:hover { border-color: #38bdf8; }
        .agent-name-container { display: flex; flex-direction: column; gap: 4px; }
        .agent-name, .agent-name * { font-size: 14px; font-weight: 800; display: flex; align-items: center; gap: 8px; color: #f8fafc !important; } 
        .agent-role { font-size: 10px; color: #94a3b8 !important; font-weight: 700; margin-left: 28px; text-transform: uppercase; letter-spacing: 0.5px;}
        
        .status-badge { font-size: 10px; padding: 4px 10px; border-radius: 20px; font-weight: 800; letter-spacing: 0.5px;}
        .st-working, .st-working * { background: rgba(34, 197, 94, 0.2) !important; color: #4ade80 !important; border: 1px solid #22c55e !important; box-shadow: 0 0 10px rgba(34, 197, 94, 0.2); } 
        .st-standby, .st-standby * { background: rgba(148, 163, 184, 0.1) !important; color: #94a3b8 !important; border: 1px solid #334155 !important; }
        
        /* Chat Feed Styling */
        .stChatMessage { background-color: #0f172a !important; border: 1px solid #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
        
        /* File Uploader overriding */
        div[data-testid="stFileUploader"] { background-color: #1e293b; padding: 10px; border-radius: 10px; border: 1px dashed #334155; }
        
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        
        @media (max-width: 768px) {
            .top-stats { flex-direction: column; gap: 5px; }
            .stat-box { width: 100%; border-bottom: 1px solid #1e293b; padding: 10px 0; }
            .stat-box:last-child { border-bottom: none; }
        }
    </style>
    """, unsafe_allow_html=True)

    AGENTS_INFO = {
        "Lab AgentX": {"name": "Lab AgentX", "role": "Squad Lead", "icon": "🧪", "desc": "The mastermind & eccentric CEO.", "stat": "System Commander"},
        "Sai": {"name": "Sai", "role": "Chief Illustrator", "icon": "🖌️", "desc": "Draws high-quality images & thumbnails.", "stat": "Visuals"},
        "Naruto": {"name": "Naruto Uzumaki", "role": "Multiplier", "icon": "🦊", "desc": "Turns 1 video into 20 posts.", "stat": "Omni-Channel"},
        "Light": {"name": "Light Yagami", "role": "Lead Booker", "icon": "📓", "desc": "Hunts leads and sends cold DMs.", "stat": "Sales"},
        "Orihime": {"name": "Orihime Inoue", "role": "Client Savior", "icon": "🛡️", "desc": "Heals client relations.", "stat": "Support"},
        "Gojo": {"name": "Satoru Gojo", "role": "Marketing Head", "icon": "♾️", "desc": "Limitless ad strategies.", "stat": "Marketing"},
        "Franky": {"name": "Franky", "role": "Tech Lead", "icon": "🦾", "desc": "Compiles SUUPER Python/HTML code.", "stat": "Developer"},
        "Tengen": {"name": "Tengen Uzui", "role": "Video Producer", "icon": "✨", "desc": "Flashy viral video scripts.", "stat": "Media"},
        "L": {"name": "L Lawliet", "role": "Deep Research", "icon": "🍰", "desc": "Ultimate web detective.", "stat": "Intel"},
        "Itachi": {"name": "Itachi Uchiha", "role": "Web Intel", "icon": "👁️", "desc": "Spies on competitor websites.", "stat": "Scraper"},
        "Nami": {"name": "Nami", "role": "Finance Analyst", "icon": "🍊", "desc": "Crunches VC data and stocks.", "stat": "Wall St"},
        "Nanami": {"name": "Kento Nanami", "role": "Legal Expert", "icon": "👔", "desc": "Reviews dense contracts.", "stat": "Lawyer"},
        "Senku": {"name": "Senku Ishigami", "role": "Data Miner", "icon": "🧫", "desc": "Summarizes YouTube transcripts.", "stat": "Knowledge"},
        "Akatsuki": {"name": "The Akatsuki", "role": "SEO Empire", "icon": "☁️", "desc": "Mass SEO blogs generator.", "stat": "Blogger"}
    }

    MEMORY_FOLDER = "memory_logs"
    UPLOAD_FOLDER = "uploads"
    DELIVERABLES_FOLDER = "Deliverables"
    SAVED_FILES_FOLDER = "Saved_Files" 

    for folder in [MEMORY_FOLDER, UPLOAD_FOLDER, DELIVERABLES_FOLDER, SAVED_FILES_FOLDER]:
        if not os.path.exists(folder): os.makedirs(folder)

    # 🧠 STATE-BASED FILE HIDING LOGIC
    def get_all_deliverables():
        files = []
        for root, _, filenames in os.walk(DELIVERABLES_FOLDER):
            for fname in filenames:
                files.append(os.path.normpath(os.path.join(root, fname)))
        return set(files)

    if "hidden_files" not in st.session_state: 
        st.session_state.hidden_files = get_all_deliverables()

    if "session_start_time" not in st.session_state: 
        st.session_state.session_start_time = time.time() - 5

    if "full_memory" not in st.session_state: st.session_state.full_memory = []
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": f"Lab AgentX Online. Welcome to the **{st.session_state.selected_plan} Workspace**. Your elite squad is ready. What's the mission?"}]
    if "active_tasks" not in st.session_state: st.session_state.active_tasks = []
    if "assigned_tasks" not in st.session_state: st.session_state.assigned_tasks = []
    if "review_tasks" not in st.session_state: st.session_state.review_tasks = []

    def get_done_tasks():
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
                except Exception:
                    pass
        return sorted(tasks, key=lambda x: x['time'], reverse=True)[:50]

    done_tasks_list = get_done_tasks()

    current_active_agent = "Lab AgentX"
    agent_keywords_map = {
        "Sai": ["sai", "draw", "image", "illustrate", "thumbnail", "picture", "art", "generate image", "paint"],
        "Naruto": ["naruto", "multiplier", "omni-channel"],
        "Light": ["light", "leadbooker", "booking", "sales"],
        "Orihime": ["orihime", "retentionbot", "churn"],
        "Gojo": ["gojo", "marketing", "superman"],
        "Franky": ["franky", "coding", "html", "cyborg", "deploying franky"],
        "Tengen": ["tengen", "video", "lantern"],
        "L": ["l lawliet", "research", "manhunter"],
        "Itachi": ["itachi", "intelligence", "competitor", "oracle"],
        "Nami": ["nami", "finance", "financial", "lucius"],
        "Nanami": ["nanami", "legal", "daredevil"],
        "Senku": ["senku", "youtube", "brainiac"],
        "Akatsuki": ["akatsuki", "seo team", "blogs"]
    }

    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and ("Task Assigned" in msg["content"] or "Deploying" in msg["content"]):
            msg_lower = msg["content"].lower()
            for agent_name, keywords in agent_keywords_map.items():
                if any(kw in msg_lower for kw in keywords):
                    current_active_agent = agent_name
                    break
            if current_active_agent != "Lab AgentX": break

    total_agents = len(AGENTS_INFO)
    working_agents_count = 2 if current_active_agent != "Lab AgentX" else 1 
    tasks_in_queue = len(st.session_state.assigned_tasks) + len(st.session_state.active_tasks) + len(st.session_state.review_tasks)

    st.markdown(f"""
    <div class="top-stats">
        <div class="stat-box"><div class="stat-value">{total_agents}</div><div class="stat-label">Total Agents</div></div>
        <div class="stat-box"><div class="stat-value">{tasks_in_queue}</div><div class="stat-label">Tasks in Queue</div></div>
        <div class="stat-box"><div class="stat-value" style="color:#3b82f6 !important;">{current_active_agent}</div><div class="stat-label">Filtering By</div></div>
        <div class="stat-box"><div class="stat-value" style="color:#4ade80 !important;">● CLOUD HOSTED</div><div class="stat-label">System Status</div></div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("⬅️ Back to Plans", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()
            
        st.markdown("### 🎛️ COMMAND CONTROLS")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("💬 New Chat", use_container_width=True):
                st.session_state.full_memory.extend(st.session_state.messages)
                st.session_state.messages = [{"role": "assistant", "content": "Lab AgentX Online. Memory archived. Ready for the next mission."}]
                st.session_state.session_start_time = time.time()
                for root, _, files in os.walk(DELIVERABLES_FOLDER):
                    for file in files:
                        src_path = os.path.join(root, file)
                        base, ext = os.path.splitext(os.path.basename(src_path))
                        new_filename = f"{base}_{int(time.time())}{ext}"
                        dst_path = os.path.join(SAVED_FILES_FOLDER, new_filename)
                        try:
                            shutil.copy2(src_path, dst_path)
                            os.remove(src_path)
                        except Exception:
                            pass
                st.session_state.active_tasks = []
                st.rerun()
                
        with col_c2:
            if st.button("🛑 Cancel Task", use_container_width=True):
                st.session_state.active_tasks = []
                st.session_state.messages.append({"role": "assistant", "content": "🛑 **Task Cancelled.** The squad is standing down."})
                st.rerun()
                
        # 🐛 THE FILE UPLOADER FIX: Moved to sidebar to prevent Chat Input layout breaking!
        st.markdown("---")
        st.markdown("### 📁 KNOWLEDGE BASE")
        st.caption("Upload documents for AI context")
        uploaded_file = st.file_uploader("Upload Docs", type=["pdf", "png", "txt", "csv"], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"{uploaded_file.name} loaded.")
                
        st.markdown("---")
        st.markdown(f"### 🏢 SQUAD STATUS ({working_agents_count} Active)")
        agents_html = ""
        for key, info in AGENTS_INFO.items():
            is_working = (key == "Lab AgentX" or key == current_active_agent)
            status_class = "st-working" if is_working else "st-standby"
            status_text = "WORKING" if is_working else "STANDBY"
            
            agents_html += f"""
            <div class='agent-row' title='{info['desc']} (Specialty: {info['stat']})'>
                <div class='agent-name-container'>
                    <span class='agent-name'>{info['icon']} {key}</span>
                    <span class='agent-role'>{info['role']}</span>
                </div>
                <span class='status-badge {status_class}'>{status_text}</span>
            </div>
            """
        st.markdown(agents_html, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔗 INTEGRATIONS")
        with st.expander("⚙️ Connect APIs (REQUIRED)", expanded=False):
            st.caption("Add your AI and Social API Keys here.")
            live_groq_key = st.text_input("Groq API Key (For AI Brain)", type="password", value=INITIAL_GROQ_KEY)
            tw_api = st.text_input("Twitter API Key", type="password")
            li_tok = st.text_input("LinkedIn Access Token", type="password")

        st.markdown("---")
        st.markdown("### 🗃️ SAVED FILES")
        saved_files = []
        for root, _, files in os.walk(SAVED_FILES_FOLDER):
            for file in files:
                saved_files.append(os.path.join(root, file))
                
        if saved_files:
            with st.expander(f"Archived Tasks ({len(saved_files)})", expanded=False):
                try:
                    saved_files.sort(key=os.path.getmtime, reverse=True)
                except:
                    pass
                for sf in saved_files:
                    fname = os.path.basename(sf)
                    display_name = fname.replace(".md", "").replace(".txt", "").replace(".jpg", "")[:25] + "..."
                    
                    if sf.endswith('.jpg') or sf.endswith('.png'):
                        with open(sf, "rb") as f:
                            st.download_button(label=f"🖼️ {display_name}", data=f, file_name=fname, mime="image/jpeg", key=sf+"_saved")
                    else:
                        with open(sf, "r", encoding="utf-8", errors="ignore") as f: file_content = f.read()
                        st.download_button(label=f"📄 {display_name}", data=file_content, file_name=fname, key=sf+"_saved")
        else:
            st.caption("No saved files yet. Click 'New Chat' to archive current tasks.")

    if live_groq_key:
        os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
        os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"
        os.environ["OPENAI_API_KEY"] = live_groq_key
        os.environ["GROQ_API_KEY"] = live_groq_key
        
        try:
            import langchain_openai
            if not hasattr(langchain_openai.ChatOpenAI, "_original_init"):
                langchain_openai.ChatOpenAI._original_init = langchain_openai.ChatOpenAI.__init__

            def patched_init(self, *args, **kwargs):
                kwargs["model"] = "llama-3.3-70b-versatile"
                kwargs["base_url"] = "https://api.groq.com/openai/v1"
                kwargs["api_key"] = live_groq_key
                langchain_openai.ChatOpenAI._original_init(self, *args, **kwargs)

            langchain_openai.ChatOpenAI.__init__ = patched_init
        except Exception:
            pass
    else:
        st.warning("⚠️ Cloud Brain Offline! Add Groq API Key in the integrations tab.")

    col_kanban, col_feed = st.columns([2.5, 1.2])

    with col_kanban:
        st.markdown("### 📋 TASK TRACKER")
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f"<div class='kanban-header k-assigned'>Assigned ({len(st.session_state.assigned_tasks)})</div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='kanban-header k-progress'>In Progress ({len(st.session_state.active_tasks)})</div>", unsafe_allow_html=True)
            for task in st.session_state.active_tasks:
                st.markdown(f"<div class='k-card' style='border-left: 4px solid #3b82f6;'><div class='k-title'>{task}</div><div class='k-agent'>🧪 Lab AgentX routing...</div></div>", unsafe_allow_html=True)
        with k3: st.markdown(f"<div class='kanban-header k-review'>Review ({len(st.session_state.review_tasks)})</div>", unsafe_allow_html=True)
        with k4:
            st.markdown(f"<div class='kanban-header k-done'>Done ({len(done_tasks_list)})</div>", unsafe_allow_html=True)
            if done_tasks_list:
                done_container = st.container(height=500, border=False)
                with done_container:
                    for task in done_tasks_list:
                        st.markdown(f"<div class='k-card' style='border-left: 4px solid #10b981;'><div class='k-title'>{task['name'][:25]}...</div><div class='k-agent'>✅ Completed</div></div>", unsafe_allow_html=True)
                        if task['path'].endswith('.jpg') or task['path'].endswith('.png'):
                            with open(task['path'], "rb") as f:
                                st.download_button(label="🖼️ Download Image", data=f, file_name=os.path.basename(task['path']), mime="image/jpeg", key=task['path']+"_img", use_container_width=True)
                        else:
                            with open(task['path'], "r", encoding="utf-8", errors="ignore") as f: file_content = f.read()
                            st.download_button(label="📄 Download Report", data=file_content, file_name=task['name']+".txt", key=task['path']+"_txt", use_container_width=True)

    with col_feed:
        st.markdown("<div class='feed-header'>🟢 LIVE FEED</div>", unsafe_allow_html=True)
        feed_container = st.container(height=500, border=False)
        with feed_container:
            for message in st.session_state.messages:
                avatar = "🧪" if message["role"] == "assistant" else "🧑‍💼"
                with st.chat_message(message["role"], avatar=avatar): st.markdown(message["content"])

    st.markdown("---")
    
    # 🐛 FIX: No extra columns, just pure chat input. File uploader is now in Sidebar!
    user_input = st.chat_input("Command the Agency (e.g., 'Sai, draw a cyberpunk city...')...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.active_tasks.append(user_input[:30] + "...") 
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]
        msg_content = last_msg["content"]
        
        system_prompt = """
        You are LAB AGENTX, the master CEO of an Anime-themed AI Agency.
        
        CRITICAL INSTRUCTION - READ CAREFULLY:
        1. YOU MUST NEVER DO THE TASK YOURSELF. Do NOT write plans, strategies, blogs, or codes.
        
        2. Your response MUST consist of EXACTLY TWO PARTS:
        
           PART 1 (The Banter): Write 1 or 2 funny sentences where your agents playfully argue or react to the task in character before you assign it. 
           Use character names like **Franky**, **Gojo**, **Nanami**, **Senku**, **Naruto**, etc. 
           Example: "Franky: SUUPER! I will code this in 2 seconds! 🦾 | Nanami: Please keep the noise down, I am reviewing contracts. 👔"
           
           PART 2 (The Routing): On a new line, output EXACTLY ONE SENTENCE from the routing list below.
        
        ROUTING LIST:
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

        If the user just says "hi", you may explain your role gracefully without routing. But if a task is given, strictly follow PART 1 and PART 2.
        """
        
        if not live_groq_key:
            full_response = "⚠️ Lab AgentX Error: Groq Cloud API Key missing! Please add it in the sidebar integrations tab."
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            if st.session_state.active_tasks: st.session_state.active_tasks.pop()
            st.rerun()
        else:
            try:
                api_messages = [{"role": "system", "content": system_prompt}]
                
                all_context = st.session_state.full_memory + st.session_state.messages
                for m in all_context[-8:]:
                    content_str = m["content"]
                    if len(content_str) > 800:
                        content_str = content_str[:800] + "... [Content truncated for memory]"
                    api_messages.append({"role": m["role"], "content": content_str})

                headers = {"Authorization": f"Bearer {live_groq_key}", "Content-Type": "application/json"}
                payload = {"model": "llama-3.3-70b-versatile", "messages": api_messages, "temperature": 0.5}
                
                api_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                
                if 'choices' in api_response:
                    full_response = api_response['choices'][0]['message']['content']
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    if "Task Assigned" in full_response or "Deploying" in full_response:
                        with st.spinner(f"Anime Agents are arguing and working... Please wait."):
                            agent_result = "⚠️ Agent not fully integrated for cloud yet."
                            
                            if "**Gojo**" in full_response:
                                from marketing import run_marketing_crew
                                agent_result = run_marketing_crew(msg_content)
                            elif "**Sai**" in full_response:
                                from sai_illustrator import run_image_generation
                                agent_result = run_image_generation(msg_content)
                            elif "**Itachi**" in full_response:
                                from oracle_intel import run_oracle_crew
                                agent_result = run_oracle_crew(msg_content)
                            elif "**Nami**" in full_response:
                                from Investment_Banker import run_finance_crew
                                agent_result = run_finance_crew(msg_content)
                            elif "**Senku**" in full_response:
                                from omni_reader import run_omnireader_crew
                                agent_result = run_omnireader_crew(msg_content)
                            elif "**Franky**" in full_response:
                                from tech import run_tech_crew
                                agent_result = run_tech_crew(msg_content)
                            elif "**Akatsuki**" in full_response:
                                from seo_empire import run_mass_seo_campaign
                                clean_kw = msg_content.lower().replace("akatsuki,", "").replace("write seo blogs on:", "").replace("write seo blogs on", "").strip()
                                agent_result = run_mass_seo_campaign(clean_kw)
                            elif "**Naruto**" in full_response:
                                try:
                                    from content_multiplier import run_multiplier_crew
                                    agent_result = run_multiplier_crew(msg_content)
                                except: agent_result = "Multiplier dependencies missing on cloud."
                            
                            if len(st.session_state.active_tasks) > 0:
                                st.session_state.messages.append({"role": "assistant", "content": f"✅ **Mission Complete:**\n\n{agent_result}"})
                else:
                    error_details = api_response.get('error', {}).get('message', str(api_response))
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Groq API Error: {error_details}"})

            except Exception as e: 
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Connection Error: {str(e)}"})
            
            if len(st.session_state.active_tasks) > 0:
                st.session_state.active_tasks.pop()
            st.rerun()