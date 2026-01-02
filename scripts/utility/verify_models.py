
import os
import yaml
import asyncio
import logging
from typing import List, Dict
import httpx
from dotenv import load_dotenv

# Load env vars
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("model_verifier")

async def verify_model(client: httpx.AsyncClient, base_url: str, api_key: str, model_id: str, provider: str) -> bool:
    """
    Verifies a single model by sending a 'hello' request.
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # xAI sometimes requires specific headers? No, standard OpenAI compat usually fine.
    # Google might require 'x-goog-api-key' query param or header if not using strict OpenAI compat proxy? 
    # But config says type: openai_compat, and base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    # Google's OpenAI compat endpoint supports standard Bearer auth usually, but sometimes prefers x-goog-api-key.
    # Let's try standard Bearer first.
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Say 'ok'."}],
        "max_tokens": 5
    }
    
    try:
        if "googleapis" in base_url:
             # Google sometimes acts weird with trailing slashes
             if not base_url.endswith("/"): base_url += "/"
             # Correction: Google OpenAI compat base follows specific pattern
        
        response = await client.post(url, json=payload, headers=headers, timeout=15.0)
        
        if response.status_code == 200:
            logger.info(f"✅ [PASS] {provider.upper()} : {model_id}")
            return True
        else:
            logger.error(f"❌ [FAIL] {provider.upper()} : {model_id} (Status: {response.status_code}) - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ [FAIL] {provider.upper()} : {model_id} (Exception: {e})")
        return False

async def main():
    print("Starting Model Verification...\n")
    
    # Load Config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    providers = config.get("providers", {})
    
    # Models to test
    models_to_test = [
        ("google", "gemini-1.5-pro"),
        ("google", "gemini-exp-1206"),
        ("google", "gemini-3-pro-preview"), 
        ("google", "gemini-3-flash-preview"),
        ("xai", "grok-4-1-fast-reasoning"),
        ("xai", "grok-4-1-fast-non-reasoning"),
        ("xai", "grok-4-fast-reasoning"),
        ("xai", "grok-4-fast-non-reasoning"),
        ("xai", "grok-code-fast-1")
    ]
    
    async with httpx.AsyncClient() as client:
        for provider_name, model_id in models_to_test:
            provider_conf = providers.get(provider_name)
            if not provider_conf:
                logger.warning(f"Skipping {model_id}: Provider '{provider_name}' not found in config.")
                continue
                
            base_url = provider_conf.get("base_url")
            api_key_env = provider_conf.get("api_key_env")
            api_key = os.getenv(api_key_env)
            
            if not api_key:
                 logger.warning(f"Skipping {model_id}: API Key ({api_key_env}) not found in .env.")
                 continue
                 
            # Strip trailing slash from base_url if sending to /chat/completions manually
            if base_url.endswith("/"): base_url = base_url[:-1]
            
            await verify_model(client, base_url, api_key, model_id, provider_name)

if __name__ == "__main__":
    asyncio.run(main())
