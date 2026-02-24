import streamlit as st
import requests
import datetime
import os
import glob
import time
import sys
from dotenv import load_dotenv

# --- FOLDER PATHS FIX FOR CLOUD ---
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'Agents')
sys.path.append(agents_dir)
for dept in ['Marketing', 'Tech', 'Video', 'Oracle', 'SEO', 'Legal', 'Finance', 'OmniReader', 'Multiplier', 'sales']:
    sys.path.append(os.path.join(agents_dir, dept))

# Load environment variables (API Keys)
load_dotenv()
INITIAL_GROQ_KEY = os.getenv("GROQ_API_KEY", "")

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

st.set_page_config(page_title="Lab AgentX | Anime HQ", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #f8f9fa; font-family: 'Inter', sans-serif; color: #1e293b; }
    .top-stats { display: flex; justify-content: space-around; background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .stat-box { text-align: center; } .stat-value { font-size: 24px; font-weight: 700; color: #0f172a; } .stat-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
    .kanban-header { font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; }
    .k-assigned { border-bottom-color: #f59e0b; } .k-progress { border-bottom-color: #3b82f6; } .k-review { border-bottom-color: #8b5cf6; } .k-done { border-bottom-color: #10b981; }
    .k-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s; }
    .k-title { font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 5px; } .k-agent { font-size: 11px; color: #64748b; display: flex; align-items: center; gap: 5px;} .k-tag { font-size: 10px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #475569; display: inline-block; margin-top: 8px; }
    .feed-header { font-size: 16px; font-weight: 600; margin-bottom: 15px; color: #1e293b; }
    .agent-row { display: flex; justify-content: space-between; align-items: center; padding: 10px; margin-bottom: 6px; border-radius: 8px; background: white; border: 1px solid #e2e8f0; position: relative; cursor: pointer; transition: all 0.2s ease; }
    .agent-row:hover { border-color: #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .agent-name { font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px;} .status-badge { font-size: 10px; padding: 3px 8px; border-radius: 12px; font-weight: 700; }
    .st-working { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; } .st-standby { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
    .agent-id-card { visibility: hidden; width: 220px; background-color: #0f172a; color: #f8fafc; text-align: left; border-radius: 10px; padding: 12px; position: absolute; z-index: 1000; top: 110%; left: 5px; opacity: 0; transition: opacity 0.3s, transform 0.3s; transform: translateY(10px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); border: 1px solid #334155; }
    .agent-row:hover .agent-id-card { visibility: visible; opacity: 1; transform: translateY(0); }
    .id-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 6px; } .id-role { color: #38bdf8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; } .id-desc { font-size: 12px; color: #94a3b8; line-height: 1.4; } .id-stat { display: inline-block; margin-top: 8px; background: #1e293b; padding: 2px 6px; border-radius: 4px; font-size: 10px; color: #cbd5e1; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ANIME THEME AGENTS MAPPING
AGENTS_INFO = {
    "Lab AgentX": {"name": "Lab AgentX", "role": "Squad Lead", "icon": "🧪", "desc": "The mastermind & eccentric CEO. Routes tasks.", "stat": "System Commander"},
    "Naruto": {"name": "Naruto Uzumaki", "role": "Content Multiplier", "icon": "🦊", "desc": "Uses shadow clones to turn 1 video into 20 posts.", "stat": "Omni-Channel"},
    "Light": {"name": "Light Yagami", "role": "Appointment Setter", "icon": "📓", "desc": "Writes leads' names, books meetings, sends cold DMs.", "stat": "Sales"},
    "Orihime": {"name": "Orihime Inoue", "role": "Client Savior", "icon": "🛡️", "desc": "Heals client relations and prevents churn.", "stat": "Support"},
    "Gojo": {"name": "Satoru Gojo", "role": "Marketing Head", "icon": "♾️", "desc": "Limitless ad strategies, copywriting & SEO.", "stat": "Content Creator"},
    "Franky": {"name": "Franky", "role": "Tech Lead", "icon": "🦾", "desc": "Compiles SUUPER Python/HTML code and builds apps.", "stat": "Developer"},
    "Tengen": {"name": "Tengen Uzui", "role": "Video Producer", "icon": "✨", "desc": "Generates flashy viral video scripts and visual assets.", "stat": "Media"},
    "L": {"name": "L Lawliet", "role": "Deep Research", "icon": "🍰", "desc": "Ultimate detective, scans the web for verified facts.", "stat": "Intel"},
    "Itachi": {"name": "Itachi Uchiha", "role": "Web Intel", "icon": "👁️", "desc": "Uses Sharingan to spy on competitor websites.", "stat": "Scraper"},
    "Nami": {"name": "Nami", "role": "Finance Analyst", "icon": "🍊", "desc": "Crunches VC data, tracks money and stocks.", "stat": "Wall St"},
    "Nanami": {"name": "Kento Nanami", "role": "Legal Expert", "icon": "👔", "desc": "Reviews dense contracts strictly during working hours.", "stat": "Lawyer"},
    "Senku": {"name": "Senku Ishigami", "role": "Knowledge Extractor", "icon": "🧫", "desc": "Summarizes YouTube transcripts with 10 Billion % accuracy.", "stat": "Data Miner"},
    "Akatsuki": {"name": "The Akatsuki", "role": "Mass Generator", "icon": "☁️", "desc": "Parallel workflows generating mass SEO blogs.", "stat": "Blogger"}
}

MEMORY_FOLDER = "memory_logs"
UPLOAD_FOLDER = "uploads"
DELIVERABLES_FOLDER = "Deliverables"
for folder in [MEMORY_FOLDER, UPLOAD_FOLDER, DELIVERABLES_FOLDER]:
    if not os.path.exists(folder): os.makedirs(folder)

if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Lab AgentX Online. Awaiting your command, Commander."}]
if "active_tasks" not in st.session_state: st.session_state.active_tasks = []
if "assigned_tasks" not in st.session_state: st.session_state.assigned_tasks = []
if "review_tasks" not in st.session_state: st.session_state.review_tasks = []
if "processed_files" not in st.session_state: st.session_state.processed_files = set()

def get_done_tasks():
    tasks = []
    for root, _, filenames in os.walk(DELIVERABLES_FOLDER):
        for fname in filenames:
            fpath = os.path.join(root, fname)
            tasks.append({"name": fname.replace(".md", "").replace(".txt", "").replace("_", " "), "path": fpath, "time": os.path.getmtime(fpath)})
    return sorted(tasks, key=lambda x: x['time'], reverse=True)[:5]

done_tasks_list = get_done_tasks()

current_active_agent = "Lab AgentX"
agent_keywords_map = {
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
    <div class="stat-box"><div class="stat-value" style="color:#38bdf8;">{current_active_agent}</div><div class="stat-label">Filtering By</div></div>
    <div class="stat-box"><div class="stat-value" style="color:#10b981;">● CLOUD HOSTED</div><div class="stat-label">System Status</div></div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 🏢 SQUAD STATUS ({working_agents_count} Active)")
    agents_html = ""
    for key, info in AGENTS_INFO.items():
        is_working = (key == "Lab AgentX" or key == current_active_agent)
        status_class = "st-working" if is_working else "st-standby"
        status_text = "WORKING" if is_working else "STANDBY"
        agents_html += f"""<div class='agent-row'><span class='agent-name'>{info['icon']} {key}</span><span class='status-badge {status_class}'>{status_text}</span>
        <div class='agent-id-card'><div class='id-header'><span style='font-size: 20px;'>{info['icon']}</span><div><div style='font-size: 14px; font-weight: bold;'>{info['name']}</div>
        <div class='id-role'>{info['role']}</div></div></div><div class='id-desc'>{info['desc']}</div><div class='id-stat'>⚙️ Specialty: {info['stat']}</div></div></div>"""
    st.markdown(agents_html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔗 INTEGRATIONS")
    with st.expander("⚙️ Connect APIs (REQUIRED)", expanded=True):
        st.caption("Add your AI and Social API Keys here.")
        live_groq_key = st.text_input("Groq API Key (For AI Brain)", type="password", value=INITIAL_GROQ_KEY)
        tw_api = st.text_input("Twitter API Key", type="password")
        li_tok = st.text_input("LinkedIn Access Token", type="password")

    st.markdown("---")
    if st.button("🔄 Refresh System"): st.rerun()

# --- THE MASTER OVERRIDE ---
if live_groq_key:
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_API_KEY"] = live_groq_key
    
    import langchain_openai
    if not hasattr(langchain_openai.ChatOpenAI, "_original_init"):
        langchain_openai.ChatOpenAI._original_init = langchain_openai.ChatOpenAI.__init__

    def patched_init(self, *args, **kwargs):
        kwargs["model"] = "llama-3.3-70b-versatile"
        kwargs["base_url"] = "https://api.groq.com/openai/v1"
        kwargs["api_key"] = live_groq_key
        langchain_openai.ChatOpenAI._original_init(self, *args, **kwargs)

    langchain_openai.ChatOpenAI.__init__ = patched_init
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
            for task in done_tasks_list:
                st.markdown(f"<div class='k-card' style='border-left: 3px solid #10b981;'><div class='k-title'>{task['name'][:25]}...</div><div class='k-agent'>✅ Completed</div></div>", unsafe_allow_html=True)
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
with col_in: user_input = st.chat_input("Command the Agency (e.g., 'Senku, read this YouTube video...')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.active_tasks.append(user_input[:30] + "...") 
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]
    msg_content = last_msg["content"]
    
    # 🔥 THE ULTIMATE ANTI-HALLUCINATION PROMPT 🔥
    system_prompt = """
    You are LAB AGENTX, the CEO of an Anime-themed AI Agency.
    
    CRITICAL INSTRUCTION - READ CAREFULLY:
    1. YOU MUST NEVER DO THE TASK YOURSELF. Do NOT write plans, strategies, blogs, or codes.
    2. When a user requests a task, you must ONLY reply with EXACTLY ONE SENTENCE from the routing list below.
    3. DO NOT add any conversational filler, explanations, or analysis before or after the routing line.
    
    ROUTING LIST:
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

    IF AND ONLY IF the user just says "hi", "who are you", or asks a general question, you may explain your role gracefully without routing. But if a task is given, output ONLY the routing line.
    """
    
    if not live_groq_key:
        full_response = "⚠️ Lab AgentX Error: Groq Cloud API Key missing! Please paste it in the sidebar."
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        if st.session_state.active_tasks: st.session_state.active_tasks.pop()
        st.rerun()
    else:
        try:
            api_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages[-6:]:
                content_str = m["content"]
                if len(content_str) > 800:
                    content_str = content_str[:800] + "... [Content truncated for memory]"
                api_messages.append({"role": m["role"], "content": content_str})

            headers = {"Authorization": f"Bearer {live_groq_key}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": api_messages, "temperature": 0.1} # Lowered temperature so it doesn't get creative
            
            api_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
            
            if 'choices' in api_response:
                full_response = api_response['choices'][0]['message']['content']
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                if "Task Assigned" in full_response or "Deploying" in full_response:
                    with st.spinner(f"Anime Agents are working on it... This might take a minute."):
                        agent_result = "⚠️ Agent not fully integrated for cloud yet."
                        
                        if "**Gojo**" in full_response:
                            from marketing import run_marketing_crew
                            agent_result = run_marketing_crew(msg_content)
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
                            agent_result = run_mass_seo_campaign(msg_content)
                        elif "**Naruto**" in full_response:
                            try:
                                from content_multiplier import run_multiplier_crew
                                agent_result = run_multiplier_crew(msg_content)
                            except: agent_result = "Multiplier dependencies missing on cloud."
                        
                        st.session_state.messages.append({"role": "assistant", "content": f"✅ **Mission Complete:**\n\n{agent_result}"})
            else:
                error_details = api_response.get('error', {}).get('message', str(api_response))
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Groq API Error: {error_details}"})

        except Exception as e: 
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Connection Error: {str(e)}"})
        
        if st.session_state.active_tasks: st.session_state.active_tasks.pop()
        st.rerun()