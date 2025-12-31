import modal
import sys
import logging
from pathlib import Path
from agent_runner.modal_tasks import (
    app, 
    CloudIntelligence, 
    graph_community_detection,
    rerank_search_results,
    verify_fact,
    cloud_process_image,
    detect_visual_anomaly,
    cloud_database_cleanup
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("h100_live")

@app.local_entrypoint()
def main():
    print("🚀 Starting LIVE H100 Uplink Verification (Full Coverage)...")
    
    ci = CloudIntelligence()

    # --- PART 1: CLOUD INTELLIGENCE (H100 + Snapshot) ---

    # 1. Test Cloud Graph Weaver
    print("\n🕸️ [1/10] Testing Cloud Graph Weaver (H100)...")
    nodes = ["Tesla", "Elon Musk", "SpaceX", "Mars"]
    try:
        res = ci.cloud_graph_weaver.remote(nodes)
        print(f"   ✅ Result: {res}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 2. Test Cloud Truth Auditor
    print("\n⚖️ [2/10] Testing Cloud Truth Auditor (H100)...")
    conflicts = ["The sky is blue.", "The sky is green."]
    try:
        res = ci.cloud_truth_auditor.remote(conflicts)
        print(f"   ✅ Result: {res}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 3. Test Cloud Gap Detector
    print("\n🔍 [3/10] Testing Cloud Gap Detector (H100)...")
    context = "Project: Build a Rocket. Deadline: tomorrow."
    try:
        res = ci.cloud_gap_detector.remote(context)
        print(f"   ✅ Result: {res}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # --- PART 2: STANDALONE FUNCTIONS ---

    # 4. Graph Community Detection (CPU)
    print("\n🏘️ [4/10] Testing Graph Community Detection (CPU)...")
    g_nodes = ["A", "B", "C", "D", "E"]
    g_edges = [("A", "B"), ("A", "C"), ("B", "C"), ("D", "E")] # Two communities: {A,B,C}, {D,E}
    try:
        res = graph_community_detection.remote(g_nodes, g_edges)
        print(f"   ✅ Result: {res}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 5. Rerank Search Results (CPU + Pip)
    print("\n📊 [5/10] Testing Rerank Search Results...")
    query = "What is the capital of France?"
    candidates = ["Paris is in France.", "London is in UK.", "Paris is the capital."]
    try:
        res = rerank_search_results.remote(query, candidates)
        print(f"   ✅ Result: {res}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 6. Verify Fact (CPU + RoBERTa)
    print("\n✔️ [6/10] Testing Fact Verification...")
    fact = "Paris is the capital of France."
    evidence = "Paris is the capital city of France."
    try:
        res = verify_fact.remote(fact, evidence)
        print(f"   ✅ Result: {res}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 7. Cloud Database Cleanup (H100)
    print("\n🧹 [7/10] Testing Cloud Database Cleanup (H100)...")
    facts_dirty = '["Sky is blue", "Sky is blue", "Water is wet"]'
    try:
        res = cloud_database_cleanup.remote(facts_dirty)
        print(f"   ✅ Result: {str(res)[:100]}...") # Truncate
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # --- PART 3: VISION (Using Real PDF as Image Source) ---
    print("\n🖼️ [8/10] Preparing Image Data (Extracting from PDF)...")
    pdf_path = Path("/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest/deferred/seavision_eyeglasses_invoice_2024.pdf")
    first_page_bytes = None
    
    if pdf_path.exists():
        try:
            from pdf2image import convert_from_path
            import io
            # We assume pdf2image is installed LOCALLY for this prep step
            # If not, we might fail here. But let's try reading as raw or assume local has tools.
            # Fallback: Just send the PDF bytes as "image" (Fail) or use a dummy image.
            # Better: Create a dummy image in memory if pdf2image fails.
            
            try:
                images = convert_from_path(str(pdf_path), first_page=1, last_page=1)
                img_byte_arr = io.BytesIO()
                images[0].save(img_byte_arr, format='JPEG')
                first_page_bytes = img_byte_arr.getvalue()
                print("   ✅ Extracted Page 1 as Image.")
            except ImportError:
                print("   ⚠️ Local pdf2image missing. Using dummy black image.")
                from PIL import Image
                img = Image.new('RGB', (100, 100), color = 'red')
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                first_page_bytes = img_byte_arr.getvalue()
            
            # 8. Test Cloud Process Image
            print("\n📸 [8/10] Testing Cloud Process Image (H100)...")
            res = cloud_process_image.remote(first_page_bytes, "Describe this image.")
            print(f"   ✅ Result: {str(res)[:100]}...")

            # 9. Test Visual Anomaly
            print("\n👁️ [9/10] Testing Visual Anomaly Detection (H100)...")
            # Compare image to itself (Should be no anomaly)
            res = detect_visual_anomaly.remote(first_page_bytes, first_page_bytes)
            print(f"   ✅ Result: {str(res)[:100]}...")

            # 10. Test PDF Processing (Full)
            print("\n📄 [10/10] Testing Full PDF Processing (H100 + Docling)...")
            pdf_bytes = pdf_path.read_bytes()
            res = ci.cloud_process_pdf.remote(pdf_bytes, pdf_path.name)
            meta = res.get("metadata", {})
            print(f"   ✅ Processing Complete.")
            print(f"   📝 Summary: {meta.get('summary', 'No summary')}")
            print(f"   📊 Entities: {len(meta.get('entities', []))}")

        except Exception as e:
             print(f"   ❌ Vision/PDF Tests Failed: {e}")

    else:
        print("   ⚠️ PDF File not found. Skipping Vision Tests.")

    print("\n✅ Verification Complete.")
