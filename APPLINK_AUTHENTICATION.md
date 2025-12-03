# AppLink Authentication Integration

## Overview

Your Heroku app now supports **AppLink authentication** for Salesforce API calls. When requests come through AppLink, the service mesh automatically injects authentication headers, eliminating the need for OAuth2 password flow.

## How It Works

### AppLink Request Flow

```
Salesforce → AppLink Service Mesh → Heroku App
                ↓
        Injects Auth Headers:
        - Authorization: Bearer <token>
        - X-Salesforce-Instance-Url: <instance_url>
        - X-Salesforce-Org-Id: <org_id>
```

### Authentication Priority

The app now checks for authentication in this order:

1. **AppLink Headers** (Highest Priority)
   - Checks for `Authorization` header
   - Uses `X-Salesforce-Instance-Url` if provided
   - No OAuth2 needed - authentication is automatic

2. **Existing Access Token**
   - Uses cached token if available

3. **OAuth2 Fallback** (Lowest Priority)
   - Falls back to OAuth2 password flow if AppLink headers not present
   - Maintains backward compatibility

## Code Changes

### 1. Updated `/upload` Endpoint (`backend/main.py`)

The upload endpoint now extracts AppLink headers from the request:

```python
@app.post("/upload")
async def upload_file(
    request: Request,  # Added Request parameter
    file: UploadFile = File(...),
    record_id: str = Form(...),
    file_name: str = Form(...)
):
    # Extract AppLink headers
    auth_header = request.headers.get("Authorization")
    instance_url = request.headers.get("X-Salesforce-Instance-Url")
    
    # Pass to Salesforce API
    salesforce_result = await salesforce_api.upload_file_to_record(
        record_id, 
        file_path, 
        file_name,
        applink_auth_token=auth_header,
        applink_instance_url=instance_url
    )
```

### 2. Updated `upload_file_to_record` Method (`backend/salesforce_integration.py`)

The method now accepts AppLink authentication:

```python
async def upload_file_to_record(
    self, 
    record_id: str, 
    file_path: str, 
    file_name: str,
    applink_auth_token: Optional[str] = None,  # New parameter
    applink_instance_url: Optional[str] = None  # New parameter
) -> Dict[str, Any]:
    # Use AppLink auth if provided
    if applink_auth_token:
        self.access_token = applink_auth_token
        if applink_instance_url:
            self.base_url = applink_instance_url
    # Fallback to OAuth2 if no AppLink headers
    elif not self.access_token:
        await self.authenticate()
```

## Benefits

### ✅ Automatic Authentication
- No need to manage OAuth2 credentials
- No security tokens required
- Authentication handled by AppLink service mesh

### ✅ User Context
- Automatically uses the Salesforce user context from the request
- No need to specify which user to authenticate as

### ✅ Backward Compatible
- Still works with OAuth2 if AppLink headers not present
- Existing functionality preserved

### ✅ More Secure
- Tokens are managed by AppLink
- No credentials stored in environment variables
- Tokens are request-scoped

## Testing

### Test AppLink Authentication

1. **Call from Salesforce via AppLink:**
   - Use the published external service
   - AppLink will automatically inject headers
   - Check logs for "Using AppLink authentication"

2. **Test Direct Call (OAuth2 fallback):**
   - Call the endpoint directly (not through AppLink)
   - Should fall back to OAuth2
   - Check logs for "attempting OAuth2 authentication"

### Log Messages to Look For

**AppLink Authentication:**
```
=== APPLINK AUTHENTICATION CHECK ===
Authorization header: SET
Using AppLink authentication
AppLink access token set. Length: XXX
```

**OAuth2 Fallback:**
```
Access token not available, attempting OAuth2 authentication...
Using OAuth2 authentication
```

## Troubleshooting

### Issue: AppLink headers not present

**Symptoms:**
- Logs show "Authorization header: NOT SET"
- Falls back to OAuth2

**Solutions:**
1. Verify the request is coming through AppLink
2. Check that the external service is properly published
3. Ensure the request is made from Salesforce (Apex/Flow), not directly

### Issue: Authentication still fails

**Symptoms:**
- AppLink headers are present but API calls fail

**Solutions:**
1. Check the Authorization header format
2. Verify the instance URL is correct
3. Check user permissions in Salesforce
4. Review Heroku logs for detailed error messages

## Configuration

### No Configuration Needed!

AppLink authentication works automatically when:
- ✅ Heroku AppLink add-on is provisioned
- ✅ App is published to Salesforce
- ✅ Requests come through AppLink service mesh

### Environment Variables (Still Needed for Fallback)

If AppLink headers are not present, the app falls back to OAuth2 using:
- `SALESFORCE_INSTANCE_URL`
- `SALESFORCE_CLIENT_ID`
- `SALESFORCE_CLIENT_SECRET`
- `SALESFORCE_USERNAME`
- `SALESFORCE_PASSWORD`
- `SALESFORCE_SECURITY_TOKEN`

These are only used as a fallback when AppLink is not available.

## Next Steps

1. **Deploy to Heroku:**
   ```bash
   git add backend/main.py backend/salesforce_integration.py
   git commit -m "Add AppLink authentication support"
   git push heroku main
   ```

2. **Test the Integration:**
   - Make a request through AppLink
   - Check logs to verify AppLink authentication is used
   - Test file upload functionality

3. **Monitor Logs:**
   ```bash
   heroku logs --tail --app democomponent-qrcode-generator
   ```

## References

- [Heroku AppLink Documentation](https://devcenter.heroku.com/articles/heroku-applink)
- [AppLink Service Mesh](https://devcenter.heroku.com/articles/heroku-applink-service-mesh)
- [External Services in Salesforce](https://help.salesforce.com/s/articleView?id=sf.external_services.htm)

