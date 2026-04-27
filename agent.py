from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()

# Connect to Groq
llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)

# Search tool
search = DuckDuckGoSearchRun()
tools = [search]

# Create agent
agent_executor = create_react_agent(llm, tools)

print("🔍 Search Agent Ready! Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    
    response = agent_executor.invoke({
        "messages": [HumanMessage(content=user_input)]
    })
    
    last_message = response["messages"][-1]
    
    print(f"\nAgent: {last_message.content}\n")