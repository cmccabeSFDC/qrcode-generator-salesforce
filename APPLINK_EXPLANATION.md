# AppLink Authentication - What You Need to Know

## The Core Issue

**AppLink ONLY works when requests come FROM Salesforce**, not from browser requests.

### How AppLink Works

```
Salesforce (Apex/Flow) 
    ↓
AppLink Service Mesh (automatically injects headers)
    ↓
Heroku App (receives headers)
```

**AppLink automatically injects:**
- `Authorization: Bearer <session_token>`
- `X-Salesforce-Instance-Url: <instance_url>`
- `X-Salesforce-Org-Id: <org_id>`

### Your Current Flow

```
User scans QR code
    ↓
Opens form in browser (DIRECT HTTP request)
    ↓
Browser submits form
    ↓
Heroku App (NO AppLink headers - it's a browser request!)
```

**Result:** AppLink headers are NOT present because the request didn't come from Salesforce.

---

## Current Solution: Session Token from Form

Since AppLink won't work for browser requests, we're passing the session token manually:

1. **LWC gets session token** from Apex (`getSessionToken()`)
2. **QR code URL includes** `session_token` parameter
3. **Form JavaScript reads** token from URL
4. **Form sends token** as form field
5. **Backend uses token** for Salesforce API calls

### What's Going Wrong

The logs show:
- ✅ Session token IS in the QR code URL
- ❌ Session token is NOT reaching the backend
- ❌ Falls back to OAuth2 (which is failing)

**Possible causes:**
1. JavaScript isn't reading token from URL correctly
2. FormData isn't including the token
3. FastAPI isn't parsing the form field

---

## What AppLink Needs (For Future Reference)

If you want to use AppLink, you need to make the upload request FROM Salesforce:

### Option 1: Apex Callout from LWC

```apex
// In QRCodeService.cls
@AuraEnabled
public static String uploadFileToHeroku(String recordId, String fileName, Blob fileContent) {
    HttpRequest req = new HttpRequest();
    req.setEndpoint('https://your-app.herokuapp.com/upload');
    req.setMethod('POST');
    // ... set body with file
    Http http = new Http();
    HttpResponse res = http.send(req);
    return res.getBody();
}
```

**This would work with AppLink** because the request comes from Salesforce.

### Option 2: Current Approach (What We're Doing)

Pass session token manually through the form - this works for browser requests but requires the token to be passed correctly.

---

## Debugging Steps

1. **Check browser console** when submitting form:
   - Should see: `DEBUG: sessionToken from URL: SET (...)...`
   - Should see: `DEBUG: Added session_token to FormData`
   - Should see: `DEBUG: FormData entries:` with session_token listed

2. **Check Heroku logs** for:
   - `=== FASTAPI FORM PARAMETERS ===`
   - `session_token from Form(): '...'`
   - Should NOT be empty string

3. **If session_token is empty:**
   - JavaScript isn't reading it from URL
   - FormData isn't including it
   - Check browser console for errors

---

## Next Steps

1. **Deploy the latest code** (with improved logging)
2. **Test and check:**
   - Browser console output
   - Heroku logs (especially `=== FASTAPI FORM PARAMETERS ===`)
3. **If still not working:**
   - The issue is in the JavaScript form submission
   - We may need to use a different approach (e.g., hidden input fields instead of FormData.append)

---

## Summary

- **AppLink won't work** for browser requests (your current flow)
- **Session token approach** should work, but token isn't reaching backend
- **New logging** will show exactly where it's failing
- **Once fixed**, the session token will be used instead of OAuth2

