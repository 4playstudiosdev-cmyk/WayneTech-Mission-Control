import streamlit as st
import requests
import datetime
import os
import glob
import time
import sys
import shutil 
from dotenv import load_dotenv

# --- FOLDER PATHS FIX FOR CLOUD ---
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

# 🧠 PAGE ROUTING SYSTEM (Landing Page vs Dashboard)
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

def go_to_dashboard():
    st.session_state.current_page = "dashboard"

# ==========================================
# 🌟 VIP SAAS LANDING PAGE (ISOLATED UI)
# ==========================================
if st.session_state.current_page == "landing":
    # 🛑 HIDE STREAMLIT ELEMENTS ENTIRELY FOR LANDING PAGE
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        header[data-testid="stHeader"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        button[data-testid="collapsedControl"] { display: none !important; }
        .block-container { padding-top: 0rem !important; max-width: 100% !important; padding-left: 0 !important; padding-right: 0 !important;}
        footer {display: none !important;}
        
        .stApp { background-color: #020617; font-family: 'Plus Jakarta Sans', sans-serif; color: white; background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 70%); }
        
        .custom-navbar { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; border-bottom: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px); }
        .nav-brand { font-size: 24px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px; }
        .nav-links { font-size: 14px; font-weight: 600; color: #94a3b8; cursor: pointer; }
        .nav-links:hover { color: #38bdf8; }
        
        .hero-section { text-align: center; padding: 6rem 2rem 4rem 2rem; max-width: 900px; margin: 0 auto; }
        .badge { background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 6px 16px; border-radius: 30px; font-size: 12px; font-weight: 700; letter-spacing: 1px; display: inline-block; margin-bottom: 20px; border: 1px solid rgba(56, 189, 248, 0.2); }
        .hero-title { font-size: 4.5rem; font-weight: 800; color: #f8fafc; margin-bottom: 1.5rem; line-height: 1.1; letter-spacing: -1px; }
        .hero-title span { background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-subtitle { font-size: 1.25rem; color: #94a3b8; max-width: 700px; margin: 0 auto 3rem auto; line-height: 1.6; }
        
        .pricing-wrapper { padding: 0 2rem 6rem 2rem; max-width: 1200px; margin: 0 auto; }
        .pricing-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 24px; }
        
        .pricing-card { background: rgba(30, 41, 59, 0.5); border-radius: 24px; padding: 2.5rem; border: 1px solid #334155; transition: all 0.3s ease; text-align: left; position: relative; backdrop-filter: blur(10px); }
        .pricing-card:hover { transform: translateY(-10px); border-color: #38bdf8; box-shadow: 0 20px 40px rgba(56, 189, 248, 0.1); background: rgba(30, 41, 59, 0.8); }
        
        .popular-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #38bdf8, #818cf8); color: #fff; font-size: 12px; font-weight: 800; padding: 6px 16px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(56,189,248,0.4); }
        
        .plan-name { font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 10px; }
        .plan-price { font-size: 3rem; font-weight: 800; color: #ffffff; margin-bottom: 5px; display: flex; align-items: baseline; gap: 5px; }
        .plan-price span { font-size: 1rem; color: #94a3b8; font-weight: 500; }
        .plan-desc { font-size: 0.95rem; color: #94a3b8; margin-bottom: 25px; border-bottom: 1px solid #334155; padding-bottom: 25px;}
        
        .feature-list { list-style: none; padding: 0; margin: 0 0 30px 0; }
        .feature-list li { font-size: 0.95rem; color: #cbd5e1; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
        .feature-list li::before { content: '✓'; color: #38bdf8; font-weight: 900; background: rgba(56,189,248,0.1); width: 20px; height: 20px; display: flex; justify-content: center; align-items: center; border-radius: 50%; font-size: 12px; }
        
        div[data-testid="stButton"] > button { width: 100%; border-radius: 12px; padding: 24px 0; font-weight: 700; background: #1e293b; color: #f8fafc; border: 1px solid #475569; transition: all 0.2s; font-size: 16px; }
        div[data-testid="stButton"] > button:hover { background: #f8fafc; color: #0f172a; border-color: #f8fafc; transform: scale(1.02); }
        
        .elite-btn div[data-testid="stButton"] > button { background: #38bdf8; color: #0f172a; border: none; }
        .elite-btn div[data-testid="stButton"] > button:hover { background: #0ea5e9; color: white; }
        
        @media (max-width: 768px) {
            .hero-title { font-size: 3rem; }
            .custom-navbar { padding: 20px; }
            .pricing-wrapper { padding: 0 1rem 4rem 1rem; }
        }
    </style>
    
    <div class="custom-navbar">
        <div class="nav-brand">🧪 Lab AgentX</div>
        <div class="nav-links">Sign In →</div>
    </div>
    
    <div class="hero-section">
        <div class="badge">🚀 VERSION 2.0 LIVE</div>
        <div class="hero-title">Hire an Elite AI Squad.<br><span>Automate Everything.</span></div>
        <div class="hero-subtitle">Stop paying expensive agencies. Lab AgentX replaces your Marketing, Sales, Tech, and Research departments with autonomous, hyper-intelligent anime agents working 24/7.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="pricing-wrapper">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="pricing-card">
            <div class="plan-name">Starter</div>
            <div class="plan-price">$19<span>.99/mo</span></div>
            <div class="plan-desc">Perfect for solopreneurs & creators.</div>
            <ul class="feature-list">
                <li>5 Autonomous AI Agents</li>
                <li>Content Multiplier (Naruto)</li>
                <li>Deep Research (L)</li>
                <li>Standard Dashboard</li>
                <li>Community Support</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.button("Start Free Trial", key="btn1"): go_to_dashboard(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="pricing-card">
            <div class="plan-name">Growth</div>
            <div class="plan-price">$39<span>.99/mo</span></div>
            <div class="plan-desc">For growing startups & small teams.</div>
            <ul class="feature-list">
                <li>10 Autonomous AI Agents</li>
                <li>Sales Outreach (Light)</li>
                <li>SEO Empire (Akatsuki)</li>
                <li>Finance Analyst (Nami)</li>
                <li>Priority Support</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.button("Get Growth", key="btn2"): go_to_dashboard(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="pricing-card" style="border-color: #38bdf8; background: rgba(30, 41, 59, 0.7);">
            <div class="popular-badge">Most Popular</div>
            <div class="plan-name" style="color: #38bdf8;">Elite Agency</div>
            <div class="plan-price">$54<span>.99/mo</span></div>
            <div class="plan-desc">Full agency power for serious businesses.</div>
            <ul class="feature-list">
                <li>16 Premium AI Agents</li>
                <li>Image Generation (Sai)</li>
                <li>Tech Dev Team (Franky)</li>
                <li>Legal Audits (Nanami)</li>
                <li>24/7 VIP Support</li>
            </ul>
        <div class="elite-btn">
        """, unsafe_allow_html=True)
        if st.button("Get Elite Access", key="btn3"): go_to_dashboard(); st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="pricing-card">
            <div class="plan-name">Enterprise</div>
            <div class="plan-price">$89<span>.99/mo</span></div>
            <div class="plan-desc">Custom automation for large scale operations.</div>
            <ul class="feature-list">
                <li>25+ AI Agents (Unlimited)</li>
                <li>Custom Character Bots</li>
                <li>Dedicated API Keys</li>
                <li>White-label Workspace</li>
                <li>1-on-1 Onboarding</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.button("Contact Sales", key="btn4"): go_to_dashboard(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown('</div><div style="text-align:center; padding: 2rem 0; color: #475569; font-size: 14px;">Backed by Groq Technology ⚡ • © 2026 Lab AgentX</div>', unsafe_allow_html=True)


# ==========================================
# 🧪 MAIN DASHBOARD (ISOLATED UI)
# ==========================================
elif st.session_state.current_page == "dashboard":

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp { background-color: #f4f7f6 !important; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        section[data-testid="stSidebar"] { display: block !important; }
        button[data-testid="collapsedControl"] { display: block !important; }
        .block-container { padding-top: 3rem !important; max-width: 1400px !important; }
        
        .top-stats { 
            display: flex; justify-content: space-around; 
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
            padding: 20px; border-radius: 16px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.04); 
            margin-bottom: 25px; border: 1px solid #e2e8f0; 
            flex-wrap: wrap; gap: 15px;
        }
        
        .stat-box { text-align: center; flex: 1; min-width: 120px; transition: transform 0.2s; } 
        .stat-box:hover { transform: translateY(-2px); }
        .stat-box * { color: #0f172a !important; }
        .stat-value { font-size: 28px; font-weight: 800; letter-spacing: -0.5px; } 
        .stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-top: 4px; color: #64748b !important; }
        
        .kanban-header { font-size: 14px; font-weight: 700; color: #334155 !important; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 3px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px; }
        .k-assigned { border-bottom-color: #f59e0b; } .k-progress { border-bottom-color: #3b82f6; } .k-review { border-bottom-color: #8b5cf6; } .k-done { border-bottom-color: #10b981; }
        
        .k-card { 
            background: #ffffff !important; border: 1px solid #e2e8f0; border-radius: 10px; 
            padding: 14px; margin-bottom: 14px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.02); 
            transition: all 0.2s ease; word-wrap: break-word;
        }
        .k-card:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.05); transform: translateY(-2px); border-color: #cbd5e1; }
        .k-card * { color: #0f172a !important; }
        .k-title { font-size: 14px; font-weight: 700; margin-bottom: 6px; } 
        .k-agent { font-size: 12px; color: #64748b !important; display: flex; align-items: center; gap: 6px; font-weight: 500;} 
        
        /* 🐛 BUG FIX: Hover Card Overlap Removed! Now it uses a clean inline flexbox */
        .agent-row { 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 12px; margin-bottom: 8px; border-radius: 10px; 
            background: #ffffff !important; 
            border: 1px solid #e2e8f0; cursor: pointer; 
            transition: all 0.2s ease; 
        }
        .agent-row:hover { border-color: #94a3b8; box-shadow: 0 4px 10px rgba(0,0,0,0.06); transform: translateY(-1px); }
        .agent-name-container { display: flex; flex-direction: column; gap: 2px; }
        .agent-name, .agent-name * { font-size: 14px; font-weight: 800; display: flex; align-items: center; gap: 8px; color: #0f172a !important; } 
        .agent-role { font-size: 10px; color: #64748b !important; font-weight: 600; margin-left: 28px; text-transform: uppercase; letter-spacing: 0.5px;}
        
        .status-badge { font-size: 10px; padding: 4px 10px; border-radius: 20px; font-weight: 800; letter-spacing: 0.5px;}
        .st-working, .st-working * { background: #dcfce7 !important; color: #166534 !important; border: 1px solid #bbf7d0 !important; box-shadow: 0 0 10px rgba(34, 197, 94, 0.2); } 
        .st-standby, .st-standby * { background: #f8fafc !important; color: #64748b !important; border: 1px solid #e2e8f0 !important; }
        
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        
        @media (max-width: 768px) {
            .top-stats { flex-direction: column; gap: 5px; }
            .stat-box { width: 100%; border-bottom: 1px solid #f1f5f9; padding: 10px 0; }
            .stat-box:last-child { border-bottom: none; }
            .agent-row { padding: 10px; }
            .agent-name, .agent-name * { font-size: 13px; }
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

    # 🧠 100% UNBREAKABLE TIMESTAMP LOGIC FOR HIDING FILES
    if "session_start_time" not in st.session_state: 
        st.session_state.session_start_time = time.time() - 5

    if "full_memory" not in st.session_state: st.session_state.full_memory = []
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Lab AgentX Online. The Squad is ready. What's the mission, Commander?"}]
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
                    # Sirf wo files dikhaye ga jo New Chat button dabane ke baad bani hain!
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
        <div class="stat-box"><div class="stat-value" style="color:#10b981 !important;">● ONLINE</div><div class="stat-label">System Status</div></div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("⬅️ View Pricing Plans", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()
            
        st.markdown("### 🎛️ AGENCY CONTROLS")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("💬 New Chat", use_container_width=True):
                st.session_state.full_memory.extend(st.session_state.messages)
                st.session_state.messages = [{"role": "assistant", "content": "Lab AgentX Online. Memory archived. Ready for the next mission."}]
                
                # 🛑 TIMESTAMP MAGIC: UI instantly saaf ho jayegi
                st.session_state.session_start_time = time.time()
                
                # Move files physically
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
                
        st.markdown("---")
        
        st.markdown(f"### 🏢 SQUAD STATUS ({working_agents_count} Active)")
        agents_html = ""
        for key, info in AGENTS_INFO.items():
            is_working = (key == "Lab AgentX" or key == current_active_agent)
            status_class = "st-working" if is_working else "st-standby"
            status_text = "WORKING" if is_working else "STANDBY"
            
            # 🐛 FIXED: Hover Card removed, added clean inline details & Native Tooltip
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
        st.markdown("### 📁 SAVED FILES")
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
        st.warning("⚠️ Cloud Brain Offline! Open 'Connect APIs' in the sidebar and paste your Groq API Key.")

    col_kanban, col_feed = st.columns([2.5, 1.2])

    with col_kanban:
        st.markdown("### 📋 TASK TRACKER")
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f"<div class='kanban-header k-assigned'>Assigned ({len(st.session_state.assigned_tasks)})</div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='kanban-header k-progress'>In Progress ({len(st.session_state.active_tasks)})</div>", unsafe_allow_html=True)
            for task in st.session_state.active_tasks:
                st.markdown(f"<div class='k-card' style='border-left: 3px solid #3b82f6;'><div class='k-title'>{task}</div><div class='k-agent'>🧪 Lab AgentX routing...</div><div class='k-tag'>Processing</div></div>", unsafe_allow_html=True)
        with k3: st.markdown(f"<div class='kanban-header k-review'>Review ({len(st.session_state.review_tasks)})</div>", unsafe_allow_html=True)
        with k4:
            st.markdown(f"<div class='kanban-header k-done'>Done ({len(done_tasks_list)})</div>", unsafe_allow_html=True)
            if done_tasks_list:
                done_container = st.container(height=500, border=False)
                with done_container:
                    for task in done_tasks_list:
                        st.markdown(f"<div class='k-card' style='border-left: 3px solid #10b981;'><div class='k-title'>{task['name'][:25]}...</div><div class='k-agent'>✅ Completed</div></div>", unsafe_allow_html=True)
                        if task['path'].endswith('.jpg') or task['path'].endswith('.png'):
                            with open(task['path'], "rb") as f:
                                st.download_button(label="🖼️ Download Image", data=f, file_name=os.path.basename(task['path']), mime="image/jpeg", key=task['path']+"_img")
                        else:
                            with open(task['path'], "r", encoding="utf-8", errors="ignore") as f: file_content = f.read()
                            st.download_button(label="📄 Download Report", data=file_content, file_name=task['name']+".txt", key=task['path']+"_txt")

    with col_feed:
        st.markdown("<div class='feed-header'>🟢 LIVE FEED</div>", unsafe_allow_html=True)
        feed_container = st.container(height=500)
        with feed_container:
            for message in st.session_state.messages:
                avatar = "🧪" if message["role"] == "assistant" else "🧑‍💼"
                with st.chat_message(message["role"], avatar=avatar): st.markdown(message["content"])

    st.markdown("---")
    col_up, col_in = st.columns([1, 6])
    with col_up: uploaded_file = st.file_uploader("Upload", type=["pdf", "png", "txt", "csv"], label_visibility="collapsed")
    with col_in: user_input = st.chat_input("Command the Agency (e.g., 'Sai, draw a cyberpunk city...')...")

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
            full_response = "⚠️ Lab AgentX Error: Groq Cloud API Key missing! Please paste it in the sidebar."
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
                        with st.spinner(f"Anime Agents are arguing and working... This might take a minute."):
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