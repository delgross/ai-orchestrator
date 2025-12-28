# Router Authentication Setup

## Why Use a Router Token?

**YES, you should use a router token** for these reasons:

### Security Risks Without Token

1. **Dangerous Admin Endpoints Unprotected:**
   - `/admin/restart-router` - Can restart the router itself
   - `/admin/restart-agent` - Can restart agent-runner
   - `/admin/restart-all` - Can restart entire system
   - `/admin/stop-router` - Can stop the router
   - `/admin/stop-agent` - Can stop agent-runner
   - `/admin/cache/clear` - Can clear caches
   - `/admin/mcp-toggle` - Can enable/disable MCP access
   - `/admin/active-model` - Can change active model
   - `/admin/reload-providers` - Can reload providers

2. **Network Exposure:**
   - If router is accessible beyond localhost, anyone can call these endpoints
   - Even on localhost, browser extensions or malicious scripts could call them
   - No protection against accidental clicks or mistakes

3. **Production Readiness:**
   - When deploying, you'll need auth anyway
   - Better to set it up now than forget later

## How to Set It Up

### Option 1: Environment Variable (Recommended)

```bash
export ROUTER_AUTH_TOKEN="your-secret-token-here"
```

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export ROUTER_AUTH_TOKEN="your-secret-token-here"
```

### Option 2: config.yaml

Add to `config/config.yaml`:
```yaml
router:
  auth_token: "your-secret-token-here"
```

### Option 3: router.env

Create or edit `router.env`:
```
ROUTER_AUTH_TOKEN=your-secret-token-here
```

## Generate a Secure Token

```bash
# Generate a random token
openssl rand -hex 32

# Or use Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Using the Token

### In Dashboard

1. Open dashboard
2. Enter token in "auth-token" field (top of page)
3. Token is stored in browser (not sent to server until needed)
4. All admin buttons will work with token

### Via API

```bash
curl -X POST http://localhost:5455/admin/restart-agent \
  -H "Authorization: Bearer your-secret-token-here"
```

### In Code

```python
headers = {
    "Authorization": "Bearer your-secret-token-here"
}
```

## Current Behavior

- **Without token**: All admin endpoints are accessible (no protection)
- **With token**: All admin endpoints require `Authorization: Bearer <token>` header

## Recommendation

**Set a token now** - it's a simple security measure that protects against:
- Accidental admin actions
- Malicious scripts
- Future network exposure
- Production deployment issues

Even if you're only using localhost, it's good practice and takes 30 seconds to set up.






