import sys
import os
# Ensure root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from sdk.client import AntigravityClient

def test_sdk():
    print("Initializing Client...")
    # Test Debug Mode
    client = AntigravityClient(debug=True)
    
    print("\n--- Testing Health ---")
    h = client.health()
    print("Health:", h)
    
    print("\n--- Testing Chat (Sync) ---")
    try:
        # Short timeout to avoid blocking if LLM is slow, but client has 60s timeout
        msg = client.chat("Hello SDK", model="router")
        print("Response:", msg)
    except Exception as e:
        print("Chat Failed:", e)

if __name__ == "__main__":
    test_sdk()
