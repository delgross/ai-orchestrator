
import time
import requests
import json

MODELS = [
    "llama3.3:70b",
    "qwen2.5:7b-instruct",
    "mxbai-embed-large:latest"
]

def benchmark_model(model_name):
    print(f"\n--- Benchmarking {model_name} ---")
    
    url = "http://127.0.0.1:11434/api/generate"
    data = {
        "model": model_name,
        "prompt": "Say hello.",
        "stream": False,
        "options": {
            "num_ctx": 32768 if "70b" in model_name else 16384 if "qwen" in model_name else 8192
        }
    }
    
    if "embed" in model_name:
         url = "http://127.0.0.1:11434/api/embeddings"
         data = {"model": model_name, "prompt": "Hello world"}
    
    start_time = time.time()
    try:
        response = requests.post(url, json=data)
        end_time = time.time()
        
        if response.status_code == 200:
            duration = end_time - start_time
            print(f"✅ Success. Duration: {duration:.4f}s")
            if "embed" not in model_name:
                res_json = response.json()
                print(f"   Output: {res_json.get('response', '').strip()}")
                print(f"   Eval Duration: {res_json.get('eval_duration', 0) / 1e9:.4f}s")
                print(f"   Load Duration: {res_json.get('load_duration', 0) / 1e9:.4f}s")
                
                if res_json.get('load_duration', 0) > 1e9: # > 1 second
                     print("   ⚠️  WARNING: High Load Duration (Model was swapped/reloaded?)")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🚀 Starting Latency Diagnosis...")
    for model in MODELS:
        benchmark_model(model)
    print("\nBenchmark Complete.")

if __name__ == "__main__":
    main()
