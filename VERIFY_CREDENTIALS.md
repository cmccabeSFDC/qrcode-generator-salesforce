# Verify Salesforce OAuth2 Credentials

## Current Status
- ✅ Token in Heroku: `8rdaQQA2TJvEOfAxLc6nohsdv` (25 chars)
- ✅ Username: `trailsignup.a59cbb1bc47f48@salesforce.com`
- ✅ Password length: 12 chars
- ❌ OAuth2 authentication failing: `invalid_grant: authentication failure`

## What to Check

### 1. Verify Security Token is Correct
The token you provided: `8rdaQQA2TJvEOfAxLc6nohsdv`

**To verify:**
1. Log into Salesforce as: `trailsignup.a59cbb1bc47f48@salesforce.com`
2. Go to: **Setup → My Personal Information → Reset My Security Token**
3. Check your email for the token
4. Compare it to: `8rdaQQA2TJvEOfAxLc6nohsdv`
5. **Make sure there are no spaces or extra characters**

### 2. Verify Password is Correct
- Password: `Salesforce1!` (12 characters)
- **Important:** If you changed your password recently, the security token was automatically reset
- You need to get a NEW security token after changing your password

### 3. Verify Connected App Settings

Go to: **Setup → App Manager → Your Connected App**

**Check these settings:**

#### OAuth Settings
- ✅ **Enable OAuth Settings**: Must be CHECKED
- ✅ **Callback URL**: Can be `https://localhost` or `http://localhost` (doesn't matter for password flow)
- ✅ **Selected OAuth Scopes**: Must include at least:
  - `Access and manage your data (api)` OR
  - `Full access (full)`
- ✅ **IP Relaxation**: Should be set to **"Relax IP restrictions"**

#### Consumer Key & Secret
- **Consumer Key** should match the value stored in Heroku as `SALESFORCE_CLIENT_ID`
- **Consumer Secret** should match the value stored in Heroku as `SALESFORCE_CLIENT_SECRET`

### 4. Verify User Permissions

Go to: **Setup → Users → Users → Find your user**

**Check:**
- ✅ User is **Active**
- ✅ User has **API Enabled** permission
- ✅ User profile/permission set allows API access

### 5. Test Credentials Manually

You can test the exact credentials with this command (replace with your actual values):

```bash
curl -X POST "https://YOUR_INSTANCE.my.salesforce.com/services/oauth2/token" \
  -d "grant_type=password" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "username=YOUR_USERNAME" \
  -d "password=YOUR_PASSWORD+YOUR_SECURITY_TOKEN"
```

**Important:** Replace `YOUR_PASSWORD+YOUR_SECURITY_TOKEN` with:
- Your actual password (no quotes)
- Plus sign (+)
- Your actual security token (no space, no quotes)

Example format (replace with your actual values):
```
-d "password=MyPassword123!MySecurityToken"
```

## Common Issues

### Issue: "invalid_grant: authentication failure"

**Most common causes:**
1. **Wrong password** - Double-check the password is exactly `Salesforce1!`
2. **Wrong security token** - Token might be for a different user or expired
3. **Password changed** - If you changed password, you MUST reset the security token
4. **Token has spaces** - Copy/paste might have added spaces
5. **Connected App not configured** - OAuth scopes missing or IP restrictions too strict

### Issue: Token Length
- Security tokens are typically **24-25 characters**
- Your token: `8rdaQQA2TJvEOfAxLc6nohsdv` = 25 characters ✅

## Next Steps

1. **Verify the security token** - Get a fresh one from Salesforce email
2. **Check Connected App OAuth settings** - Make sure scopes are set correctly
3. **Verify user has API Enabled** - Check user permissions
4. **Test with curl** - Use the curl command above to test credentials directly

If the curl command works, the issue is in the code.
If the curl command fails, the issue is with the credentials or Connected App settings.

