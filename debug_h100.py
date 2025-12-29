
import modal

app = modal.App("debug-h100")

@app.function()
def square(x):
    print("Running on remote...")
    return x**2

@app.local_entrypoint()
def main():
    print("Connecting to Modal...")
    print(f"Result: {square.remote(42)}")
