#!/bin/bash

# Heroku Config Vars Setup Script
# App: democomponent-qrcode-generator
# 
# IMPORTANT: Replace all placeholder values with your actual values before running!

APP_NAME="democomponent-qrcode-generator"

echo "=========================================="
echo "Heroku Config Vars Setup"
echo "App: $APP_NAME"
echo "=========================================="
echo ""

# Check if heroku CLI is available
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first."
    exit 1
fi

# Check authentication
echo "Checking Heroku authentication..."
if ! heroku auth:whoami &> /dev/null; then
    echo "⚠️  Not authenticated with Heroku. Run: heroku login"
    exit 1
fi

echo "✅ Authenticated"
echo ""

# ==========================================
# REQUIRED CONFIG VARS FOR OAUTH2
# ==========================================

echo "Setting required OAuth2 config vars..."
echo ""

# 1. Instance URL
echo "1. Setting SALESFORCE_INSTANCE_URL..."
heroku config:set SALESFORCE_INSTANCE_URL="https://trailsignup-a59cbb1bc47f48.my.salesforce.com" --app $APP_NAME

# 2. Client ID (Consumer Key)
echo "2. Setting SALESFORCE_CLIENT_ID..."
echo "   ⚠️  REPLACE WITH YOUR ACTUAL CONSUMER KEY"
read -p "   Enter Consumer Key (Client ID): " CLIENT_ID
heroku config:set SALESFORCE_CLIENT_ID="$CLIENT_ID" --app $APP_NAME

# 3. Client Secret (Consumer Secret)
echo "3. Setting SALESFORCE_CLIENT_SECRET..."
echo "   ⚠️  REPLACE WITH YOUR ACTUAL CONSUMER SECRET"
read -p "   Enter Consumer Secret (Client Secret): " CLIENT_SECRET
heroku config:set SALESFORCE_CLIENT_SECRET="$CLIENT_SECRET" --app $APP_NAME

# 4. Username
echo "4. Setting SALESFORCE_USERNAME..."
heroku config:set SALESFORCE_USERNAME="trailsignup.a59cbb1bc47f48@salesforce.com" --app $APP_NAME

# 5. Password (ONLY password, no token)
echo "5. Setting SALESFORCE_PASSWORD..."
echo "   ⚠️  IMPORTANT: Enter ONLY your password (no security token)"
read -s -p "   Enter Password: " PASSWORD
echo ""
heroku config:set SALESFORCE_PASSWORD="$PASSWORD" --app $APP_NAME

# 6. Security Token
echo "6. Setting SALESFORCE_SECURITY_TOKEN..."
echo "   ⚠️  Get this from: Setup → My Personal Information → Reset My Security Token"
read -p "   Enter Security Token (24 chars): " SECURITY_TOKEN
heroku config:set SALESFORCE_SECURITY_TOKEN="$SECURITY_TOKEN" --app $APP_NAME

# ==========================================
# REMOVE SESSION ID (to force OAuth2)
# ==========================================

echo ""
echo "Removing SALESFORCE_SESSION_ID (to use OAuth2 instead)..."
heroku config:unset SALESFORCE_SESSION_ID --app $APP_NAME 2>/dev/null || echo "   (Session ID was not set)"

# ==========================================
# VERIFY
# ==========================================

echo ""
echo "=========================================="
echo "Verifying config vars..."
echo "=========================================="
echo ""

heroku config --app $APP_NAME | grep SALESFORCE

echo ""
echo "=========================================="
echo "Restarting app to apply changes..."
echo "=========================================="
heroku restart --app $APP_NAME

echo ""
echo "✅ Done! Check logs with: heroku logs --tail --app $APP_NAME"
echo ""




