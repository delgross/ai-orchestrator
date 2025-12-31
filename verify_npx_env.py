
import asyncio
import os
import sys

# Mimicking agent_runner/transports/stdio.py logic
async def test_npx_invocation():
    print(f"Testing NPX invocation...")
    
    cmd = ["npx", "-y", "tavily-mcp@0.1.3"]
    
    # Define the secret in the environment dict
    env_vars = os.environ.copy()
    env_vars["TAVILY_API_KEY"] = "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"  # Using the real key key for repro
    
    print(f"Command: {cmd}")
    print(f"Env 'TAVILY_API_KEY' set: {'TAVILY_API_KEY' in env_vars}")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env_vars,
        )
        
        # Give it a second to fail or start
        try:
            # Tavily usually exits instantly if key is missing 
            # or waits for input if successful
            
            # We try to read stderr
            stderr_data = await asyncio.wait_for(proc.stderr.read(1024), timeout=3.0)
            if stderr_data:
                print(f"STDERR Output: {stderr_data.decode()}")
            else:
                print("No STDERR output (Process started successfully?)")
                
        except asyncio.TimeoutError:
             print("Process is running (Timeout on stderr read). This implies SUCCESS.")
             proc.kill()

        if proc.returncode is not None:
            print(f"Process exited with code: {proc.returncode}")
        else:
            print("Process is still running.")
            proc.terminate()
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_npx_invocation())
