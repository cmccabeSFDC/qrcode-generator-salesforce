# Heroku Config Vars - Complete Guide

This document lists all Heroku config vars required for the QR Code Generator application.

## Required Config Vars for OAuth2 Authentication

### 1. `SALESFORCE_INSTANCE_URL`
**Required:** ✅ Yes  
**Description:** Your Salesforce instance URL  
**Format:** `https://your-instance.my.salesforce.com` or `https://login.salesforce.com`  
**How to get:**
- Log into Salesforce
- Look at the URL in your browser
- Use the domain part (e.g., `https://trailsignup-a59cbb1bc47f48.my.salesforce.com`)
- **OR** use `https://login.salesforce.com` for production orgs

**Example:**
```bash
heroku config:set SALESFORCE_INSTANCE_URL="https://trailsignup-a59cbb1bc47f48.my.salesforce.com" --app democomponent-qrcode-generator
```

---

### 2. `SALESFORCE_CLIENT_ID`
**Required:** ✅ Yes (for OAuth2)  
**Description:** Consumer Key from your Connected App  
**Format:** Long alphanumeric string (starts with `3MVG...`)  
**How to get:**
1. Go to Salesforce Setup → App Manager
2. Find your Connected App (or create one)
3. Click on the app name
4. Under "API (Enable OAuth Settings)" section, find **Consumer Key**
5. Copy the entire Consumer Key value

**Example:**
```bash
heroku config:set SALESFORCE_CLIENT_ID="3MVG9XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" --app democomponent-qrcode-generator
```

---

### 3. `SALESFORCE_CLIENT_SECRET`
**Required:** ✅ Yes (for OAuth2)  
**Description:** Consumer Secret from your Connected App  
**Format:** 64-character hexadecimal string  
**How to get:**
1. Go to Salesforce Setup → App Manager
2. Find your Connected App
3. Click **Manage** → **View**
4. Under "Consumer Details", find **Consumer Secret**
5. Click "Click to reveal" if hidden
6. Copy the entire Consumer Secret (64 hex characters)

**Example:**
```bash
heroku config:set SALESFORCE_CLIENT_SECRET="1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF" --app democomponent-qrcode-generator
```

---

### 4. `SALESFORCE_USERNAME`
**Required:** ✅ Yes (for OAuth2)  
**Description:** Salesforce username (email address)  
**Format:** Email address  
**How to get:**
- Your Salesforce login email
- Format: `username@domain.com` or `username@yourorg.salesforce.com`

**Example:**
```bash
heroku config:set SALESFORCE_USERNAME="trailsignup.a59cbb1bc47f48@salesforce.com" --app democomponent-qrcode-generator
```

---

### 5. `SALESFORCE_PASSWORD`
**Required:** ✅ Yes (for OAuth2)  
**Description:** Salesforce password (plain password only, NOT password+token)  
**Format:** Your actual Salesforce password  
**Important:** 
- ⚠️ **ONLY include the password** - the code automatically appends the security token
- ⚠️ **Do NOT include the security token** in this value
- ⚠️ If your password has special characters, wrap in quotes

**How to get:**
- Your Salesforce login password
- The password you use to log into Salesforce UI

**Example:**
```bash
heroku config:set SALESFORCE_PASSWORD="YourActualPassword123!" --app democomponent-qrcode-generator
```

---

### 6. `SALESFORCE_SECURITY_TOKEN`
**Required:** ✅ Yes (for OAuth2)  
**Description:** Security token for OAuth2 password flow  
**Format:** 24-character alphanumeric string  
**How to get:**
1. Log into Salesforce
2. Click your profile picture → **Settings** (or "My Settings")
3. Under **Personal**, click **Reset My Security Token**
4. Click **Reset Security Token** button
5. **Check your email** - Salesforce sends the token
6. Copy the 24-character token from the email

**Important:**
- ⚠️ Token expires if you change your password (reset it again)
- ⚠️ Token is case-sensitive
- ⚠️ The code automatically concatenates password + token for OAuth2

