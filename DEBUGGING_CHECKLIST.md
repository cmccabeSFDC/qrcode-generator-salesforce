# Step-by-Step Debugging Checklist

## What to Check at Each Step

### Step 1: QR Code Generation (Salesforce Console)
**Location:** Salesforce browser console when generating QR code

**Check:**
- ✅ `Form URL created:` - Does it include `session_token=` parameter?
- ✅ `session_token=00DJ9000001lQog!...` - Is the token present?
- ✅ `instance_url=https://...` - Is the instance URL present?

**Expected:** Both should be in the URL

---

### Step 2: Form Page Load (Browser)
**Location:** The form page itself (visible debug box at top)

**Check:**
- ✅ **Debug box visible?** - Should see a gray box with "🔍 DEBUG INFORMATION"
- ✅ **Step 1: URL Parameters** - Shows full URL and URL search params
- ✅ **Step 2: Extracted Values** - Should show:
  - `session_token: ✓ FOUND (XXX chars, starts with: 00DJ9000001lQog...)`
  - `instance_url: ✓ FOUND (https://...)`

**If NOT FOUND:**
- The URL doesn't have the parameters
- JavaScript isn't reading them correctly

---

### Step 3: Form Submission (Browser Console)
**Location:** Browser console (F12) when submitting form

**Check:**
- ✅ `=== FORM SUBMISSION DEBUG ===`
- ✅ `DEBUG: sessionToken from URL: SET (...)...`
- ✅ `✓ Added session_token to FormData`
- ✅ `DEBUG: FormData entries:` - Should list `session_token: ...`

**Also check visible debug box:**
- Should update to show "FormData Contents:" with all entries including session_token

**If NOT SET:**
- JavaScript variable `sessionToken` is null/empty
- FormData.append isn't working

---

### Step 4: Backend Receives Request (Heroku Logs)
**Location:** Heroku logs when upload happens

**Check for these sections:**

#### 4a. FastAPI Form Parameters
```
=== FASTAPI FORM PARAMETERS ===
session_token from Form(): '00DJ9000001lQog!...'
session_token length: XXX
```

**If EMPTY:**
- FastAPI isn't receiving the form field
- FormData wasn't sent correctly

#### 4b. After Normalization
```
=== AFTER NORMALIZATION ===
session_token: 00DJ9000001lQog!... (was: '00DJ9000001lQog!...')
```

**If None:**
- Was empty string, got normalized to None

#### 4c. AppLink Headers
```
=== CHECKING APPLINK HEADERS ===
Authorization header: NOT SET
```

**Expected:** NOT SET (because it's a browser request, not from Salesforce)

#### 4d. Authentication Method Selection
```
=== AUTHENTICATION METHOD SELECTION ===
✓ Using session token from form
```

**If shows OAuth2 fallback:**
- Session token wasn't received
- Will fail with authentication error

#### 4e. Final Summary
```
=== FINAL VARIABLE STATUS SUMMARY ===
1. Form Parameters (from FastAPI):
   - session_token: ✓ SET (XXX chars)  OR  ✗ EMPTY/NONE
   - instance_url: ✓ SET (...)  OR  ✗ EMPTY/NONE
2. AppLink Headers (from request):
   - Authorization: ✗ NOT SET (expected for browser requests)
3. Selected Authentication:
   - Method: Session Token  OR  OAuth2 Fallback
```

---

## What Each Status Means

### ✅ All Steps Pass
- Session token flows correctly from Salesforce → Form → Backend
- Authentication should work

### ❌ Step 1 Fails (No token in URL)
- **Problem:** LWC isn't getting/adding session token
- **Fix:** Check Apex methods `getSessionToken()` and `getInstanceUrl()` are deployed
- **Fix:** Check LWC JavaScript is calling them and appending to URL

### ❌ Step 2 Fails (Token not found on form page)
- **Problem:** URL doesn't have parameters OR JavaScript isn't reading them
- **Fix:** Check the actual URL in browser address bar
- **Fix:** Check JavaScript console for errors

### ❌ Step 3 Fails (Token not in FormData)
- **Problem:** JavaScript variable is null OR FormData.append isn't working
- **Fix:** Check if `sessionToken` variable is set before form submission
- **Fix:** Try using hidden input fields instead of FormData.append

### ❌ Step 4 Fails (Backend doesn't receive token)
- **Problem:** FormData wasn't sent OR FastAPI isn't parsing it
- **Fix:** Check browser Network tab → see if form data includes session_token
- **Fix:** Check FastAPI Form parameter definition

---

## Quick Diagnosis

**If you see in Heroku logs:**
- `session_token from Form(): ''` → **Form field is empty string**
- `session_token from Form(): None` → **Form field wasn't sent**
- `✗ No AppLink headers or session token` → **Both failed, using OAuth2**

**If you see in browser:**
- Debug box shows `✗ NOT FOUND` → **URL doesn't have parameters**
- Debug box shows `✓ FOUND` but backend shows empty → **FormData not sending correctly**

---

## Next Steps After Testing

1. **Deploy to Heroku:**
   ```bash
   cd /Users/cmccabe/qr-code-generator/backend
   git push heroku main
   ```

2. **Test and collect:**
   - Screenshot of form page (showing debug box)
   - Browser console output
   - Heroku logs (especially the SUMMARY section)

3. **Share results** - This will show exactly where the token is being lost

