# How to Get Your Salesforce Security Token

## Method 1: Reset Security Token (Easiest)

1. **Log into Salesforce** (as the user: `trailsignup.a59cbb1bc47f48@salesforce.com`)
2. Click your **profile picture/avatar** in the top right
3. Click **Settings** (or "My Settings")
4. In the left sidebar, under **Personal**, click **Reset My Security Token**
5. Click **Reset Security Token** button
6. **Check your email** - Salesforce will send you the new security token
7. The token is a **24-character alphanumeric string** (like: `AbCdEfGhIjKlMnOpQrStUvWx`)

## Method 2: If Email Not Received

1. Go to **Setup** (gear icon → Setup)
2. Search for: **"Reset My Security Token"** in Quick Find
3. Click **Reset My Security Token**
4. Check your email inbox

## Method 3: If You Can't Access Email

1. Go to **Setup** → **Users** → **Users**
2. Find your user
3. Click on the user
4. Scroll to **Security Token** section
5. If visible, you can see it there (or reset it)

## Important Notes

- **Security tokens are case-sensitive**
- **They expire if you change your password** (you'll need to reset again)
- **They can be reset multiple times** - each reset generates a new token
- **Keep it secure** - it's like a password

## Setting in Heroku

Once you have your security token, set it in Heroku:

```bash
heroku config:set SALESFORCE_SECURITY_TOKEN="YOUR_TOKEN_HERE" --app democomponent-qrcode-generator
```

Replace `YOUR_TOKEN_HERE` with the actual token from the email.

## Why Security Token?

For OAuth2 password flow, Salesforce requires:
- Username
- Password + Security Token (concatenated)
- Client ID (Consumer Key)
- Client Secret (Consumer Secret)

The security token is appended directly to your password with no space:
```
password + security_token
```

Example: If password is `Salesforce1!` and token is `AbCd1234`, the combined password would be:
```
Salesforce1!AbCd1234
```

## Alternative: Use Session ID (Current Setup)

You already have a Session ID set. However:
- ⚠️ Session IDs **expire** after periods of inactivity
- ⚠️ Session IDs expire when you log out
- ✅ Session IDs are simpler (no security token needed)
- ✅ Session IDs work immediately if valid

**Recommendation**: For production, use OAuth2 with security token. For testing, Session ID is fine if it's still valid.

