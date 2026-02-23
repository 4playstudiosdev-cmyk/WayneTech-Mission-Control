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

st.set_page_config(page_title="Mission Control | WayneTech", page_icon="🦇", layout="wide", initial_sidebar_state="expanded")

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

AGENTS_INFO = {
    "Batman": {"name": "Batman", "role": "Squad Lead", "icon": "🦇", "desc": "The mastermind. Routes tasks.", "stat": "System Commander"},
    "Multiplier": {"name": "Multiplier", "role": "Content Repurposer", "icon": "🐙", "desc": "Turns 1 video into 20 posts.", "stat": "Omni-Channel"},
    "LeadBooker": {"name": "LeadBooker", "role": "Appointment Setter", "icon": "📅", "desc": "Books meetings, sends cold DMs.", "stat": "Sales"},
    "RetentionBot": {"name": "RetentionBot", "role": "Client Savior", "icon": "🛟", "desc": "Prevents client churn.", "stat": "Support"},
    "Superman": {"name": "Superman", "role": "Marketing Head", "icon": "🦸‍♂️", "desc": "Ad strategies & SEO.", "stat": "Content Creator"},
    "Cyborg": {"name": "Cyborg", "role": "Tech Lead", "icon": "🤖", "desc": "Compiles python/HTML code.", "stat": "Developer"},
    "Lantern": {"name": "Green Lantern", "role": "Video Producer", "icon": "💍", "desc": "Generates video scripts.", "stat": "Media"},
    "Manhunter": {"name": "Martian Manhunter", "role": "Deep Research", "icon": "👽", "desc": "Scans web for facts.", "stat": "Intel"},
    "Oracle": {"name": "Oracle", "role": "Web Intel", "icon": "🔮", "desc": "Spies on competitor websites.", "stat": "Scraper"},
    "Lucius": {"name": "Lucius", "role": "Finance Analyst", "icon": "💰", "desc": "Crunches VC data, stocks.", "stat": "Wall St"},
    "Daredevil": {"name": "Daredevil", "role": "Legal Expert", "icon": "⚖️", "desc": "Reviews dense contracts.", "stat": "Lawyer"},
    "Brainiac": {"name": "Brainiac", "role": "Knowledge Extractor", "icon": "🧠", "desc": "Summarizes YouTube transcripts.", "stat": "Data Miner"},
    "SEO Team": {"name": "SEO Team", "role": "Mass Generator", "icon": "✍️", "desc": "Parallel SEO workflows.", "stat": "Blogger"}
}

MEMORY_FOLDER = "memory_logs"
UPLOAD_FOLDER = "uploads"
DELIVERABLES_FOLDER = "Deliverables"
for folder in [MEMORY_FOLDER, UPLOAD_FOLDER, DELIVERABLES_FOLDER]:
    if not os.path.exists(folder): os.makedirs(folder)

if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Mission Control Online. Waiting for Commander's input."}]
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

current_active_agent = "Batman"
agent_keywords_map = {
    "Multiplier": ["multiplier", "omni-channel", "repurpose"], "LeadBooker": ["leadbooker", "booking"], "RetentionBot": ["retentionbot", "churn"],
    "Superman": ["superman", "marketing"], "Cyborg": ["cyborg", "coding", "html"], "Lantern": ["lantern", "video"],
    "Manhunter": ["manhunter", "research"], "Oracle": ["oracle", "intelligence", "competitor"], "Lucius": ["lucius", "finance", "financial"],
    "Daredevil": ["daredevil", "legal"], "Brainiac": ["brainiac", "youtube"], "SEO Team": ["seo team", "seo department", "blogs"]
}

for msg in reversed(st.session_state.messages):
    if msg["role"] == "assistant" and ("Task Assigned" in msg["content"] or "Deploying" in msg["content"]):
        msg_lower = msg["content"].lower()
        for agent_name, keywords in agent_keywords_map.items():
            if any(kw in msg_lower for kw in keywords):
                current_active_agent = agent_name
                break
        if current_active_agent != "Batman": break

total_agents = len(AGENTS_INFO)
working_agents_count = 2 if current_active_agent != "Batman" else 1 
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
        is_working = (key == "Batman" or key == current_active_agent)
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
        # UI fetches key directly. It will persist as long as session is active.
        live_groq_key = st.text_input("Groq API Key (For AI Brain)", type="password", value=INITIAL_GROQ_KEY)
        tw_api = st.text_input("Twitter API Key", type="password")
        li_tok = st.text_input("LinkedIn Access Token", type="password")

    st.markdown("---")
    if st.button("🔄 Refresh System"): st.rerun()

