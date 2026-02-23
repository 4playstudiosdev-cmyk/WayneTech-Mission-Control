import os
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="llama3-70b-8192")
def get_production_agent():
    return Agent(
        role='Auto-Video Architect',
        goal='Generate Python code (FFmpeg/MoviePy) and AI Prompts to build the video',
        backstory='You are a technical wizard. You write code to automate video editing and generate image prompts.',
        allow_delegation=False,
        llm=llm
    )