# Load stdlib modules manually
libraries = []
libraries.extend(["json", "logging", "asyncio", "typing", "pathlib", "datetime", "sys", "os", "time", "contextlib", "abc", "subprocess", "signal", "dataclasses", "enum", "re", "io", "traceback", "uuid", "math", "collections", "functools", "itertools", "random", "hashlib", "secrets", "shutil", "tempfile", "glob", "argparse", "inspect", "platform", "threading", "queue", "weakref", "site", "importlib", "builtins", "copy", "types", "yaml", "dotenv", "uvicorn", "fastapi", "httpx", "pydantic", "watchdog", "surrealdb", "tenacity", "mcp"])

# Known third-party mappings (Import Name -> PyPI Name)
MAPPING = {
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
    "surrealdb": "surrealdb",
    "fastapi": "fastapi",
    "pydantic": "pydantic",
    "uvicorn": "uvicorn",
    "httpx": "httpx",
    "watchdog": "watchdog",
    "mcp": "mcp",
    "tenacity": "tenacity",
    "sse_starlette": "sse-starlette", # Example if used
    "starlette": "starlette", # Dep of fastapi
    "multipart": "python-multipart",
    "click": "click", # Dep of uvicorn
    "h11": "h11",
    "sniffio": "sniffio",
    "anyio": "anyio",
    "idna": "idna",
    "certifi": "certifi",
    "distutils": "std", # Part of stdlib but sometimes flagged
}

# Add standard library additions
libraries.extend(["unittest", "doctest"])

def get_imports(file_path):
    with open(file_path, "r") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()
            
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def scan_directory(root_dir):
    all_imports = set()
    for root, dirs, files in os.walk(root_dir):
        if ".venv" in root or "__pycache__" in root or "tests" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                imports = get_imports(os.path.join(root, file))
                all_imports.update(imports)
    return all_imports

def main():
    root_dir = os.getcwd()
    imports = scan_directory(root_dir)
    
    # Filter out known local packages (agent_runner, router, common, etc)
    local_packages = {"agent_runner", "router", "common", "mcp_server", "tests", "scripts", "sdk", "bin"}
    
    unknown = []
    for imp in imports:
        if imp in libraries:
            continue
        if imp in local_packages:
            continue
        if imp in MAPPING:
            continue
        # Also check if it's a known dependency of our dependencies (approx)
        unknown.append(imp)
        
    print("Potential Missing Dependencies:")
    for u in sorted(unknown):
        print(f"- {u}")

if __name__ == "__main__":
    main()
