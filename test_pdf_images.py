
import pypdf
import os

file_path = "./agent_fs_root/ingest/Skidloader Manual.pdf"

try:
    reader = pypdf.PdfReader(file_path)
    print(f"Pages: {len(reader.pages)}")
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"Page {i+1} text length: {len(text) if text else 0}")
        
        # Check images
        if hasattr(page, "images") and page.images:
            print(f"Page {i+1} has {len(page.images)} images.")
            for img in page.images:
                print(f"  - Image: {img.name} ({len(img.data)} bytes)")
        else:
            print(f"Page {i+1} has NO images.")

except Exception as e:
    print(f"Error: {e}")
