
import os
from dotenv import load_dotenv

print("--- DEBUG TOKEN LOAD ---")
# Mimic router/config.py loading order
load_dotenv("providers.env")
print(f"After providers.env: {os.getenv('ROUTER_AUTH_TOKEN')}")
load_dotenv() # .env
print(f"After .env: {os.getenv('ROUTER_AUTH_TOKEN')}")
load_dotenv("router.env")
print(f"After router.env: {os.getenv('ROUTER_AUTH_TOKEN')}")

token = os.getenv("ROUTER_AUTH_TOKEN", "antigravity_router_token_2025")
print(f"FINAL EFFECTIVE TOKEN: {token}")
print("------------------------")
