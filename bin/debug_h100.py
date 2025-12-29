import modal

app = modal.App("debug-h100")

# Minimal image (no massive downloads)
image = modal.Image.debian_slim()

@app.function(image=image, gpu="H100")
def test_h100():
    import subprocess
    print("✅ H100 GPU Allocated Successfully!")
    # Print GPU info
    print(subprocess.check_output(["nvidia-smi"]).decode())

@app.local_entrypoint()
def main():
    print("⏳ Requesting H100 GPU...")
    test_h100.remote()