# Apply Groq Key globally for CrewAI agents
if live_groq_key:
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_API_KEY"] = live_groq_key
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
            st.markdown(f"<div class='k-card' style='border-left: 3px solid #3b82f6;'><div class='k-title'>{task}</div><div class='k-agent'>🦇 Batman routing...</div><div class='k-tag'>Processing</div></div>", unsafe_allow_html=True)
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
            avatar = "🦇" if message["role"] == "assistant" else "🧑‍💼"
            with st.chat_message(message["role"], avatar=avatar): st.markdown(message["content"])

st.markdown("---")
col_up, col_in = st.columns([1, 6])
with col_up: uploaded_file = st.file_uploader("Upload", type=["pdf", "png", "txt", "csv"], label_visibility="collapsed")
with col_in: user_input = st.chat_input("Command the Agency (e.g., 'Repurpose this video into 20 posts')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.active_tasks.append(user_input[:30] + "...") 
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]
    msg_content = last_msg["content"]
    
    system_prompt = """
    You are BATMAN. The Master Strategist and Dispatcher of the AI Agency.
    Reply EXACTLY with ONE of these lines depending on the task:
    1. Video Repurpose -> "Task Assigned. **Multiplier** is generating omni-channel content."
    2. Booking/Leads -> "Task Assigned. **LeadBooker** is scheduling meetings."
    3. Retention/Churn -> "Task Assigned. **RetentionBot** is analyzing customer health."
    4. Uploaded document -> "Task Assigned. **Daredevil** is reviewing the document."
    5. Stocks/Finance -> "Task Assigned. **Lucius** is crunching financial data."
    6. Legal/Contracts -> "Task Assigned. **Daredevil** is reviewing legal terms."
    7. Spying/Competitors -> "Task Assigned. **Oracle** is extracting intelligence."
    8. Write SEO/Blogs -> "Task Assigned. **SEO Team** is running parallel workflows."
    9. Code/HTML/Bugs -> "Task Assigned. Deploying **Cyborg**."
    10. YouTube Summary -> "Task Assigned. **Brainiac** is extracting YouTube data."
    11. General Marketing/Ads -> "Task Assigned. **Superman** is drafting content."
    If none match, reply: "Batman: I need more details to assign this task."
    """
    
    if not live_groq_key:
        full_response = "⚠️ Batman Error: Groq Cloud API Key missing! Please paste it in the sidebar."
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        if st.session_state.active_tasks: st.session_state.active_tasks.pop()
        st.rerun()
    else:
        try:
            # 1. Get routing decision from Batman
            headers = {"Authorization": f"Bearer {live_groq_key}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": msg_content}]}
            
            api_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
            
            # Robust Error Handling
            if 'choices' in api_response:
                full_response = api_response['choices'][0]['message']['content']
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # 2. 🔥 SERVERLESS EXECUTION: Run the Agent directly inside the dashboard!
                with st.spinner(f"Agents are working on it... This might take a minute."):
                    agent_result = "⚠️ Agent not fully integrated for cloud yet."
                    
                    if "**Superman**" in full_response:
                        from marketing import run_marketing_crew
                        agent_result = run_marketing_crew(msg_content)
                    elif "**Oracle**" in full_response:
                        from oracle_intel import run_oracle_crew
                        agent_result = run_oracle_crew(msg_content)
                    elif "**Lucius**" in full_response:
                        from Investment_Banker import run_finance_crew
                        agent_result = run_finance_crew(msg_content)
                    elif "**Brainiac**" in full_response:
                        from omni_reader import run_omnireader_crew
                        agent_result = run_omnireader_crew(msg_content)
                    elif "**Cyborg**" in full_response:
                        from tech import run_tech_crew
                        agent_result = run_tech_crew(msg_content)
                    elif "**SEO Team**" in full_response:
                        from seo_empire import run_mass_seo_campaign
                        agent_result = run_mass_seo_campaign(msg_content)
                    elif "**Multiplier**" in full_response:
                        try:
                            from content_multiplier import run_multiplier_crew
                            agent_result = run_multiplier_crew(msg_content)
                        except: agent_result = "Multiplier dependencies (tweepy/youtube-transcript-api) missing on cloud."
                    
                    # Show result in chat
                    st.session_state.messages.append({"role": "assistant", "content": f"✅ **Mission Complete:**\n\n{agent_result}"})
            else:
                # Agar Groq ne error diya hai (jaise Invalid Key ya Rate Limit) toh wo screen par show hoga
                error_details = api_response.get('error', {}).get('message', str(api_response))
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Groq API Error: {error_details}"})

        except Exception as e: 
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Connection Error: {str(e)}"})
        
        if st.session_state.active_tasks: st.session_state.active_tasks.pop()
        st.rerun()