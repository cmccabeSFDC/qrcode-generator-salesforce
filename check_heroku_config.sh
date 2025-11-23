#!/bin/bash

echo "=== HEROKU CONFIG VARS CHECK ==="
echo ""
echo "Checking config vars for app: democomponent-qrcode-generator"
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

# Get all Salesforce-related config vars
echo "=== SALESFORCE CONFIG VARS ==="
heroku config --app democomponent-qrcode-generator | grep SALESFORCE

echo ""
echo "=== CHECKING FOR REQUIRED VARS ==="

# Check each required var
vars=(
    "SALESFORCE_INSTANCE_URL"
    "SALESFORCE_CLIENT_ID"
    "SALESFORCE_CLIENT_SECRET"
    "SALESFORCE_USERNAME"
    "SALESFORCE_PASSWORD"
    "SALESFORCE_SECURITY_TOKEN"
)

for var in "${vars[@]}"; do
    value=$(heroku config:get "$var" --app democomponent-qrcode-generator 2>/dev/null)
    if [ -z "$value" ]; then
        echo "❌ $var: NOT SET"
    else
        # Mask sensitive values
        if [[ "$var" == *"PASSWORD"* ]] || [[ "$var" == *"SECRET"* ]] || [[ "$var" == *"TOKEN"* ]]; then
            len=${#value}
            if [ $len -gt 8 ]; then
                masked="${value:0:4}${value: -4}"
                echo "✅ $var: SET (length: $len, masked: ${value:0:4}****${value: -4})"
            else
                echo "✅ $var: SET (length: $len, masked: ***)"
            fi
        else
            echo "✅ $var: SET (value: $value)"
        fi
    fi
done

echo ""
echo "=== DONE ==="

