
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
# Add project root to path (The 'ai' directory)
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.modal_tasks import CloudIntelligence, has_modal, app

async def main():
    if not has_modal:
        print("❌ Modal not installed or configured.")
        return

    print("🚀 Using Real Test PDF...")
    # Path to an existing known PDF in the repo (found via find_by_name)
    pdf_path = "agent_fs_root/ingest/deferred/Beekeeping Blueprint (Exclusive Pre-Release).pdf"
    
    if not os.path.exists(pdf_path):
         print(f"❌ PDF not found at {pdf_path}. Trying fallback search...")
         # Fallback to absolute path or search?
         # Assuming cwd is /Users/bee/Sync/Antigravity/ai
         pdf_path = "/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest/deferred/Beekeeping Blueprint (Exclusive Pre-Release).pdf"
         if not os.path.exists(pdf_path):
             print("❌ Aborting. Cannot find test PDF.")
             return

    print(f"📄 Found: {os.path.basename(pdf_path)}")

    print("📤 Uploading to H100 (Refinery)...")
    if not os.path.exists(pdf_path):
         print("❌ PDF generation failed.")
         return

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    try:
        # Trigger the Class Method Remotely (Ephemeral Run)
        print("   Starting Ephemeral App...")
        with app.run():
            print("   Calling CloudIntelligence().cloud_process_pdf...")
            # Note: Instantiate the class first!
            
            result = CloudIntelligence().cloud_process_pdf.remote(file_bytes, "project_apollo.pdf")
            
            print("\n--- 🧠 H100 RESULT ---")
        if "metadata" in result:
            meta = result["metadata"]
            print(f"Entities: {meta.get('entities')}")
            print(f"Summary:  {meta.get('summary')}")
            print(f"Structure: {meta.get('structured_data')}")
            print(f"Score:    {meta.get('quality_score')}")
        else:
            print("❌ No metadata returned.")
            print(result)

    except Exception as e:
        print(f"❌ Cloud Execution Failed: {e}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    asyncio.run(main())
