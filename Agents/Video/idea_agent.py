import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# Setup LLM
llm = ChatOpenAI(model="llama3-70b-8192")
search_tool = DuckDuckGoSearchRun()

def get_idea_agent():
    return Agent(
        role='Viral Idea Generator',
        goal='Find a unique angle for this video topic that will go viral',
        backstory='You analyze YouTube trends. You know what makes people click.',
        tools=[search_tool],
        allow_delegation=False,
        llm=llm
    )