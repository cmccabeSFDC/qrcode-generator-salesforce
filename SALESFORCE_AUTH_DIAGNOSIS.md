# Salesforce Authentication Diagnosis Guide

## Most Common Causes of 400 Bad Request

### 1. **Connected App Configuration Issues**

**Check in Salesforce Setup:**
1. Go to Setup → App Manager → Find your Connected App
2. **OAuth Settings must include:**
   - ✅ Enable OAuth Settings: **CHECKED**
   - ✅ Callback URL: Can be `https://localhost` or `http://localhost` (or your Heroku URL)
   - ✅ Selected OAuth Scopes: Must include at least one of:
     - `Access and manage your data (api)`
     - `Perform requests on your behalf at any time (refresh_token, offline_access)`
     - `Full access (full)`
   - ✅ Enable Client Credentials Flow: Usually **NOT** needed for password flow
   - ✅ IP Relaxation: Should be set to **"Relax IP restrictions"** or include Heroku IPs

### 2. **User Permissions**

**Check the Salesforce User:**
1. Go to Setup → Users → Find your user
2. **Verify:**
   - ✅ User is **Active**
   - ✅ User has **API Enabled** permission (Profile or Permission Set)
   - ✅ User has permissions to create ContentVersion and ContentDocumentLink

### 3. **Security Token Issues**

**Common Problems:**
- Security token might be expired (reset it if needed)
- Security token might be wrong (get new one from: Setup → My Personal Information → Reset My Security Token)
- Password format: `password + security_token` (no space, concatenated)

### 4. **Heroku Config Vars**

**Required Variables:**
```
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_CLIENT_ID=your_client_id
SALESFORCE_CLIENT_SECRET=your_client_secret
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
```

**Verify these are set correctly:**
```bash
heroku config --app democomponent-qrcode-generator
```

## What to Check/Share

### 1. **Connected App Consumer Key & Secret**
- Consumer Key = Client ID
- Consumer Secret = Client Secret
- Verify these match what's in Heroku config vars

### 2. **Instance URL Format**
- Should be: `https://trailsignup-a59cbb1bc47f48.my.salesforce.com` (your current one)
- OR: `https://yourdomain.salesforce.com`
- OR: `https://login.salesforce.com` (if using production)
- **NOT**: `https://your-instance.salesforce.com` (placeholder)

### 3. **User Profile/Permission Set**
- User needs: **API Enabled**
- User needs: **Create** permission on ContentVersion
- User needs: **Create** permission on ContentDocumentLink

### 4. **Test Authentication Locally**

You can test the exact credentials with this curl command:

```bash
curl -X POST "https://trailsignup-a59cbb1bc47f48.my.salesforce.com/services/oauth2/token" \
  -d "grant_type=password" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "username=YOUR_USERNAME" \
  -d "password=YOUR_PASSWORD+YOUR_SECURITY_TOKEN"
```

If this works, the issue is with Heroku config vars.
If this fails, the issue is with Salesforce setup.

## Process of Elimination

### Step 1: Verify Config Vars are Set
```bash
heroku config --app democomponent-qrcode-generator | grep SALESFORCE
```

### Step 2: Check Connected App Settings
Share (without sensitive data):
- Is "Enable OAuth Settings" checked? ✅/❌
- What OAuth Scopes are selected?
- What is the Callback URL set to?
- What is IP Relaxation set to?

### Step 3: Check User Permissions
- Is the user Active? ✅/❌
- Does the user have "API Enabled"? ✅/❌
- What Profile/Permission Set does the user have?

### Step 4: Test with curl (above)
- Does the curl command work? ✅/❌
- What error message does it return?

## Common Error Messages and Solutions

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| "invalid_grant: authentication failure" | Wrong username/password/token | Verify credentials, reset security token |
| "invalid_client_id" | Wrong Client ID | Check Connected App Consumer Key |
| "invalid_client: invalid client credentials" | Wrong Client Secret | Check Connected App Consumer Secret |
| "invalid_grant: user hasn't approved this consumer" | User doesn't have access | Check user permissions, IP restrictions |
| "400 Bad Request" (generic) | Multiple possible causes | Check all of the above |

