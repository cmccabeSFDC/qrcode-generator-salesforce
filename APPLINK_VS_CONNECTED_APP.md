# AppLink vs Connected App - Complete Guide

## Quick Answer

**For your current setup:** You only need a **Connected App**. AppLink is NOT required.

- ✅ **Connected App** - Required for OAuth2 authentication (what you're using now)
- ❌ **AppLink** - NOT needed for your use case (only for Heroku apps that need deep Salesforce integration)

---

## What is a Connected App?

**Connected App** = OAuth2 application configuration in Salesforce

**Purpose:**
- Allows external applications to authenticate with Salesforce using OAuth2
- Defines authentication flows, permissions, and access scopes
- Required for API access from external systems (like your Heroku app)

**What it provides:**
- Consumer Key (Client ID)
- Consumer Secret (Client Secret)
- OAuth2 endpoints
- Permission scopes
- IP restrictions

**Your current setup:**
- ✅ You're using a Connected App for OAuth2 password flow
- ✅ Your Heroku app authenticates using Consumer Key/Secret
- ✅ This is the standard way to integrate external apps with Salesforce

---

## What is AppLink?

**AppLink** = Framework for deep Heroku-Salesforce integration

**Purpose:**
- Connects Heroku applications directly into Salesforce UI
- Allows Salesforce tools (Apex, Flow, Agentforce) to call Heroku apps
- Handles authentication, context, and data operations automatically
- Publishes Heroku apps into Salesforce orgs

**What it provides:**
- Automatic authentication (no OAuth2 needed)
- Salesforce context (user, org, record) passed automatically
- Deep integration with Salesforce UI
- Can be called from Apex, Flow, etc.

**When to use:**
- Heroku apps that need to appear in Salesforce UI
- Heroku apps called from Apex/Flow
- Heroku apps that need Salesforce user context automatically
- Complex integrations requiring Salesforce-native experience

---

## Comparison Table

| Feature | Connected App | AppLink |
|---------|--------------|---------|
| **Purpose** | OAuth2 authentication for external apps | Deep Heroku-Salesforce integration |
| **Authentication** | Manual OAuth2 flow (password, web server, etc.) | Automatic (handled by framework) |
| **Setup Complexity** | Medium (configure OAuth settings) | High (requires Heroku add-on, configuration) |
| **Use Cases** | Any external app needing Salesforce API access | Heroku apps integrated into Salesforce UI |
| **API Access** | ✅ Yes (via OAuth2 tokens) | ✅ Yes (automatic) |
| **Salesforce Context** | ❌ Must pass manually | ✅ Automatic (user, org, record) |
| **Can be called from Apex** | ❌ No (must use HTTP callouts) | ✅ Yes (native integration) |
| **Can be called from Flow** | ❌ No | ✅ Yes |
| **IP Restrictions** | ✅ Configurable | ✅ Handled automatically |
| **Your Current Setup** | ✅ **Using this** | ❌ Not using |

---

## Your Current Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  Salesforce     │────────▶│  Heroku App     │────────▶│  Salesforce     │
│  LWC Component  │  HTTP   │  (FastAPI)      │  OAuth2 │  REST API       │
│                 │  POST   │                  │  Token  │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
     │                              │                            │
     │                              │                            │
     │                              │                            │
     │                              ▼                            │
     │                    ┌──────────────────┐                 │
     │                    │  Connected App    │                 │
     │                    │  (OAuth2 Config) │                 │
     │                    └──────────────────┘                 │
     │                                                           │
     └───────────────────────────────────────────────────────────┘
                    (File upload form opens in browser)
```

**What you're using:**
1. **Salesforce LWC** - Generates QR code, calls Apex
2. **Apex Class** (`QRCodeService`) - Makes HTTP callout to Heroku
3. **Heroku App** - Generates QR code, handles file uploads
4. **Connected App** - Provides OAuth2 credentials for Heroku → Salesforce API calls
5. **Salesforce REST API** - Heroku uploads files using OAuth2 token

**AppLink is NOT in this flow** - You're using standard HTTP callouts with OAuth2.

---

## When Would You Need AppLink?

You would need AppLink if you wanted to:

### Scenario 1: Call Heroku from Apex/Flow (without HTTP callouts)
```apex
// Instead of this (current approach):
HttpRequest req = new HttpRequest();
req.setEndpoint('https://your-app.herokuapp.com/generate');
HttpResponse res = http.send(req);

// You could do this (with AppLink):
HerokuApp.generateQRCode(data); // Native Apex call
```

### Scenario 2: Heroku App in Salesforce UI
- Heroku app appears as a Salesforce component
- Users interact with Heroku app within Salesforce
- No external URLs needed

### Scenario 3: Automatic Context Passing
- Salesforce user context passed automatically
- No need to pass user/org/record IDs manually
- Heroku app knows who's calling it

**Your use case:** You're making HTTP callouts from Apex, which is perfectly fine and doesn't require AppLink.

---

## Do You Need Both?

**Short answer: NO**

### Option A: Current Setup (Recommended for You)
- ✅ **Connected App** - For OAuth2 authentication
- ❌ **AppLink** - NOT needed

**Why:** Your Heroku app is a standalone service that:
- Receives HTTP requests from Salesforce
- Authenticates with Salesforce using OAuth2
- Makes API calls to Salesforce
- Doesn't need to be called from Apex/Flow natively
- Doesn't need Salesforce UI integration

### Option B: AppLink Setup (Not Recommended for You)
- ✅ **AppLink** - For deep integration
- ❌ **Connected App** - NOT needed (AppLink handles auth)

**Why you don't need this:** AppLink is overkill for your use case. It's designed for:
- Heroku apps that are deeply integrated into Salesforce
- Apps that need to be called from Apex/Flow without HTTP callouts
- Apps that need automatic Salesforce context

---

## Connected App Configuration (What You Need)

Your Connected App should have:

1. **Basic Information:**
   - Connected App Name
   - API Name
   - Contact Email

2. **OAuth Settings:**
   - ✅ Enable OAuth Settings
   - Callback URL: `https://localhost` (doesn't matter for password flow)
   - Selected OAuth Scopes:
     - `Access and manage your data (api)` ✅
     - `Perform requests on your behalf at any time (refresh_token, offline_access)` ✅

3. **API (Enable OAuth Settings):**
   - Consumer Key (Client ID) ✅
   - Consumer Secret (Client Secret) ✅

4. **OAuth Policies:**
   - IP Relaxation: **Relax IP restrictions** ✅
   - Permitted Users: **All users may self-authorize** or **Admin approved users are pre-authorized**

5. **Manage Policies:**
   - Refresh Token Policy: Set as needed
   - Session Timeout: Set as needed

**This is all you need!** No AppLink configuration required.

---

## AppLink Configuration (What You DON'T Need)

If you were using AppLink, you would need:

1. **Heroku Add-on:**
   - Install Salesforce AppLink add-on on Heroku
   - Configure Salesforce org connection

2. **Salesforce Setup:**
   - Register Heroku app in Salesforce
   - Configure authentication
   - Set up context passing

3. **Code Changes:**
   - Modify Heroku app to use AppLink SDK
   - Update Apex to use native Heroku calls instead of HTTP

**You don't need any of this** for your current architecture.

---

## Summary

### ✅ What You Have (Correct Setup)
- **Connected App** - Provides OAuth2 credentials
- **Heroku App** - Standalone service using OAuth2
- **Apex HTTP Callouts** - Standard integration pattern
- **Salesforce REST API** - File uploads using OAuth2 tokens

### ❌ What You DON'T Need
- **AppLink** - Overkill for your use case
- **Heroku AppLink Add-on** - Not required
- **Native Apex Heroku calls** - HTTP callouts work fine

### 🎯 Bottom Line
**You only need a Connected App.** AppLink is a different integration pattern for different use cases. Your current setup is correct and follows Salesforce best practices for external API integrations.

---

## FAQ

**Q: Can I use both AppLink and Connected App?**  
A: Yes, but usually unnecessary. AppLink handles authentication, so you typically don't need a Connected App if using AppLink.

**Q: Should I switch to AppLink?**  
A: No. Your current setup is simpler and works well. AppLink adds complexity without benefits for your use case.

**Q: Will AppLink fix my authentication issues?**  
A: No. Your authentication issues are with OAuth2 credentials (password/token). AppLink wouldn't help - it's a different integration pattern.

**Q: Can I call Heroku from Flow without AppLink?**  
A: No. Flow can't make HTTP callouts. You'd need AppLink for Flow integration, but you're using Apex which can make HTTP callouts.

**Q: Is AppLink more secure?**  
A: Not necessarily. Both use secure authentication. AppLink handles it automatically, Connected App requires manual OAuth2 setup.

---

## References

- [Salesforce Connected Apps Documentation](https://help.salesforce.com/s/articleView?id=sf.connected_app_overview.htm)
- [Heroku AppLink Documentation](https://devcenter.heroku.com/articles/salesforce-applink)
- [OAuth2 Password Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_username_password_flow.htm)

