# tests/test_agent.py
import sys
import os

# Add the project root to the Python path so we can import the agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from namer_agent.agent import root_agent
from namer_agent.config import configure_genai

def test_naming_flow():
    """
    Integration Test: Runs a full dialogue flow to verify the agent works.
    """
    print("🧪 Starting Integration Test for Naming Master...")
    
    # 1. Configure Auth
    configure_genai()
    
    # 2. Define a test user session
    # We simulate the "Jack Smith" scenario
    user_id = "test_user_001"
    
    # Step 1: Greeting
    print("\n🔹 Step 1: Sending 'Hi'...")
    response_1 = root_agent.invoke("Hi", user_id=user_id)
    print(f"🤖 Agent: {response_1.text[:100]}...") # Print preview
    assert "Hello" in response_1.text or "Name" in response_1.text
    
    # Step 2: Full Request
    print("\n🔹 Step 2: Sending 'I am Jack Smith, Male'...")
    response_2 = root_agent.invoke("I am Jack Smith, Male", user_id=user_id)
    print(f"🤖 Agent: {response_2.text[:200]}...") 
    
    # 3. Verify Logic (The "Asserts")
    # Check if it mapped the surname 'Smith' -> 'Shi' (史)
    if "史" in response_2.text:
        print("✅ PASS: Surname 'Smith' correctly mapped to 'Shi' (史).")
    else:
        print("❌ FAIL: Surname mapping missed.")
        
    # Check if it generated a Markdown table
    if "|" in response_2.text and "Rank" in response_2.text:
        print("✅ PASS: Output format is a Markdown Table.")
    else:
        print("❌ FAIL: Output format is wrong.")

    print("\n🎉 Test Complete!")

if __name__ == "__main__":
    test_naming_flow()
