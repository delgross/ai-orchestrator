
import os

def check_file(filename):
    print(f"--- CHECKING {filename} ---")
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return

    try:
        with open(filename, 'rb') as f:
            content = f.read()
            print(f"Raw content (bytes): {content}")
            try:
                decoded = content.decode('utf-8')
                print(f"Decoded content:\n{decoded}")
                for line in decoded.splitlines():
                    if "ROUTER_AUTH_TOKEN" in line:
                        print(f"FOUND TOKEN LINE: >{line}<")
            except Exception as e:
                print(f"Could not decode utf-8: {e}")
    except Exception as e:
        print(f"Error reading file: {e}")

check_file(".env")
check_file("router.env")
check_file("providers.env")
