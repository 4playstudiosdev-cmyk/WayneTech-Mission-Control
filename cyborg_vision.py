import cv2
import os
import base64
import ollama
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# --- Setup Local AI ---
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "NA"

llm = ChatOpenAI(model="llama3", base_url="http://localhost:11434/v1", api_key="NA")

def extract_frames(video_path, output_folder="video_frames"):
    """Video ko tod kar 5 main screenshots nikalna"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    cam = cv2.VideoCapture(video_path)
    total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cam.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps
    
    # Hum sirf 4 key moments nikalenge taaki PC hang na ho
    timestamps = [duration*0.2, duration*0.4, duration*0.6, duration*0.8]
    frame_paths = []
    
    print(f"🎬 Analyzing Video Duration: {duration:.2f}s. Extracting keyframes...")
    
    for i, timestamp in enumerate(timestamps):
        cam.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cam.read()
        if ret:
            path = f"{output_folder}/frame_{i}.jpg"
            cv2.imwrite(path, frame)
            frame_paths.append(path)
            
    cam.release()
    return frame_paths

def analyze_frames_with_vision(frame_paths):
    """Llama 3.2 Vision se poocho ke frames mein kya ho raha hai"""
    print("🤖 Cyborg is scanning the visual data...")
    full_description = ""
    
    for path in frame_paths:
        with open(path, "rb") as f:
            img_bytes = f.read()
            
        response = ollama.chat(
            model='llama3.2-vision',
            messages=[{
                'role': 'user',
                'content': 'Describe this UI/Game screen in extreme technical detail. What buttons, colors, mechanics, and layout do you see? If it is a game, explain the rules.',
                'images': [img_bytes]
            }]
        )
        full_description += f"\n[Frame Analysis]: {response['message']['content']}\n"
        
    return full_description

def run_cyborg_video_coder(video_path):
    print(f"\n🦾 CYBORG VISION ACTIVATED: Processing {video_path}\n")
    
    # 1. Video se aankhein (Frames) nikalo
    frames = extract_frames(video_path)
    
    # 2. Dimaag (Vision Model) se samjho
    visual_analysis = analyze_frames_with_vision(frames)
    
    # 3. Code Generation Crew
    cyborg = Agent(
        role='Cyborg (Lead Developer)',
        goal='Recreate exactly what is seen in the video using Python/HTML',
        backstory='You are Victor Stone. You can interface with any tech. You see a video of software and you instantly know how to code it.',
        allow_delegation=False,
        llm=llm
    )
    
    coding_task = Task(
        description=f"""
        ANALYSIS OF UPLOADED VIDEO:
        {visual_analysis}
        
        YOUR MISSION:
        Based strictly on the visual analysis above, write the COMPLETE CODE to recreate this game/app.
        1. If it looks like a game (Flappy Bird, Pong, etc.), use Python with Pygame.
        2. If it looks like a website, use HTML/CSS/JS.
        
        Output only the code.
        """,
        agent=cyborg,
        expected_output="Functional Code Block"
    )
    
    crew = Crew(agents=[cyborg], tasks=[coding_task], verbose=True)
    result = crew.kickoff()
    
    # Save Code
    timestamp = os.path.basename(video_path).split('.')[0]
    filename = f"Deliverables/Cyborg_Recreation_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(result))
        
    return f"🦾 CYBORG REPORT: System Recreated.\n📂 Code Saved: {filename}"