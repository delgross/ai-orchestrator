
import sys
import os

# Add parent dir to path so we can import agent_runner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.modal_tasks import graph_community_detection, has_modal

def test_gpu_connection():
    print("🔌 Testing Cloud GPU Connection (Modal)...")
    
    if not has_modal:
        print("❌ Error: Modal library not found or import failed.")
        return

    print("   Target: Graph Community Detection (Louvain Algorithm)")
    
    # 1. Create Dummy Data (A triangle and a separate pair)
    nodes = [1, 2, 3, 4, 5]
    edges = [(1,2), (2,3), (3,1), (4,5)] 
    # This should find two communities: {1,2,3} and {4,5}

    print("   Sending data to Cloud...")
    try:
        # call .remote() to trigger cloud execution
        result = graph_community_detection.remote(nodes, edges)
        
        print("\n✅ SUCCESS: Received response from Cloud!")
        print(f"   Result: {result}")
        print("   (Note: If you see {1: 0, 2: 0, 3: 0, 4: 1, 5: 1}, the math is correct.)")
        
    except Exception as e:
        print(f"\n❌ FAILURE: Could not connect to Cloud GPU.\n   Reason: {e}")
        print("\n   Did you run 'modal token new'?")

if __name__ == "__main__":
    test_gpu_connection()
