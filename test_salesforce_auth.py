#!/usr/bin/env python3
"""
Test script to verify Salesforce OAuth2 credentials
Run this to test if your credentials work before deploying
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get credentials from environment
instance_url = os.getenv('SALESFORCE_INSTANCE_URL', 'https://trailsignup-a59cbb1bc47f48.my.salesforce.com')
client_id = os.getenv('SALESFORCE_CLIENT_ID')
client_secret = os.getenv('SALESFORCE_CLIENT_SECRET')
username = os.getenv('SALESFORCE_USERNAME')
password = os.getenv('SALESFORCE_PASSWORD')
security_token = os.getenv('SALESFORCE_SECURITY_TOKEN')

print("=" * 80)
print("Salesforce OAuth2 Credential Test")
print("=" * 80)
print(f"\nInstance URL: {instance_url}")
print(f"Client ID: {client_id[:30]}..." if client_id and len(client_id) > 30 else f"Client ID: {client_id}")
print(f"Client Secret: {'SET' if client_secret else 'NOT SET'} ({len(client_secret) if client_secret else 0} chars)")
print(f"Username: {username}")
print(f"Password: {'SET' if password else 'NOT SET'} ({len(password) if password else 0} chars)")
print(f"Security Token: {'SET' if security_token else 'NOT SET'} ({len(security_token) if security_token else 0} chars)")

if not all([client_id, client_secret, username, password, security_token]):
    print("\n❌ ERROR: Missing required credentials!")
    exit(1)

# Build combined password
combined_password = f"{password}{security_token}"
print(f"\nCombined Password: password({len(password)}) + token({len(security_token)}) = {len(combined_password)} chars")

# Test OAuth2
auth_url = f"{instance_url}/services/oauth2/token"
print(f"\nAuth URL: {auth_url}")
print("Making OAuth2 request...")

data = {
    'grant_type': 'password',
    'client_id': client_id,
    'client_secret': client_secret,
    'username': username,
    'password': combined_password
}

try:
    response = requests.post(auth_url, data=data)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! OAuth2 authentication worked!")
        print(f"Access Token: {result.get('access_token', 'N/A')[:30]}...")
        print(f"Instance URL: {result.get('instance_url', 'N/A')}")
    else:
        print(f"\n❌ FAILED: Status {response.status_code}")
        try:
            error = response.json()
            print(f"Error: {error}")
        except:
            print(f"Error text: {response.text}")
            
except Exception as e:
    print(f"\n❌ EXCEPTION: {str(e)}")
    import traceback
    traceback.print_exc()

