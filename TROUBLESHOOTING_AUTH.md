# Troubleshooting Authentication Issues

## Current Status

✅ **Password is correct:** `Salesforce1!` (12 characters)  
✅ **All config vars are set**  
❌ **Still getting `invalid_grant: authentication failure`**

## Most Likely Causes & Solutions

### 1. Security Token Issue (Most Common)

**Problem:** Security token might be wrong, expired, or not matching the password.

**Solution:**
1. Reset the security token:
   - Setup → My Personal Information → Reset My Security Token
   - Click "Reset Security Token"
   - **Check your email** for the new token
2. Update Heroku immediately:
   ```bash
   heroku config:set SALESFORCE_SECURITY_TOKEN="NEW_TOKEN_FROM_EMAIL" --app democomponent-qrcode-generator
   heroku restart --app democomponent-qrcode-generator
   ```

**Important:** Security tokens expire when you change your password. If you changed your password recently, you MUST reset the token.

---

### 2. Instance URL Issue (Common Fix)

**Problem:** OAuth2 password flow sometimes requires `login.salesforce.com` instead of My Domain URL.

**Solution:** The code now automatically tries `login.salesforce.com` as a fallback. But you can also set it explicitly:

```bash
heroku config:set SALESFORCE_INSTANCE_URL="https://login.salesforce.com" --app democomponent-qrcode-generator
heroku restart --app democomponent-qrcode-generator
```

**Note:** The code will still use the returned `instance_url` from OAuth2 response for API calls, so this is safe.

---

### 3. Connected App Configuration

**Verify these settings in Salesforce:**

1. **Go to:** Setup → App Manager → Your Connected App
2. **Click:** Your Connected App name
3. **Check:**
   - ✅ **Enable OAuth Settings:** CHECKED
   - ✅ **Callback URL:** Can be `https://localhost` or `http://localhost` (doesn't matter for password flow)
   - ✅ **Selected OAuth Scopes:** Must include `Access and manage your data (api)` or `Full access (full)`
   - ✅ **IP Relaxation:** Set to **"Relax IP restrictions"**
   - ✅ **Require Secret for Web Server Flow:** Can be checked or unchecked

4. **Click:** Manage → View
5. **Verify:**
   - Consumer Key matches `SALESFORCE_CLIENT_ID`
   - Consumer Secret matches `SALESFORCE_CLIENT_SECRET`

---

### 4. User Account Issues

**Check the Salesforce user account:**

1. **Go to:** Setup → Users → Users
2. **Find:** `trailsignup.a59cbb1bc47f48@salesforce.com`
3. **Verify:**
   - ✅ User Status: **Active**
   - ✅ User License: Valid
   - ✅ Profile/Permission Set has: **API Enabled**
   - ✅ Profile/Permission Set has: **Create** permission on ContentVersion
   - ✅ Profile/Permission Set has: **Create** permission on ContentDocumentLink

4. **Check for restrictions:**
   - ❌ User is NOT locked
   - ❌ Password does NOT expire at next login
   - ❌ User does NOT require MFA (Multi-Factor Authentication)

**If MFA is required:**
- Create an "API Only" user without MFA
- OR use a Connected App with "Require Secret for Web Server Flow" and configure it properly

---

### 5. Test Authentication Locally

Run the test script to isolate the issue:

```bash
# Set environment variables (or it will prompt you)
export SALESFORCE_CLIENT_ID="your_client_id"
export SALESFORCE_CLIENT_SECRET="your_client_secret"
export SALESFORCE_USERNAME="trailsignup.a59cbb1bc47f48@salesforce.com"
export SALESFORCE_PASSWORD="Salesforce1!"
export SALESFORCE_SECURITY_TOKEN="your_token"

# Run test
python3 test_salesforce_auth.py
```

This will test:
1. My Domain URL authentication
2. `login.salesforce.com` authentication (fallback)
3. Show detailed error messages

---

### 6. Verify Config Vars Are Set Correctly

```bash
# View all Salesforce vars
heroku config --app democomponent-qrcode-generator | grep SALESFORCE

# Check each one individually
heroku config:get SALESFORCE_INSTANCE_URL --app democomponent-qrcode-generator
heroku config:get SALESFORCE_CLIENT_ID --app democomponent-qrcode-generator
heroku config:get SALESFORCE_CLIENT_SECRET --app democomponent-qrcode-generator
heroku config:get SALESFORCE_USERNAME --app democomponent-qrcode-generator
heroku config:get SALESFORCE_PASSWORD --app democomponent-qrcode-generator
heroku config:get SALESFORCE_SECURITY_TOKEN --app democomponent-qrcode-generator
```

**Check for:**
- No extra spaces or newlines
- No quotes around values (Heroku adds them automatically)
- Values match exactly what's in Salesforce

---

### 7. Test with curl (Direct API Test)

Test OAuth2 directly without Heroku:

```bash
curl -X POST "https://login.salesforce.com/services/oauth2/token" \
  -d "grant_type=password" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "username=trailsignup.a59cbb1bc47f48@salesforce.com" \
  -d "password=Salesforce1!YOUR_SECURITY_TOKEN"
```

**Note:** In curl, manually concatenate password + token. In Heroku config, they're separate.

**Expected success response:**
```json
{
  "access_token": "00D...",
  "instance_url": "https://trailsignup-a59cbb1bc47f48.my.salesforce.com",
  "id": "https://login.salesforce.com/id/...",
  "token_type": "Bearer",
  "issued_at": "1234567890",
  "signature": "..."
}
```

**If curl fails:** The issue is with Salesforce configuration (credentials, Connected App, or user).

**If curl succeeds:** The issue is with how Heroku config vars are set or how the code reads them.

---

## Step-by-Step Debugging Process

1. **Reset security token** (most common fix)
   ```bash
   # Get new token from Salesforce email
   heroku config:set SALESFORCE_SECURITY_TOKEN="NEW_TOKEN" --app democomponent-qrcode-generator
   heroku restart --app democomponent-qrcode-generator
   ```

2. **Try login.salesforce.com**
   ```bash
   heroku config:set SALESFORCE_INSTANCE_URL="https://login.salesforce.com" --app democomponent-qrcode-generator
   heroku restart --app democomponent-qrcode-generator
   ```

3. **Test with curl** (see above)

4. **Check Connected App settings** (see section 3)

5. **Check user permissions** (see section 4)

6. **Run local test script** (see section 5)

7. **Check Heroku logs** for detailed error messages:
   ```bash
   heroku logs --tail --app democomponent-qrcode-generator
   ```

---

## Quick Fix Checklist

- [ ] Reset security token and update Heroku
- [ ] Try `login.salesforce.com` as instance URL
- [ ] Verify Connected App OAuth settings
- [ ] Verify user has "API Enabled" permission
- [ ] Test with curl command
- [ ] Check Heroku logs for detailed errors
- [ ] Restart Heroku app after any config changes

---

## Still Not Working?

If none of the above works, check:

1. **Is this a Sandbox org?** Some sandbox orgs have different OAuth endpoints
2. **Is the org using My Domain?** Sometimes My Domain needs to be activated
3. **Are there IP restrictions at the org level?** (not just Connected App level)
4. **Is the user in a different org?** Verify the username matches the instance URL

Share the exact error message from Heroku logs for further diagnosis.

