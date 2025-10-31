"""
Salesforce Integration Module for QR Code Generator
Handles authentication and file uploads to Salesforce
"""

import requests
import json
import os
from typing import Dict, Any, Optional

class SalesforceAPI:
    def __init__(self):
        self.base_url = os.getenv('SALESFORCE_INSTANCE_URL', 'https://your-instance.salesforce.com')
        self.session_id = os.getenv('SALESFORCE_SESSION_ID')
        self.access_token = os.getenv('SALESFORCE_ACCESS_TOKEN')
        self.client_id = os.getenv('SALESFORCE_CLIENT_ID')
        self.client_secret = os.getenv('SALESFORCE_CLIENT_SECRET')
        self.username = os.getenv('SALESFORCE_USERNAME')
        self.password = os.getenv('SALESFORCE_PASSWORD')
        self.security_token = os.getenv('SALESFORCE_SECURITY_TOKEN')
        
    async def authenticate(self) -> bool:
        """Authenticate with Salesforce using Session ID or OAuth2"""
        try:
            print(f"=== SALESFORCE AUTHENTICATION DEBUG ===")
            print(f"Base URL: {self.base_url}")
            print(f"Session ID: {'SET' if self.session_id else 'NOT SET'}")
            print(f"Client ID: {'SET' if self.client_id else 'NOT SET'}")
            print(f"Client Secret: {'SET' if self.client_secret else 'NOT SET'}")
            print(f"Username: {'SET' if self.username else 'NOT SET'}")
            print(f"Password: {'SET' if self.password else 'NOT SET'}")
            print(f"Security Token: {'SET' if self.security_token else 'NOT SET'}")
            
            # Try Session ID first (preferred for API-only users)
            if self.session_id:
                print(f"Using Session ID authentication")
                self.access_token = self.session_id
                print(f"Session ID authentication successful!")
                return True
            
            # Fallback to OAuth2 if no Session ID
            if self.client_id and self.client_secret and self.username and self.password:
                print(f"Using OAuth2 authentication")
                auth_url = f"{self.base_url}/services/oauth2/token"
                print(f"Auth URL: {auth_url}")
                
                # Build password - include security token if provided
                password = self.password
                if self.security_token:
                    password = f"{self.password}{self.security_token}"
                
                data = {
                    'grant_type': 'password',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'username': self.username,
                    'password': password
                }
                
                # Don't log the actual password, but log the data structure
                print(f"Auth data (password hidden): grant_type={data['grant_type']}, client_id={data['client_id']}, username={data['username']}")
                
                response = requests.post(auth_url, data=data)
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response text: {response.text}")
                
                # If 400 error, show detailed debug info
                if response.status_code == 400:
                    print(f"=== OAuth2 400 ERROR DEBUG ===")
                    print(f"Auth URL: {auth_url}")
                    print(f"Request headers: {dict(response.request.headers)}")
                    print(f"Full response: {response.text}")
                    print(f"Request data (password hidden): grant_type=password, client_id={self.client_id}, username={self.username}")
                
                response.raise_for_status()
                
                auth_data = response.json()
                self.access_token = auth_data['access_token']
                self.base_url = auth_data['instance_url']
                
                print(f"OAuth2 authentication successful!")
                print(f"Access token: {'SET' if self.access_token else 'NOT SET'}")
                print(f"Instance URL: {self.base_url}")
                
                return True
            
            print(f"No valid authentication method available")
            return False
            
        except Exception as e:
            print(f"=== SALESFORCE AUTHENTICATION ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def upload_file_to_record(self, record_id: str, file_path: str, file_name: str) -> Dict[str, Any]:
        """Upload a file to a Salesforce record as a ContentDocument"""
        try:
            print(f"=== UPLOAD FILE TO RECORD DEBUG ===")
            print(f"Record ID: {record_id}")
            print(f"File path: {file_path}")
            print(f"File name: {file_name}")
            print(f"Access token: {'SET' if self.access_token else 'NOT SET'}")
            
            if not self.access_token:
                print(f"Access token not available, attempting authentication...")
                if not await self.authenticate():
                    return {"status": "error", "message": "Authentication failed"}
            
            # Step 1: Create ContentVersion
            print(f"=== STEP 1: Creating ContentVersion ===")
            content_version = await self.create_content_version(file_path, file_name)
            print(f"ContentVersion result: {content_version}")
            if content_version.get('status') == 'error':
                return content_version
            
            # Step 2: Get ContentDocument ID from ContentVersion
            print(f"=== STEP 2: Getting ContentDocument ID ===")
            content_document_id = await self.get_content_document_id(content_version['id'])
            print(f"ContentDocument ID: {content_document_id}")
            if not content_document_id:
                return {"status": "error", "message": "Failed to get ContentDocument ID"}
            
            # Step 3: Create ContentDocumentLink to associate with record
            print(f"=== STEP 3: Creating ContentDocumentLink ===")
            link_result = await self.create_content_document_link(record_id, content_document_id)
            print(f"ContentDocumentLink result: {link_result}")
            if link_result.get('status') == 'error':
                return link_result
            
            print(f"=== UPLOAD SUCCESSFUL ===")
            return {
                "status": "success",
                "message": f"File {file_name} successfully attached to record {record_id}",
                "content_document_id": content_document_id,
                "content_version_id": content_version['id']
            }
            
        except Exception as e:
            print(f"=== UPLOAD FILE ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {"status": "error", "message": f"Upload failed: {str(e)}"}
    
    async def create_content_version(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Create a ContentVersion record in Salesforce"""
        try:
            # Read file content
            with open(file_path, 'rb') as file:
                file_content = file.read()
            
            # Encode file content to base64
            import base64
            file_data = base64.b64encode(file_content).decode('utf-8')
            
            # Prepare ContentVersion data
            content_version_data = {
                "Title": file_name,
                "PathOnClient": file_name,
                "VersionData": file_data,
                "IsMajorVersion": True
            }
            
            # Make API call
            url = f"{self.base_url}/services/data/v58.0/sobjects/ContentVersion"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json=content_version_data)
            response.raise_for_status()
            
            result = response.json()
            return {
                "status": "success",
                "id": result['id']
            }
            
        except Exception as e:
            return {"status": "error", "message": f"ContentVersion creation failed: {str(e)}"}
    
    async def get_content_document_id(self, content_version_id: str) -> Optional[str]:
        """Get ContentDocument ID from ContentVersion ID"""
        try:
            url = f"{self.base_url}/services/data/v58.0/sobjects/ContentVersion/{content_version_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('ContentDocumentId')
            
        except Exception as e:
            print(f"Failed to get ContentDocument ID: {str(e)}")
            return None
    
    async def create_content_document_link(self, record_id: str, content_document_id: str) -> Dict[str, Any]:
        """Create ContentDocumentLink to associate file with record"""
        try:
            link_data = {
                "ContentDocumentId": content_document_id,
                "LinkedEntityId": record_id,
                "ShareType": "V"
            }
            
            url = f"{self.base_url}/services/data/v58.0/sobjects/ContentDocumentLink"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json=link_data)
            response.raise_for_status()
            
            result = response.json()
            return {
                "status": "success",
                "id": result['id']
            }
            
        except Exception as e:
            return {"status": "error", "message": f"ContentDocumentLink creation failed: {str(e)}"}
    
    async def get_record_info(self, record_id: str) -> Dict[str, Any]:
        """Get basic information about a Salesforce record"""
        try:
            if not self.access_token:
                if not await self.authenticate():
                    return {"status": "error", "message": "Authentication failed"}
            
            # Determine object type from record ID prefix
            object_type = self.get_object_type_from_id(record_id)
            
            url = f"{self.base_url}/services/data/v58.0/sobjects/{object_type}/{record_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.json()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to get record info: {str(e)}"}
    
    def get_object_type_from_id(self, record_id: str) -> str:
        """Determine Salesforce object type from record ID prefix"""
        prefix_map = {
            '001': 'Account',
            '003': 'Contact',
            '00Q': 'Lead',
            '006': 'Opportunity',
            '00T': 'Task',
            '00U': 'Event',
            'a00': 'Custom_Object__c'  # Example custom object
        }
        
        prefix = record_id[:3]
        return prefix_map.get(prefix, 'Unknown')

# Global instance
salesforce_api = SalesforceAPI()
