#!/bin/bash

# QR Code Generator - Heroku Deployment Script
echo "🚀 Deploying QR Code Generator to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first."
    echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please log in to Heroku first:"
    heroku login
fi

# Create Heroku app (if it doesn't exist)
echo "📱 Creating Heroku app..."
APP_NAME="qr-code-generator-$(date +%s)"
heroku create $APP_NAME

# Set environment variables
echo "🔧 Setting up environment variables..."
echo "Please provide your Salesforce credentials:"

read -p "Salesforce Instance URL (e.g., https://your-instance.salesforce.com): " SALESFORCE_URL
read -p "Salesforce Client ID: " CLIENT_ID
read -p "Salesforce Client Secret: " CLIENT_SECRET
read -p "Salesforce Username: " USERNAME
read -p "Salesforce Password: " PASSWORD
read -p "Salesforce Security Token: " SECURITY_TOKEN

# Set environment variables in Heroku
heroku config:set SALESFORCE_INSTANCE_URL="$SALESFORCE_URL" --app $APP_NAME
heroku config:set SALESFORCE_CLIENT_ID="$CLIENT_ID" --app $APP_NAME
heroku config:set SALESFORCE_CLIENT_SECRET="$CLIENT_SECRET" --app $APP_NAME
heroku config:set SALESFORCE_USERNAME="$USERNAME" --app $APP_NAME
heroku config:set SALESFORCE_PASSWORD="$PASSWORD" --app $APP_NAME
heroku config:set SALESFORCE_SECURITY_TOKEN="$SECURITY_TOKEN" --app $APP_NAME

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for QR Code Generator"
fi

# Add Heroku remote
echo "🔗 Adding Heroku remote..."
heroku git:remote -a $APP_NAME

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy QR Code Generator to Heroku"
git push heroku main

# Open the app
echo "🌐 Opening your app..."
heroku open --app $APP_NAME

echo "✅ Deployment complete!"
echo "📱 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📋 Update your LWC component with this URL: https://$APP_NAME.herokuapp.com"
echo ""
echo "🔧 Next steps:"
echo "1. Update the herokuEndpoint in your LWC component"
echo "2. Deploy the LWC to your Salesforce org"
echo "3. Test the QR code generation and file upload flow"
