# Token Flow - Where Each Token Needs to Be

## Overview

For file uploads to work, you need **ONE** of these authentication methods:

1. **Session ID from Form** (Preferred for browser requests) ⭐
2. **AppLink Headers** (For requests from Salesforce)
3. **OAuth2** (Fallback - requires Client ID, Client Secret, Username, Password, Security Token)

---

## Method 1: Session ID from Form (What We're Trying to Use)

### Flow:
```
Salesforce LWC
    ↓
Gets Session ID (UserInfo.getSessionId())
    ↓
Includes in QR Code URL: ?session_token=00DJ9000001lQog!...
    ↓
Form Page (Browser)
    ↓
Reads session_token from URL
    ↓
Sets hidden input field: <input name="session_token" value="00DJ9000001lQog!...">
    ↓
Form submits to /upload endpoint
    ↓
Backend receives: session_token from Form()
    ↓
Creates: auth_header = "Bearer " + session_token
    ↓
Passes to: salesforce_api.upload_file_to_record(applink_auth_token=auth_header)
    ↓
Salesforce API uses: self.access_token = applink_auth_token
    ↓
Makes API calls with: Authorization: Bearer <session_token>
```

### Where Session ID Needs to Be:

1. **In LWC (Salesforce):**
   - ✅ Retrieved via: `getSessionToken()` Apex method
   - ✅ Logged in console on component load
   - ✅ Included in QR code URL: `?session_token=00DJ9000001lQog!...`

2. **In Form Page (Browser):**
   - ✅ Read from URL: `urlParams.get('session_token')`
   - ✅ Set in hidden field: `<input name="session_token" value="...">`
   - ✅ Logged in console on page load

3. **In Backend (Heroku):**
   - ✅ Received as: `session_token: str = Form("")` parameter
   - ✅ Converted to: `auth_header = f"Bearer {session_token}"`
   - ✅ Passed to: `upload_file_to_record(applink_auth_token=auth_header)`

4. **In Salesforce API (`salesforce_integration.py`):**
   - ✅ Received as: `applink_auth_token` parameter
   - ✅ Set as: `self.access_token = applink_auth_token` (removes "Bearer " prefix if present)
   - ✅ Used in API calls: `Authorization: Bearer {self.access_token}`

---

## Method 2: AppLink Headers (For Requests from Salesforce)

### Flow:
```
Salesforce (Apex/Flow)
    ↓
Makes HTTP call to Heroku
    ↓
AppLink Service Mesh (automatically injects headers)
    ↓
Heroku receives:
  - Authorization: Bearer <token>
  - X-Salesforce-Instance-Url: <url>
    ↓
Backend extracts: auth_header = request.headers.get("Authorization")
    ↓
Passes to Salesforce API
```

### Where AppLink Headers Need to Be:

1. **In Request Headers (Automatic):**
   - ✅ `Authorization: Bearer <token>` (injected by AppLink)
   - ✅ `X-Salesforce-Instance-Url: <url>` (injected by AppLink)

2. **In Backend:**
   - ✅ Extracted: `applink_auth = request.headers.get("Authorization")`
   - ✅ Passed to: `upload_file_to_record(applink_auth_token=applink_auth)`

**Note:** This ONLY works when requests come FROM Salesforce, not from browser requests.

---

## Method 3: OAuth2 Fallback (Current Fallback)

### Flow:
```
Backend (Heroku)
    ↓
No Session ID or AppLink headers
    ↓
Falls back to OAuth2
    ↓
Uses Heroku Config Vars:
  - SALESFORCE_CLIENT_ID
  - SALESFORCE_CLIENT_SECRET
  - SALESFORCE_USERNAME
  - SALESFORCE_PASSWORD
  - SALESFORCE_SECURITY_TOKEN
    ↓
Makes OAuth2 request: POST /services/oauth2/token
    ↓
Gets access_token from response
    ↓
Uses access_token for API calls
```

### Where OAuth2 Credentials Need to Be:

