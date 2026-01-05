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
            print(f"=== SALESFORCE AUTHENTICATION DEBUG ===", flush=True)
            print(f"Base URL: {self.base_url}", flush=True)
            print(f"Session ID: {'SET' if self.session_id else 'NOT SET'}", flush=True)
            if self.session_id:
                print(f"Session ID length: {len(self.session_id)}", flush=True)
            print(f"Client ID: {'SET' if self.client_id else 'NOT SET'}", flush=True)
            if self.client_id:
                print(f"Client ID value: {self.client_id[:20]}...", flush=True)
            print(f"Client Secret: {'SET' if self.client_secret else 'NOT SET'}", flush=True)
            if self.client_secret:
                print(f"Client Secret length: {len(self.client_secret)}", flush=True)
            print(f"Username: {'SET' if self.username else 'NOT SET'}", flush=True)
            if self.username:
                print(f"Username value: {self.username}", flush=True)
            print(f"Password: {'SET' if self.password else 'NOT SET'}", flush=True)
            if self.password:
                print(f"Password length: {len(self.password)}", flush=True)
            print(f"Security Token: {'SET' if self.security_token else 'NOT SET'}", flush=True)
            if self.security_token:
                print(f"Security Token length: {len(self.security_token)}", flush=True)
            
            # Try Session ID first (preferred for API-only users)
            if self.session_id:
                print(f"Using Session ID authentication", flush=True)
                self.access_token = self.session_id
                print(f"Session ID authentication successful!", flush=True)
                print(f"Access token set. Length: {len(self.access_token) if self.access_token else 0}", flush=True)
                return True
            
            # Fallback to OAuth2 if no Session ID
            if self.client_id and self.client_secret and self.username and self.password:
                print(f"Using OAuth2 authentication", flush=True)
                
                # Build password - include security token if provided
                password = self.password
                if self.security_token:
                    password = f"{self.password}{self.security_token}"
                    print(f"Password includes security token. Combined length: {len(password)}", flush=True)
                else:
                    print(f"Password does not include security token. Length: {len(password)}", flush=True)
                
                data = {
                    'grant_type': 'password',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'username': self.username,
                    'password': password
                }
                
                # Don't log the actual password, but log the data structure
                print(f"Auth data (password hidden): grant_type={data['grant_type']}, client_id={data['client_id']}, username={data['username']}", flush=True)
                
                # Try My Domain URL first
                auth_url = f"{self.base_url}/services/oauth2/token"
                print(f"Attempting OAuth2 with My Domain URL: {auth_url}", flush=True)
                print(f"Making OAuth2 request...", flush=True)
                
                response = requests.post(auth_url, data=data)
                print(f"Response status: {response.status_code}", flush=True)
                print(f"Response headers: {dict(response.headers)}", flush=True)
                print(f"Response text: {response.text}", flush=True)
                
                # If My Domain URL fails with 400, try login.salesforce.com as fallback
                if response.status_code == 400:
                    print(f"\n⚠️  My Domain URL failed, trying login.salesforce.com as fallback...", flush=True)
                    auth_url_fallback = "https://login.salesforce.com/services/oauth2/token"
                    print(f"Attempting OAuth2 with login.salesforce.com: {auth_url_fallback}", flush=True)
                    
                    response_fallback = requests.post(auth_url_fallback, data=data)
                    print(f"Fallback response status: {response_fallback.status_code}", flush=True)
                    print(f"Fallback response text: {response_fallback.text}", flush=True)
                    
                    if response_fallback.status_code == 200:
                        print(f"✅ SUCCESS with login.salesforce.com!", flush=True)
                        response = response_fallback
                    else:
                        print(f"❌ Fallback also failed, using original response for error analysis", flush=True)
                        # Continue with original response for detailed error analysis below
                
                # If 400 error, show detailed debug info BEFORE raising exception
                if response.status_code == 400:
                    print(f"\n{'='*80}", flush=True)
                    print(f"=== OAuth2 400 BAD REQUEST - DETAILED ERROR ANALYSIS ===", flush=True)
                    print(f"{'='*80}\n", flush=True)
                    
                    # Parse error response
                    error_data = {}
                    error_code = None
                    error_description = None
                    
                    try:
                        error_data = response.json()
                        error_code = error_data.get('error', 'unknown_error')
                        error_description = error_data.get('error_description', 'No description provided')
                    except (ValueError, json.JSONDecodeError):
                        # If not JSON, try to extract error from text
                        error_text = response.text
                        print(f"⚠️  Response is not JSON format. Raw response:", flush=True)
                        print(f"   {error_text}", flush=True)
                        error_code = "non_json_response"
                        error_description = error_text[:200]  # First 200 chars
                    
                    print(f"📋 ERROR SUMMARY:", flush=True)
                    print(f"   Error Code: {error_code}", flush=True)
                    print(f"   Error Description: {error_description}", flush=True)
                    print(f"\n", flush=True)
                    
                    # Map error codes to specific issues and solutions
                    error_explanations = {
                        'invalid_grant': {
                            'title': '❌ AUTHENTICATION FAILURE',
                            'possible_causes': [
                                'Wrong username or password',
                                'Security token is incorrect or missing',
                                'Password format is wrong (should be: password + security_token concatenated)',
                                'Security token expired (reset it if you changed your password)',
                                'User account is locked or inactive'
                            ],
                            'checks': [
                                f'✓ Username: {self.username}',
                                f'✓ Password length: {len(self.password) if self.password else 0} characters',
                                f'✓ Security token: {"SET" if self.security_token else "❌ NOT SET"}',
                                f'✓ Combined password length: {len(self.password + (self.security_token or "")) if self.password else 0} characters'
                            ],
                            'solution': 'Verify username, password, and security token. Reset security token if needed.'
                        },
                        'invalid_client_id': {
                            'title': '❌ INVALID CLIENT ID',
                            'possible_causes': [
                                'Client ID (Consumer Key) is incorrect',
                                'Client ID format is wrong',
                                'Connected App might be deleted or inactive'
                            ],
                            'checks': [
                                f'✓ Client ID provided: {"YES" if self.client_id else "NO"}',
                                f'✓ Client ID length: {len(self.client_id) if self.client_id else 0} characters',
                                f'✓ Client ID starts with: {self.client_id[:20] + "..." if self.client_id and len(self.client_id) > 20 else self.client_id if self.client_id else "N/A"}'
                            ],
                            'solution': 'Verify Client ID matches the Consumer Key from Connected App settings in Salesforce.'
                        },
                        'invalid_client': {
                            'title': '❌ INVALID CLIENT SECRET',
                            'possible_causes': [
                                'Client Secret (Consumer Secret) is incorrect',
                                'Client Secret was regenerated and not updated in Heroku',
                                'Client Secret format is wrong'
                            ],
                            'checks': [
                                f'✓ Client Secret provided: {"YES" if self.client_secret else "NO"}',
                                f'✓ Client Secret length: {len(self.client_secret) if self.client_secret else 0} characters (should be 64 hex chars)'
                            ],
                            'solution': 'Verify Client Secret matches the Consumer Secret from Connected App. If regenerated, update Heroku config.'
                        },
                        'unsupported_grant_type': {
                            'title': '❌ UNSUPPORTED GRANT TYPE',
                            'possible_causes': [
                                'Password grant type not enabled in Connected App',
                                'Connected App only supports other OAuth flows'
                            ],
                            'checks': [
                                '✓ Grant type used: password',
                                '✓ Check Connected App OAuth settings in Salesforce'
                            ],
                            'solution': 'Enable OAuth Settings in Connected App and ensure password flow is allowed.'
                        }
                    }
                    
                    # Show specific error explanation
                    if error_code in error_explanations:
                        explanation = error_explanations[error_code]
                        print(f"{explanation['title']}", flush=True)
                        print(f"\n🔍 POSSIBLE CAUSES:", flush=True)
                        for cause in explanation['possible_causes']:
                            print(f"   • {cause}", flush=True)
                        print(f"\n✅ CURRENT VALUES:", flush=True)
                        for check in explanation['checks']:
                            print(f"   {check}", flush=True)
                        print(f"\n💡 SOLUTION:", flush=True)
                        print(f"   {explanation['solution']}", flush=True)
                    else:
                        print(f"⚠️  UNKNOWN ERROR CODE: {error_code}", flush=True)
                        print(f"   This is an uncommon error. Check Salesforce documentation.", flush=True)
                    
                    print(f"\n{'='*80}", flush=True)
                    print(f"📤 REQUEST DETAILS:", flush=True)
                    print(f"{'='*80}", flush=True)
                    print(f"   Auth URL: {auth_url}", flush=True)
                    print(f"   Request Method: {response.request.method}", flush=True)
                    print(f"   Request URL: {response.request.url}", flush=True)
                    print(f"   Grant Type: password", flush=True)
                    print(f"   Client ID: {self.client_id[:30]}..." if self.client_id and len(self.client_id) > 30 else f"   Client ID: {self.client_id}", flush=True)
                    print(f"   Client Secret: {'SET (' + str(len(self.client_secret)) + ' chars)' if self.client_secret else 'NOT SET'}", flush=True)
                    print(f"   Username: {self.username}", flush=True)
                    print(f"   Password: {'SET (' + str(len(self.password)) + ' chars)' if self.password else 'NOT SET'}", flush=True)
                    print(f"   Security Token: {'SET (' + str(len(self.security_token)) + ' chars)' if self.security_token else '❌ NOT SET'}", flush=True)
                    if self.password and self.security_token:
                        combined_length = len(self.password + self.security_token)
                        print(f"   Combined Password (password+token): {combined_length} chars", flush=True)
                    
                    print(f"\n{'='*80}", flush=True)
                    print(f"📥 RESPONSE DETAILS:", flush=True)
                    print(f"{'='*80}", flush=True)
                    print(f"   Status Code: {response.status_code}", flush=True)
                    print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}", flush=True)
                    print(f"   Full Response Text:", flush=True)
                    print(f"   {response.text}", flush=True)
                    
                    # Try to parse as JSON for pretty print
                    try:
                        error_json = response.json()
                        print(f"\n   Parsed JSON:", flush=True)
                        import json as json_module
                        print(f"   {json_module.dumps(error_json, indent=2)}", flush=True)
                    except:
                        pass
                    
                    print(f"\n{'='*80}", flush=True)
                    print(f"🔧 RECOMMENDED ACTIONS:", flush=True)
                    print(f"{'='*80}", flush=True)
                    
                    if error_code == 'invalid_grant':
                        print(f"   1. Verify username is correct: {self.username}", flush=True)
                        print(f"   2. Verify password is correct (length: {len(self.password) if self.password else 0})", flush=True)
                        if not self.security_token:
                            print(f"   3. ❌ CRITICAL: Security token is NOT SET! Get it from Salesforce:", flush=True)
                            print(f"      - Setup → My Personal Information → Reset My Security Token", flush=True)
                            print(f"      - Then: heroku config:set SALESFORCE_SECURITY_TOKEN=\"your_token\"", flush=True)
                        else:
                            print(f"   3. Verify security token is correct (current length: {len(self.security_token)})", flush=True)
                            print(f"      - If you changed your password, the token expired. Reset it.", flush=True)
                        print(f"   4. Password format should be: password + security_token (no space, concatenated)", flush=True)
                    elif error_code == 'invalid_client_id':
                        print(f"   1. Go to Salesforce Setup → App Manager → Your Connected App", flush=True)
                        print(f"   2. Verify Consumer Key matches: {self.client_id[:30]}..." if self.client_id and len(self.client_id) > 30 else f"   2. Verify Consumer Key matches: {self.client_id}", flush=True)
                        print(f"   3. Update Heroku config if Consumer Key changed", flush=True)
                    elif error_code == 'invalid_client':
                        print(f"   1. Go to Salesforce Setup → App Manager → Your Connected App", flush=True)
                        print(f"   2. Click 'Manage' → 'View' to see Consumer Secret", flush=True)
                        print(f"   3. If regenerated, update Heroku: heroku config:set SALESFORCE_CLIENT_SECRET=\"new_secret\"", flush=True)
                    
                    print(f"\n{'='*80}", flush=True)
                    print(f"ERROR: OAuth2 authentication failed with 400 error", flush=True)
                    print(f"{'='*80}\n", flush=True)
                    return False
                
                response.raise_for_status()
                
                auth_data = response.json()
                self.access_token = auth_data['access_token']
                self.base_url = auth_data['instance_url']
                
                print(f"OAuth2 authentication successful!", flush=True)
                print(f"Access token: {'SET' if self.access_token else 'NOT SET'}", flush=True)
                if self.access_token:
                    print(f"Access token length: {len(self.access_token)}", flush=True)
                print(f"Instance URL: {self.base_url}", flush=True)
                
                return True
            
            print(f"No valid authentication method available", flush=True)
            print(f"Available methods check:", flush=True)
            print(f"  - Session ID: {'YES' if self.session_id else 'NO'}", flush=True)
            print(f"  - OAuth2 (client_id): {'YES' if self.client_id else 'NO'}", flush=True)
            print(f"  - OAuth2 (client_secret): {'YES' if self.client_secret else 'NO'}", flush=True)
            print(f"  - OAuth2 (username): {'YES' if self.username else 'NO'}", flush=True)
            print(f"  - OAuth2 (password): {'YES' if self.password else 'NO'}", flush=True)
            return False
            
        except Exception as e:
            print(f"=== SALESFORCE AUTHENTICATION ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def upload_file_to_record(
        self, 
        record_id: str, 
        file_path: str, 
        file_name: str,
        applink_auth_token: Optional[str] = None,
        applink_instance_url: Optional[str] = None
    ) -> Dict[str, Any]:
        # Store applink_auth_token for use in error handling
        self._applink_auth_token = applink_auth_token
        """Upload a file to a Salesforce record as a ContentDocument"""
        try:
            print(f"=== UPLOAD FILE TO RECORD DEBUG ===")
            print(f"Record ID: {record_id}")
            print(f"File path: {file_path}")
            print(f"File name: {file_name}")
            
            # Use AppLink authentication if provided
            if applink_auth_token:
                print(f"Attempting to use session token from form", flush=True)
                # Extract token from "Bearer <token>" format if needed
                if applink_auth_token.startswith("Bearer "):
                    session_token = applink_auth_token[7:]  # Remove "Bearer " prefix
                else:
                    session_token = applink_auth_token
                
                # Use AppLink instance URL if provided, otherwise keep existing
                if applink_instance_url:
                    self.base_url = applink_instance_url.rstrip('/')
                    print(f"Using instance URL from form: {self.base_url}", flush=True)
                
                print(f"Session token from form. Length: {len(session_token)}", flush=True)
                print(f"NOTE: Session tokens from Apex may not work with REST API. Will try first, then fall back to OAuth2 if needed.", flush=True)
                
                # Try the session token first, but we'll fall back to OAuth2 if it fails
                self.access_token = session_token
            elif not self.access_token:
                print(f"Access token not available, attempting OAuth2 authentication...")
                if not await self.authenticate():
                    return {"status": "error", "message": "Authentication failed"}
            else:
                print(f"Using existing access token (OAuth2/Session ID)", flush=True)
            
            # Step 1: Create ContentVersion
            print(f"=== STEP 1: Creating ContentVersion ===")
            content_version = await self.create_content_version(file_path, file_name, applink_auth_token)
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
    
    async def create_content_version(self, file_path: str, file_name: str, applink_auth_token: Optional[str] = None) -> Dict[str, Any]:
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
            
            print(f"Making ContentVersion API call to: {url}", flush=True)
            print(f"Authorization header: Bearer {self.access_token[:30]}... (length: {len(self.access_token)})", flush=True)
            response = requests.post(url, headers=headers, json=content_version_data)
            
            # Log response details for debugging
            print(f"Response status: {response.status_code}", flush=True)
            if response.status_code != 200:
                print(f"Response text: {response.text}", flush=True)
                print(f"Response headers: {dict(response.headers)}", flush=True)
            
            response.raise_for_status()
            
            result = response.json()
            return {
                "status": "success",
                "id": result['id']
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"ContentVersion creation failed: {str(e)}"
            error_response_text = ""
            if hasattr(e.response, 'text'):
                error_response_text = e.response.text
                error_msg += f" - Response: {error_response_text}"
            print(f"HTTP Error: {error_msg}", flush=True)
            
            # If we got 401 with INVALID_SESSION_ID, session token doesn't work with REST API
            # Fall back to OAuth2 authentication
            if e.response.status_code == 401 and applink_auth_token and "INVALID_SESSION_ID" in error_response_text:
                print(f"⚠️  Session token from Apex is not valid for REST API (INVALID_SESSION_ID)", flush=True)
                print(f"Falling back to OAuth2 authentication...", flush=True)
                # Clear the failed token
                self.access_token = None
                # Try OAuth2
                if await self.authenticate():
                    print(f"✓ OAuth2 authentication successful. Retrying ContentVersion creation...", flush=True)
                    # Retry the request with OAuth2 token
                    try:
                        response = requests.post(url, headers={
                            'Authorization': f'Bearer {self.access_token}',
                            'Content-Type': 'application/json'
                        }, json=content_version_data)
                        response.raise_for_status()
                        result = response.json()
                        print(f"✓ ContentVersion created successfully with OAuth2 token", flush=True)
                        return {
                            "status": "success",
                            "id": result['id']
                        }
                    except requests.exceptions.HTTPError as retry_error:
                        retry_error_msg = f"OAuth2 retry also failed: {str(retry_error)}"
                        if hasattr(retry_error.response, 'text'):
                            retry_error_msg += f" - Response: {retry_error.response.text}"
                        print(f"✗ {retry_error_msg}", flush=True)
                        return {"status": "error", "message": retry_error_msg}
                else:
                    return {"status": "error", "message": "Session token invalid for REST API and OAuth2 authentication also failed"}
            
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"ContentVersion creation failed: {str(e)}"
            print(f"Exception: {error_msg}", flush=True)
            return {"status": "error", "message": error_msg}
    
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
