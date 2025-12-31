
import logging
from agent_runner.modal_tasks import has_modal, app

def main():
    print(f"Modal Detected: {has_modal}")
    if has_modal:
        print(f"App Name: {app.name}")
        print("✅ Modal library is active and integrated.")
    else:
        print("❌ Modal library NOT detected (ImportFailed).")

if __name__ == "__main__":
    main()
