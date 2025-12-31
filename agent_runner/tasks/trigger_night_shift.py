
import asyncio
import modal
import os
import sys

# Connect to the Modal App
APP_NAME = "antigravity-night-shift"
CLASS_NAME = "CloudIntelligence"

async def trigger_night_shift():
    print(f"📡 Networking: Connecting to {APP_NAME}::{CLASS_NAME}...")
    
    try:
        CloudBrain = modal.Cls.from_name(APP_NAME, CLASS_NAME)
        brain = CloudBrain()
    except Exception as e:
        print(f"❌ Could not connect to Modal app: {e}")
        return

    print("⚡️ Connected. Sending dummy PDF task...")
    
    # Dummy PDF content (minimal valid PDF header if possible, or just text)
    # The Cloud function falls back to pypdf or text processing if Docling fails
    dummy_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n70 700 Td\n/F1 24 Tf\n(Hello from the Night Shift!) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\n0000000258 00000 n\n0000000344 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n439\n%%EOF"

    try:
        response = await asyncio.to_thread(
            brain.cloud_process_pdf.remote,
            file_bytes=dummy_pdf_bytes,
            filename="night_shift_test.pdf"
        )
        print("\n✅ Night Shift Result:")
        print(response)
    except Exception as e:
        print(f"❌ Execution Failed: {e}")

if __name__ == "__main__":
    asyncio.run(trigger_night_shift())
