# Quick Config Setup - Copy & Paste Commands

Based on your current setup, here are the exact commands to run. **Replace the placeholder values** with your actual values.

## Your Current App Name
```bash
APP_NAME="democomponent-qrcode-generator"
```

## Step 1: Set Required OAuth2 Config Vars

### 1. Instance URL (Already correct)
```bash
heroku config:set SALESFORCE_INSTANCE_URL="https://trailsignup-a59cbb1bc47f48.my.salesforce.com" --app democomponent-qrcode-generator
```

### 2. Client ID (Consumer Key)
**Get from:** Setup → App Manager → Your Connected App → Consumer Key
```bash
heroku config:set SALESFORCE_CLIENT_ID="PASTE_YOUR_CONSUMER_KEY_HERE" --app democomponent-qrcode-generator
```

### 3. Client Secret (Consumer Secret)
**Get from:** Setup → App Manager → Your Connected App → Manage → View → Consumer Secret
```bash
heroku config:set SALESFORCE_CLIENT_SECRET="PASTE_YOUR_CONSUMER_SECRET_HERE" --app democomponent-qrcode-generator
```

### 4. Username (Already correct)
```bash
heroku config:set SALESFORCE_USERNAME="trailsignup.a59cbb1bc47f48@salesforce.com" --app democomponent-qrcode-generator
```

### 5. Password (ONLY password, no token!)
**⚠️ CRITICAL:** Enter ONLY your password. The code automatically adds the security token.
```bash
heroku config:set SALESFORCE_PASSWORD="YOUR_PASSWORD_ONLY" --app democomponent-qrcode-generator
```

### 6. Security Token
**Get from:** Setup → My Personal Information → Reset My Security Token → Check email
```bash
heroku config:set SALESFORCE_SECURITY_TOKEN="PASTE_YOUR_24_CHAR_TOKEN_HERE" --app democomponent-qrcode-generator
```

## Step 2: Remove Expired Session ID

```bash
heroku config:unset SALESFORCE_SESSION_ID --app democomponent-qrcode-generator
```

## Step 3: Restart App

```bash
heroku restart --app democomponent-qrcode-generator
```

## Step 4: Verify

```bash
# View all Salesforce config vars
heroku config --app democomponent-qrcode-generator | grep SALESFORCE

# Check logs for authentication
heroku logs --tail --app democomponent-qrcode-generator
```

## All-in-One Script (Replace Values First!)

```bash
APP_NAME="democomponent-qrcode-generator"

# Set all config vars
heroku config:set SALESFORCE_INSTANCE_URL="https://trailsignup-a59cbb1bc47f48.my.salesforce.com" --app $APP_NAME
heroku config:set SALESFORCE_CLIENT_ID="YOUR_CONSUMER_KEY" --app $APP_NAME
heroku config:set SALESFORCE_CLIENT_SECRET="YOUR_CONSUMER_SECRET" --app $APP_NAME
heroku config:set SALESFORCE_USERNAME="trailsignup.a59cbb1bc47f48@salesforce.com" --app $APP_NAME
heroku config:set SALESFORCE_PASSWORD="YOUR_PASSWORD_ONLY" --app $APP_NAME
heroku config:set SALESFORCE_SECURITY_TOKEN="YOUR_24_CHAR_TOKEN" --app $APP_NAME

# Remove Session ID
heroku config:unset SALESFORCE_SESSION_ID --app $APP_NAME

# Restart
heroku restart --app $APP_NAME

# Verify
heroku config --app $APP_NAME | grep SALESFORCE
```

## What Each Value Should Look Like

| Config Var | Example Format | Length |
|------------|----------------|--------|
| `SALESFORCE_INSTANCE_URL` | `https://trailsignup-a59cbb1bc47f48.my.salesforce.com` | ~50 chars |
| `SALESFORCE_CLIENT_ID` | `3MVG9XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` | ~100+ chars |
| `SALESFORCE_CLIENT_SECRET` | `1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF` | 64 hex chars |
| `SALESFORCE_USERNAME` | `trailsignup.a59cbb1bc47f48@salesforce.com` | ~40 chars |
| `SALESFORCE_PASSWORD` | `YourPassword123!` | Varies |
| `SALESFORCE_SECURITY_TOKEN` | `AbCdEfGhIjKlMnOpQrStUvWx` | 24 chars |

## Troubleshooting

If you still get `invalid_grant` after setting all vars:

1. **Double-check password** - Make sure it's ONLY the password (no token appended)
2. **Reset security token again** - Setup → My Personal Information → Reset My Security Token
3. **Test with curl:**
   ```bash
   curl -X POST "https://trailsignup-a59cbb1bc47f48.my.salesforce.com/services/oauth2/token" \
     -d "grant_type=password" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "username=trailsignup.a59cbb1bc47f48@salesforce.com" \
     -d "password=YOUR_PASSWORD+YOUR_SECURITY_TOKEN"
   ```
   (Note: In curl, you manually concatenate password+token. In Heroku config, set them separately.)

4. **Check Connected App:**
   - OAuth Settings enabled ✅
   - Password flow allowed ✅
   - IP Relaxation: "Relax IP restrictions" ✅

5. **Check user:**
   - User is Active ✅
   - User has "API Enabled" ✅

