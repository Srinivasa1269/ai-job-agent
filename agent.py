from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Connect to Ollama with Llama 3
llm = OllamaLLM(model="llama3:latest")

# Give the agent a personality
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI job assistant. Help users with job applications and career advice."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Memory to remember conversation
chat_history = []

# Chain everything together
chain = prompt | llm

print("🤖 AI Job Agent is ready! Type 'quit' to exit.\n")

# Chat loop
while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    
    response = chain.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
    
    # Save to memory
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response))
    
    print(f"\nAgent: {response}\n")