1. **In Heroku Config Vars:**
   - ✅ `SALESFORCE_CLIENT_ID` - Consumer Key from Connected App
   - ✅ `SALESFORCE_CLIENT_SECRET` - Consumer Secret from Connected App
   - ✅ `SALESFORCE_USERNAME` - Your Salesforce username
   - ✅ `SALESFORCE_PASSWORD` - Your password (ONLY password, no token)
   - ✅ `SALESFORCE_SECURITY_TOKEN` - 24-char security token
   - ✅ `SALESFORCE_INSTANCE_URL` - Your Salesforce instance URL

2. **In Backend (`salesforce_integration.py`):**
   - ✅ Read from: `os.getenv('SALESFORCE_CLIENT_ID')`
   - ✅ Used in: `authenticate()` method for OAuth2 flow
   - ✅ Result: `self.access_token` is set after successful OAuth2

---

## Current Status

### ✅ What's Working:
- **Client ID:** Set in Heroku config vars
- **Client Secret:** Set in Heroku config vars
- **Username:** Set in Heroku config vars
- **Password:** Set in Heroku config vars
- **Security Token:** Set in Heroku config vars
- **OAuth2 Fallback:** Configured (but failing due to auth issues)

### ❌ What's NOT Working:
- **Session ID from Form:** Not reaching backend
  - LWC gets it ✅
  - QR code includes it ✅
  - Form page should read it ❓
  - Backend should receive it ❓

---

## The Problem

The session token is **NOT reaching the backend**. Here's where it should be at each step:

1. **LWC Console:** Should show Session ID ✅ (we just added logging)
2. **QR Code URL:** Should include `?session_token=...` ✅ (confirmed in logs)
3. **Form Page Console:** Should show session token from URL ❓ (check after deployment)
4. **Form Hidden Field:** Should have value set ❓ (check after deployment)
5. **Backend Logs:** Should show `session_token from Form(): '00DJ9000001lQog!...'` ❌ (currently empty)

---

## What to Check

### Step 1: LWC Console (Salesforce)
When you load the LWC component, check browser console:
```
=== LWC COMPONENT LOADED ===
=== SESSION INFORMATION ===
Session ID (from UserInfo.getSessionId()): 00DJ9000001lQog!...
```

### Step 2: QR Code Generation Console
When you generate QR code, check console:
```
=== SESSION TOKEN RETRIEVED (QR Code Generation) ===
Session ID: 00DJ9000001lQog!...
Form URL created: ...?session_token=00DJ9000001lQog!...
```

### Step 3: Form Page Console (Browser)
When you open the form page, check console:
```
=== FORM PAGE LOAD DEBUG ===
=== SESSION TOKEN FROM URL ===
session_token (full): 00DJ9000001lQog!...
```

### Step 4: Backend Logs (Heroku)
When you submit the form, check Heroku logs:
```
=== FASTAPI FORM PARAMETERS ===
session_token from Form(): '00DJ9000001lQog!...'  ← Should NOT be empty!
```

---

## Summary

**Session ID (Access Token) Flow:**
- **Source:** Salesforce LWC → `UserInfo.getSessionId()`
- **Transport:** QR Code URL → Form hidden field → Backend Form parameter
- **Usage:** Backend → `Bearer {session_token}` → Salesforce API calls

**Client ID:**
- **Location:** Heroku Config Var `SALESFORCE_CLIENT_ID`
- **Usage:** Only for OAuth2 fallback (not needed if session token works)

**Access Token:**
- **For Session ID method:** Session ID IS the access token
- **For OAuth2 method:** Obtained via OAuth2 flow, stored in `self.access_token`
- **Usage:** Both are used the same way: `Authorization: Bearer {token}`

---

## Next Steps

1. **Test with new logging:**
   - Check LWC console for Session ID
   - Check form page console for session token from URL
   - Check Heroku logs for session token received

2. **If session token still not received:**
   - The issue is in the form JavaScript (hidden field not being set)
   - Or FastAPI not parsing the form field correctly

3. **If OAuth2 is still failing:**
   - Verify credentials are correct
   - Check Connected App settings
   - Verify user permissions

