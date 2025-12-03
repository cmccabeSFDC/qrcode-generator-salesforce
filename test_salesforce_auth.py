#!/usr/bin/env python3
"""
Test Salesforce OAuth2 Authentication
This script tests authentication outside of Heroku to isolate the issue.
"""

import requests
import os
import sys

def test_oauth2_auth():
    """Test OAuth2 password flow authentication"""
    
    print("=" * 80)
    print("Salesforce OAuth2 Authentication Test")
    print("=" * 80)
    print()
    
    # Get credentials from environment or prompt
    instance_url = os.getenv('SALESFORCE_INSTANCE_URL', 'https://trailsignup-a59cbb1bc47f48.my.salesforce.com')
    client_id = os.getenv('SALESFORCE_CLIENT_ID')
    client_secret = os.getenv('SALESFORCE_CLIENT_SECRET')
    username = os.getenv('SALESFORCE_USERNAME', 'trailsignup.a59cbb1bc47f48@salesforce.com')
    password = os.getenv('SALESFORCE_PASSWORD', 'Salesforce1!')
    security_token = os.getenv('SALESFORCE_SECURITY_TOKEN')
    
    # Prompt for missing values
    if not client_id:
        client_id = input("Enter Consumer Key (Client ID): ").strip()
    if not client_secret:
        client_secret = input("Enter Consumer Secret (Client Secret): ").strip()
    if not security_token:
        security_token = input("Enter Security Token (24 chars): ").strip()
    
    print()
    print("Configuration:")
    print(f"  Instance URL: {instance_url}")
    print(f"  Client ID: {client_id[:30]}..." if client_id and len(client_id) > 30 else f"  Client ID: {client_id}")
    print(f"  Client Secret: {'SET (' + str(len(client_secret)) + ' chars)' if client_secret else 'NOT SET'}")
    print(f"  Username: {username}")
    print(f"  Password: {'SET (' + str(len(password)) + ' chars)' if password else 'NOT SET'}")
    print(f"  Security Token: {'SET (' + str(len(security_token)) + ' chars)' if security_token else 'NOT SET'}")
    print()
    
    # Test with My Domain URL first
    print("=" * 80)
    print("Test 1: Using My Domain URL")
    print("=" * 80)
    auth_url_1 = f"{instance_url}/services/oauth2/token"
    print(f"Auth URL: {auth_url_1}")
    
    combined_password = f"{password}{security_token}" if security_token else password
    print(f"Combined password length: {len(combined_password)}")
    print()
    
    data = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': combined_password
    }
    
    try:
        print("Making OAuth2 request...")
        response = requests.post(auth_url_1, data=data, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"Instance URL: {result.get('instance_url', 'N/A')}")
            print(f"Token Type: {result.get('token_type', 'N/A')}")
            return True
        else:
            print("❌ FAILED")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'unknown')}")
                print(f"Error Description: {error_data.get('error_description', 'No description')}")
            except:
                print(f"Error: {response.text}")
            
            # Test with login.salesforce.com as fallback
            print()
            print("=" * 80)
            print("Test 2: Using login.salesforce.com (Production)")
            print("=" * 80)
            auth_url_2 = "https://login.salesforce.com/services/oauth2/token"
            print(f"Auth URL: {auth_url_2}")
            print()
            
            print("Making OAuth2 request to login.salesforce.com...")
            response2 = requests.post(auth_url_2, data=data, timeout=10)
            
            print(f"Response Status: {response2.status_code}")
            print(f"Response Text: {response2.text}")
            print()
            
            if response2.status_code == 200:
                result = response2.json()
                print("✅ SUCCESS with login.salesforce.com!")
                print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
                print(f"Instance URL: {result.get('instance_url', 'N/A')}")
                print()
                print("💡 SOLUTION: Use login.salesforce.com for OAuth2 token endpoint")
                print("   Update SALESFORCE_INSTANCE_URL to: https://login.salesforce.com")
                return True
            else:
                print("❌ FAILED with login.salesforce.com too")
                try:
                    error_data = response2.json()
                    print(f"Error: {error_data.get('error', 'unknown')}")
                    print(f"Error Description: {error_data.get('error_description', 'No description')}")
                except:
                    print(f"Error: {response2.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_oauth2_auth()
    sys.exit(0 if success else 1)

