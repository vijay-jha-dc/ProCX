"""Quick test to check if OpenAI API key works"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key found: {api_key[:20]}..." if api_key else "No API key!")

# Test OpenAI connection
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Using gpt-4o-mini instead
        temperature=0.7,
        api_key=api_key
    )
    
    print("\n🧪 Testing OpenAI API...")
    response = llm.invoke("Say 'Hello from AgentMAX!' in one sentence.")
    print(f"✅ Success! Response: {response.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"\nFull error details:")
    import traceback
    traceback.print_exc()
