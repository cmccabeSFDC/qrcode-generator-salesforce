# Authentication Diagnosis Guide

## Step-by-Step Diagnosis Process

### Step 1: Verify Session Token is in QR Code URL

**Action:** Generate a new QR code and check the form URL in the browser console.

1. Open Salesforce and generate a QR code
2. Open browser console (F12)
3. Look for the log: `Form URL created: ...`
4. **Check:** Does the URL contain `session_token=` parameter?

**Expected:** URL should look like:
```
https://democomponent-qrcode-generator-c48b26ff05fc.herokuapp.com/form/00QJ9000003uCB4MAM?company_logo_url=...&file_name=...&session_token=00DJ9000001lQog!AQcAQ...&instance_url=https://trailsignup-a59cbb1bc47f48.my.salesforce.com
```

**If NO session_token in URL:**
- The LWC isn't getting the session token
- Check: Is the Apex method `getSessionToken()` deployed?
- Check: Browser console for errors when generating QR code

---

### Step 2: Verify Form Reads Session Token from URL

**Action:** Open the form page and check browser console.

1. Scan/open the QR code form URL
2. Open browser console (F12)
3. Before submitting, add this to console:
```javascript
const urlParams = new URLSearchParams(window.location.search);
console.log('Session Token:', urlParams.get('session_token'));
console.log('Instance URL:', urlParams.get('instance_url'));
```

**Expected:** Should show the session token and instance URL

**If NO session_token in URL params:**
- The QR code URL doesn't include it (go back to Step 1)
- The form URL was generated before deploying the updated LWC

---

### Step 3: Verify Form Sends Authorization Header

**Action:** Check browser Network tab when submitting form.

1. Open browser DevTools → Network tab
2. Submit the form
3. Find the `/upload` request
4. Click on it → Headers tab
5. **Check:** Look for `Authorization` header in Request Headers

**Expected:** Should see:
```
Authorization: Bearer 00DJ9000001lQog!AQcAQ...
X-Salesforce-Instance-Url: https://trailsignup-a59cbb1bc47f48.my.salesforce.com
```

**If NO Authorization header:**
- The form JavaScript isn't reading the token from URL
- Check browser console for JavaScript errors
- The form HTML might not be updated on Heroku

---

### Step 4: Verify Backend Receives Header

**Action:** Check Heroku logs for the authentication check section.

Look for this in logs:
```
=== APPLINK AUTHENTICATION CHECK ===
Authorization header: SET
```

**If you see "Authorization header: NOT SET":**
- The form isn't sending the header (go back to Step 3)
- CORS might be blocking custom headers
- The backend code might not be deployed

**If you DON'T see this section at all:**
- The backend code hasn't been deployed to Heroku
- Need to deploy: `git push heroku main`

---

### Step 5: If OAuth2 Fallback is Used, Check Credentials

**If Steps 1-4 all pass but still fails, or if session token approach doesn't work:**

#### 5a. Verify Security Token is Current

**Action:** Reset the security token in Salesforce.

1. Log into Salesforce as `trailsignup.a59cbb1bc47f48@salesforce.com`
2. Click profile → Settings → Reset My Security Token
3. Check email for new token
4. Update Heroku:
```bash
heroku config:set SALESFORCE_SECURITY_TOKEN="NEW_TOKEN_HERE" --app democomponent-qrcode-generator-c48b26ff05fc
heroku restart --app democomponent-qrcode-generator-c48b26ff05fc
```

#### 5b. Verify Password is Correct

**Action:** Test password directly.

1. Try logging into Salesforce with the password
2. If password changed, update Heroku:
```bash
heroku config:set SALESFORCE_PASSWORD="NEW_PASSWORD" --app democomponent-qrcode-generator-c48b26ff05fc
heroku restart --app democomponent-qrcode-generator-c48b26ff05fc
```

#### 5c. Verify Connected App Settings

**Action:** Check Connected App in Salesforce Setup.

1. Setup → App Manager → Find your Connected App
2. Click → Manage → View
3. **Check:**
   - Consumer Key matches `SALESFORCE_CLIENT_ID` in Heroku
   - Consumer Secret matches `SALESFORCE_CLIENT_SECRET` in Heroku
   - OAuth Settings enabled
   - IP Relaxation: "Relax IP restrictions"

#### 5d. Test OAuth2 Directly

**Action:** Test authentication with curl.

```bash
# Get values from Heroku
heroku config:get SALESFORCE_CLIENT_ID --app democomponent-qrcode-generator-c48b26ff05fc
heroku config:get SALESFORCE_CLIENT_SECRET --app democomponent-qrcode-generator-c48b26ff05fc
heroku config:get SALESFORCE_USERNAME --app democomponent-qrcode-generator-c48b26ff05fc
heroku config:get SALESFORCE_PASSWORD --app democomponent-qrcode-generator-c48b26ff05fc
heroku config:get SALESFORCE_SECURITY_TOKEN --app democomponent-qrcode-generator-c48b26ff05fc

# Test (replace with actual values)
curl -X POST "https://trailsignup-a59cbb1bc47f48.my.salesforce.com/services/oauth2/token" \
  -d "grant_type=password" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "username=trailsignup.a59cbb1bc47f48@salesforce.com" \
  -d "password=YOUR_PASSWORD+YOUR_SECURITY_TOKEN"
```

**Expected:** Should return `{"access_token":"...","instance_url":"..."}`

**If it fails:** The issue is with OAuth2 credentials (password, token, or Connected App)

---

## Quick Diagnostic Checklist

Run through these in order:

- [ ] **Step 1:** Session token in QR code URL? (Check browser console)
- [ ] **Step 2:** Form can read session token from URL? (Check browser console)
- [ ] **Step 3:** Form sends Authorization header? (Check Network tab)
- [ ] **Step 4:** Backend receives Authorization header? (Check Heroku logs for "APPLINK AUTHENTICATION CHECK")
- [ ] **Step 5a:** Security token is current? (Reset if needed)
- [ ] **Step 5b:** Password is correct? (Test login)
- [ ] **Step 5c:** Connected App settings correct? (Check Setup)
- [ ] **Step 5d:** OAuth2 works with curl? (Test directly)

---

## Most Likely Issues (Based on Your Logs)

Based on your logs showing "Access token: NOT SET" and no "APPLINK AUTHENTICATION CHECK" section:

1. **Backend code not deployed** - The updated `main.py` with session token support isn't on Heroku
2. **Form not sending header** - The form JavaScript isn't reading/using the session token
3. **Session token expired** - The token in the QR code URL expired before use

**Next Action:** Start with Step 1 - check if the QR code URL includes the session_token parameter.


