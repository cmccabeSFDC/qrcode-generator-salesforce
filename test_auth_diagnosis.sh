#!/bin/bash

echo "=========================================="
echo "AUTHENTICATION DIAGNOSIS SCRIPT"
echo "=========================================="
echo ""

APP_NAME="democomponent-qrcode-generator-c48b26ff05fc"

echo "Step 1: Checking if backend code is deployed..."
echo "Looking for 'APPLINK AUTHENTICATION CHECK' in recent logs..."
echo ""
heroku logs --num 50 --app $APP_NAME | grep -i "APPLINK AUTHENTICATION CHECK" | head -5
if [ $? -eq 0 ]; then
    echo "✅ Backend code appears to be deployed (found log section)"
else
    echo "❌ Backend code may not be deployed (log section not found)"
    echo "   → Need to deploy: cd backend && git push heroku main"
fi
echo ""

echo "Step 2: Checking Heroku config vars..."
echo ""
echo "Salesforce Config Vars Status:"
echo "-------------------------------"
for var in SALESFORCE_INSTANCE_URL SALESFORCE_CLIENT_ID SALESFORCE_CLIENT_SECRET SALESFORCE_USERNAME SALESFORCE_PASSWORD SALESFORCE_SECURITY_TOKEN; do
    value=$(heroku config:get $var --app $APP_NAME 2>/dev/null)
    if [ -z "$value" ]; then
        echo "❌ $var: NOT SET"
    else
        if [[ "$var" == *"PASSWORD"* ]] || [[ "$var" == *"SECRET"* ]] || [[ "$var" == *"TOKEN"* ]]; then
            len=${#value}
            echo "✅ $var: SET (length: $len)"
        else
            echo "✅ $var: SET (value: $value)"
        fi
    fi
done
echo ""

echo "Step 3: Testing OAuth2 authentication..."
echo ""
echo "Getting config values..."
CLIENT_ID=$(heroku config:get SALESFORCE_CLIENT_ID --app $APP_NAME 2>/dev/null)
CLIENT_SECRET=$(heroku config:get SALESFORCE_CLIENT_SECRET --app $APP_NAME 2>/dev/null)
USERNAME=$(heroku config:get SALESFORCE_USERNAME --app $APP_NAME 2>/dev/null)
PASSWORD=$(heroku config:get SALESFORCE_PASSWORD --app $APP_NAME 2>/dev/null)
TOKEN=$(heroku config:get SALESFORCE_SECURITY_TOKEN --app $APP_NAME 2>/dev/null)
INSTANCE_URL=$(heroku config:get SALESFORCE_INSTANCE_URL --app $APP_NAME 2>/dev/null)

if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ] || [ -z "$USERNAME" ] || [ -z "$PASSWORD" ] || [ -z "$TOKEN" ]; then
    echo "❌ Missing required config vars. Cannot test OAuth2."
else
    echo "Testing OAuth2 with Salesforce..."
    COMBINED_PASSWORD="${PASSWORD}${TOKEN}"
    
    RESPONSE=$(curl -s -X POST "${INSTANCE_URL}/services/oauth2/token" \
        -d "grant_type=password" \
        -d "client_id=${CLIENT_ID}" \
        -d "client_secret=${CLIENT_SECRET}" \
        -d "username=${USERNAME}" \
        -d "password=${COMBINED_PASSWORD}")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "✅ OAuth2 authentication SUCCESS"
        echo "   Response: $(echo $RESPONSE | jq -r '.access_token' | cut -c1-20)..."
    else
        echo "❌ OAuth2 authentication FAILED"
        echo "   Error: $(echo $RESPONSE | jq -r '.error_description // .error // "Unknown error"')"
        echo "   Full response: $RESPONSE"
    fi
fi
echo ""

echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Check if QR code URL includes session_token parameter (browser console)"
echo "2. Check if form sends Authorization header (browser Network tab)"
echo "3. Check Heroku logs for 'APPLINK AUTHENTICATION CHECK' section"
echo ""
echo "See DIAGNOSE_AUTH.md for detailed step-by-step instructions."