**Example:**
```bash
heroku config:set SALESFORCE_SECURITY_TOKEN="AbCdEfGhIjKlMnOpQrStUvWx" --app democomponent-qrcode-generator
```

---

## Optional Config Vars

### 7. `SALESFORCE_SESSION_ID`
**Required:** ❌ No (optional, alternative to OAuth2)  
**Description:** Active Salesforce session ID (alternative authentication method)  
**Format:** Long alphanumeric string (starts with `00D...` or `Bearer 00D...`)  
**How to get:**
1. Log into Salesforce in your browser
2. Open browser Developer Tools (F12)
3. Go to **Application** tab → **Cookies** → Select your Salesforce domain
4. Find cookie named `sid` or `SessionId`
5. Copy the value
6. **OR** use Workbench (workbench.developerforce.com) → Login → Copy session ID from REST Explorer

**Important:**
- ⚠️ Session IDs expire after inactivity or logout
- ⚠️ If set, the app will try Session ID first, then fall back to OAuth2
- ⚠️ **Recommendation:** Leave this unset and use OAuth2 for production

**Example:**
```bash
heroku config:set SALESFORCE_SESSION_ID="00DJ9000001lQog!AQcAQ..." --app democomponent-qrcode-generator
```

**To remove (recommended for OAuth2):**
```bash
heroku config:unset SALESFORCE_SESSION_ID --app democomponent-qrcode-generator
```

---

### 8. `SALESFORCE_ACCESS_TOKEN`
**Required:** ❌ No (automatically set by code)  
**Description:** OAuth2 access token (automatically obtained during authentication)  
**Format:** Long alphanumeric string  
**Note:** This is automatically set by the code after successful OAuth2 authentication. You don't need to set this manually.

---

## General Config Vars (Optional)

### 9. `ENVIRONMENT`
**Required:** ❌ No (has default)  
**Description:** Application environment  
**Default:** `development`  
**Example:**
```bash
heroku config:set ENVIRONMENT="production" --app democomponent-qrcode-generator
```

---

### 10. `SECRET_KEY`
**Required:** ❌ No (has default)  
**Description:** Application secret key  
**Default:** `qr-code-generator-secret-key`  
**Example:**
```bash
heroku config:set SECRET_KEY="your-secret-key-here" --app democomponent-qrcode-generator
```

---

## Complete Setup Commands

### Option A: OAuth2 Authentication (Recommended)

```bash
# Set all required OAuth2 vars
heroku config:set SALESFORCE_INSTANCE_URL="https://trailsignup-a59cbb1bc47f48.my.salesforce.com" --app democomponent-qrcode-generator

heroku config:set SALESFORCE_CLIENT_ID="YOUR_CONSUMER_KEY_HERE" --app democomponent-qrcode-generator

heroku config:set SALESFORCE_CLIENT_SECRET="YOUR_CONSUMER_SECRET_HERE" --app democomponent-qrcode-generator

heroku config:set SALESFORCE_USERNAME="trailsignup.a59cbb1bc47f48@salesforce.com" --app democomponent-qrcode-generator

heroku config:set SALESFORCE_PASSWORD="YOUR_PASSWORD_ONLY" --app democomponent-qrcode-generator

heroku config:set SALESFORCE_SECURITY_TOKEN="YOUR_24_CHAR_TOKEN" --app democomponent-qrcode-generator

# Remove Session ID if set (to force OAuth2)
heroku config:unset SALESFORCE_SESSION_ID --app democomponent-qrcode-generator

# Restart the app to apply changes
heroku restart --app democomponent-qrcode-generator
```

### Option B: Session ID Authentication (Not Recommended for Production)

```bash
# Set Session ID
heroku config:set SALESFORCE_SESSION_ID="YOUR_SESSION_ID_HERE" --app democomponent-qrcode-generator

# Set Instance URL (still needed)
heroku config:set SALESFORCE_INSTANCE_URL="https://trailsignup-a59cbb1bc47f48.my.salesforce.com" --app democomponent-qrcode-generator

# Restart the app
heroku restart --app democomponent-qrcode-generator
```

