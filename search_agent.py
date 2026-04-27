from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()

# Connect to Groq
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# Search tool
search = DuckDuckGoSearchRun()

# Bind tool directly to model
llm_with_tools = llm.bind_tools([search])

print("🔍 Search Agent Ready! Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    
    # Step 1 - Ask model what to do
    messages = [HumanMessage(content=user_input)]
    response = llm_with_tools.invoke(messages)
    
    # Step 2 - If model wants to search, do the search
    if response.tool_calls:
        for tool_call in response.tool_calls:
            search_query = tool_call["args"]["query"]
            print(f"\n🔍 Searching for: {search_query}\n")
            search_result = search.run(search_query)
            
            # Step 3 - Give results back to model
            final_messages = messages + [
                response,
                HumanMessage(content=f"Search results: {search_result}")
            ]
            final_response = llm.invoke(final_messages)
            print(f"\nAgent: {final_response.content}\n")
    else:
        print(f"\nAgent: {response.content}\n")