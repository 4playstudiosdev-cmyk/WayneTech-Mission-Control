import os
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama-3.3-70b-versatile")
def get_production_agent():
    return Agent(
        role='Auto-Video Architect',
        goal='Generate Python code (FFmpeg/MoviePy) and AI Prompts to build the video',
        backstory='You are a technical wizard. You write code to automate video editing and generate image prompts.',
        allow_delegation=False,
        llm=llm
    )