---

## Verify Your Config Vars

### View all config vars:
```bash
heroku config --app democomponent-qrcode-generator
```

### View only Salesforce vars:
```bash
heroku config --app democomponent-qrcode-generator | grep SALESFORCE
```

### Check if a specific var is set:
```bash
heroku config:get SALESFORCE_USERNAME --app democomponent-qrcode-generator
```

### View masked values (using the check script):
```bash
./check_heroku_config.sh
```

---

## Current Values (From Your Logs)

Based on your recent logs, here's what you currently have set:

| Config Var | Status | Value (Masked) |
|------------|--------|----------------|
| `SALESFORCE_INSTANCE_URL` | ✅ SET | `https://trailsignup-a59cbb1bc47f48.my.salesforce.com` |
| `SALESFORCE_SESSION_ID` | ✅ SET | `00DJ9000001lQog!AQcA...` (112 chars) - **EXPIRED** |
| `SALESFORCE_CLIENT_ID` | ✅ SET | `3MVG9XXXXXXXXXXXXXXXXX...` |
| `SALESFORCE_CLIENT_SECRET` | ✅ SET | (64 chars) |
| `SALESFORCE_USERNAME` | ✅ SET | `trailsignup.a59cbb1bc47f48@salesforce.com` |
| `SALESFORCE_PASSWORD` | ✅ SET | (12 chars) |
| `SALESFORCE_SECURITY_TOKEN` | ✅ SET | (24 chars) |

---

## Troubleshooting

### If OAuth2 still fails with `invalid_grant`:

1. **Verify password is correct:**
   ```bash
   # Check password length (should match your actual password length)
   heroku config:get SALESFORCE_PASSWORD --app democomponent-qrcode-generator | wc -c
   ```

2. **Verify security token is correct:**
   - Reset it again: Setup → My Personal Information → Reset My Security Token
   - Update Heroku: `heroku config:set SALESFORCE_SECURITY_TOKEN="NEW_TOKEN" --app democomponent-qrcode-generator`

3. **Test with curl locally:**
   ```bash
   curl -X POST "https://trailsignup-a59cbb1bc47f48.my.salesforce.com/services/oauth2/token" \
     -d "grant_type=password" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "username=trailsignup.a59cbb1bc47f48@salesforce.com" \
     -d "password=YOUR_PASSWORD+YOUR_SECURITY_TOKEN"
   ```

4. **Check Connected App settings:**
   - OAuth Settings enabled ✅
   - Password flow allowed ✅
   - IP Relaxation: "Relax IP restrictions" ✅
   - OAuth Scopes include `api` ✅

5. **Check user permissions:**
   - User is Active ✅
   - User has "API Enabled" permission ✅
   - User can create ContentVersion and ContentDocumentLink ✅

---

## Quick Reference Checklist

- [ ] `SALESFORCE_INSTANCE_URL` - Your Salesforce instance URL
- [ ] `SALESFORCE_CLIENT_ID` - Consumer Key from Connected App
- [ ] `SALESFORCE_CLIENT_SECRET` - Consumer Secret from Connected App
- [ ] `SALESFORCE_USERNAME` - Your Salesforce username/email
- [ ] `SALESFORCE_PASSWORD` - Your password (ONLY password, no token)
- [ ] `SALESFORCE_SECURITY_TOKEN` - 24-char token from email
- [ ] `SALESFORCE_SESSION_ID` - (Optional) Remove if using OAuth2
- [ ] Restart Heroku app after setting vars
- [ ] Test authentication in logs

---

## Security Notes

⚠️ **Never commit config vars to git**  
⚠️ **Never share config vars in public channels**  
⚠️ **Rotate secrets if exposed**  
⚠️ **Use Heroku's config vars, not hardcoded values**

