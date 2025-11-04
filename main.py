from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import qrcode
import io
import requests
from PIL import Image, ImageDraw
from typing import Optional
import base64
import os
import sys
import uuid
from datetime import datetime
from salesforce_integration import salesforce_api

app = FastAPI(
    title="QR Code Generator API",
    description="API for generating QR codes from text, URLs, and other data",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Print all configuration variables at startup"""
    print("=" * 80)
    print("=== APPLICATION STARTUP - CONFIGURATION VARIABLES ===")
    print("=" * 80)
    
    # Salesforce configuration
    salesforce_vars = [
        'SALESFORCE_INSTANCE_URL',
        'SALESFORCE_SESSION_ID',
        'SALESFORCE_ACCESS_TOKEN',
        'SALESFORCE_CLIENT_ID',
        'SALESFORCE_CLIENT_SECRET',
        'SALESFORCE_USERNAME',
        'SALESFORCE_PASSWORD',
        'SALESFORCE_SECURITY_TOKEN'
    ]
    
    print("\n--- Salesforce Configuration ---")
    for var in salesforce_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'SECRET' in var or 'TOKEN' in var or 'SESSION' in var or 'ACCESS' in var:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print(f"{var}: {masked} (length: {len(value)})")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: NOT SET")
    
    # General configuration
    print("\n--- General Configuration ---")
    general_vars = [
        'ENVIRONMENT',
        'SECRET_KEY',
        'API_HOST',
        'API_PORT'
    ]
    
    for var in general_vars:
        value = os.getenv(var)
        print(f"{var}: {value if value else 'NOT SET (using default)'}")
    
    print("\n--- Environment Info ---")
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Upload Directory Exists: {os.path.exists('uploads')}")
    
    print("=" * 80)
    print("=== END CONFIGURATION VARIABLES ===")
    print("=" * 80)
    print(flush=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Heroku deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

class QRCodeRequest(BaseModel):
    data: str
    size: Optional[int] = 10
    border: Optional[int] = 4
    fill_color: Optional[str] = "black"
    back_color: Optional[str] = "white"
    company_logo_url: Optional[str] = None
    file_name: Optional[str] = None
    record_id: Optional[str] = None

class FileUploadRequest(BaseModel):
    record_id: str
    file_name: str
    company_logo_url: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "QR Code Generator API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/generate")
async def generate_qr_code(request: QRCodeRequest):
    """Generate a QR code from the provided data with optional company logo"""
    try:
        print(f"=== GENERATE QR CODE DEBUG ===", flush=True)
        print(f"Data: {request.data[:100]}..." if len(request.data) > 100 else f"Data: {request.data}", flush=True)
        print(f"Size: {request.size}", flush=True)
        print(f"Border: {request.border}", flush=True)
        print(f"Fill color: {request.fill_color}", flush=True)
        print(f"Back color: {request.back_color}", flush=True)
        print(f"Company logo URL: {request.company_logo_url}", flush=True)
        print(f"File name: {request.file_name}", flush=True)
        print(f"Record ID: {request.record_id}", flush=True)
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=request.size,
            border=request.border,
        )
        
        # Add data to QR code
        qr.add_data(request.data)
        qr.make(fit=True)
        print(f"QR code generated successfully", flush=True)
        
        # Create image
        img = qr.make_image(fill_color=request.fill_color, back_color=request.back_color)
        print(f"QR image created. Size: {img.size}, Mode: {img.mode}", flush=True)
        
        # Add company logo if provided
        if request.company_logo_url:
            print(f"Adding company logo...", flush=True)
            img = await add_company_logo(img, request.company_logo_url)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        print(f"Image converted to bytes. Size: {len(img_byte_arr.getvalue())} bytes", flush=True)
        
        # Generate filename
        filename = f"{request.file_name}_qr_code.png" if request.file_name else "qr_code.png"
        print(f"Generated filename: {filename}", flush=True)
        print(f"=== END GENERATE QR CODE DEBUG ===", flush=True)
        
        return StreamingResponse(
            io.BytesIO(img_byte_arr.getvalue()),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
        
    except Exception as e:
        print(f"=== GENERATE QR CODE ERROR ===", flush=True)
        print(f"Error: {str(e)}", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        import traceback
        print(f"Traceback: {traceback.format_exc()}", flush=True)
        print(f"=== END GENERATE QR CODE ERROR ===", flush=True)
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")

async def add_company_logo(qr_img, logo_url):
    """Add company logo to the center of the QR code"""
    try:
        print(f"=== ADD COMPANY LOGO DEBUG ===", flush=True)
        print(f"Logo URL: {logo_url}", flush=True)
        print(f"QR Image size: {qr_img.size}", flush=True)
        print(f"QR Image mode: {qr_img.mode}", flush=True)
        
        # Download logo
        print(f"Downloading logo from URL...", flush=True)
        response = requests.get(logo_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        print(f"Response status code: {response.status_code}", flush=True)
        print(f"Response headers: {dict(response.headers)}", flush=True)
        print(f"Response content length: {len(response.content)} bytes", flush=True)
        print(f"Response content type: {response.headers.get('Content-Type', 'Unknown')}", flush=True)
        
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        print(f"Content-Type header: {content_type}", flush=True)
        
        # Try to identify the image format
        content_bytes = response.content
        print(f"First 20 bytes (hex): {content_bytes[:20].hex()}", flush=True)
        print(f"First 20 bytes (ascii attempt): {content_bytes[:20]}", flush=True)
        
        # Open logo image
        print(f"Attempting to open image with PIL...", flush=True)
        logo_bytes_io = io.BytesIO(content_bytes)
        print(f"BytesIO object created: {type(logo_bytes_io)}", flush=True)
        
        try:
            logo = Image.open(logo_bytes_io)
            print(f"Image opened successfully!", flush=True)
            print(f"Image format: {logo.format}", flush=True)
            print(f"Image mode: {logo.mode}", flush=True)
            print(f"Image size: {logo.size}", flush=True)
        except Exception as img_error:
            print(f"ERROR: Failed to open image with PIL: {str(img_error)}", flush=True)
            print(f"Error type: {type(img_error).__name__}", flush=True)
            import traceback
            print(f"Traceback: {traceback.format_exc()}", flush=True)
            raise
        
        # Convert to RGBA if needed
        if logo.mode != 'RGBA':
            print(f"Converting image from {logo.mode} to RGBA...", flush=True)
            logo = logo.convert('RGBA')
        
        # Calculate logo size (20% of QR code size)
        qr_width, qr_height = qr_img.size
        logo_size = min(qr_width, qr_height) // 5
        print(f"Calculated logo size: {logo_size}", flush=True)
        
        # Resize logo maintaining aspect ratio
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        print(f"Logo resized to: {logo.size}", flush=True)
        
        # Calculate position (center of QR code)
        logo_width, logo_height = logo.size
        position = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)
        print(f"Logo position: {position}", flush=True)
        
        # Create a white background for the logo
        logo_bg = Image.new('RGBA', (logo_width + 10, logo_height + 10), (255, 255, 255, 255))
        logo_bg.paste(logo, (5, 5), logo)
        
        # Paste logo onto QR code
        qr_img.paste(logo_bg, position, logo_bg)
        print(f"Logo successfully added to QR code!", flush=True)
        print(f"=== END ADD COMPANY LOGO DEBUG ===", flush=True)
        
        return qr_img
        
    except Exception as e:
        print(f"=== COMPANY LOGO ERROR ===", flush=True)
        print(f"Warning: Could not add company logo: {str(e)}", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        import traceback
        print(f"Traceback: {traceback.format_exc()}", flush=True)
        print(f"=== END COMPANY LOGO ERROR ===", flush=True)
        return qr_img

@app.get("/form/{record_id}")
async def show_upload_form(record_id: str, company_logo_url: str = None, file_name: str = None):
    """Display the upload form for file submission"""
    form_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>File Upload Form</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .logo {{
                max-width: 200px;
                max-height: 100px;
                margin-bottom: 20px;
            }}
            .form-group {{
                margin: 20px 0;
                text-align: left;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #333;
            }}
            input[type="file"] {{
                width: 100%;
                padding: 10px;
                border: 2px dashed #ddd;
                border-radius: 5px;
                background: #fafafa;
            }}
            button {{
                background: #0070d2;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }}
            button:hover {{
                background: #005fb2;
            }}
            .success {{
                color: #4bca81;
                font-weight: bold;
                margin: 20px 0;
            }}
            .error {{
                color: #ea001e;
                font-weight: bold;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>File Upload</h1>
            {f'<img src="{company_logo_url}" alt="Company Logo" class="logo" onerror="this.style.display=\'none\'">' if company_logo_url else ''}
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Select File to Upload:</label>
                    <input type="file" id="file" name="file" required>
                </div>
                
                <button type="submit">Upload File</button>
                <button type="button" onclick="window.close()">Close Window</button>
            </form>
            
            <div id="message"></div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const formData = new FormData();
                const fileInput = document.getElementById('file');
                const file = fileInput.files[0];
                
                if (!file) {{
                    showMessage('Please select a file to upload.', 'error');
                    return;
                }}
                
                formData.append('file', file);
                formData.append('record_id', '{record_id}');
                formData.append('file_name', '{file_name or "uploaded_file"}');
                
                try {{
                    const response = await fetch('/upload', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok) {{
                        showMessage('File uploaded successfully! You may now close this window.', 'success');
                        document.getElementById('uploadForm').style.display = 'none';
                    }} else {{
                        showMessage('Error: ' + result.detail, 'error');
                    }}
                }} catch (error) {{
                    showMessage('Error uploading file: ' + error.message, 'error');
                }}
            }});
            
            function showMessage(text, type) {{
                const messageDiv = document.getElementById('message');
                messageDiv.innerHTML = '<div class="' + type + '">' + text + '</div>';
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=form_html)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    record_id: str = Form(...),
    file_name: str = Form(...)
):
    """Handle file upload and send to Salesforce"""
    try:
        print(f"=== UPLOAD FILE ENDPOINT DEBUG ===", flush=True)
        print(f"Received file: {file.filename}", flush=True)
        print(f"File content type: {file.content_type}", flush=True)
        print(f"Record ID: {record_id}", flush=True)
        print(f"File name: {file_name}", flush=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_name}_{uuid.uuid4().hex[:8]}{file_extension}"
        print(f"Unique filename: {unique_filename}", flush=True)
        
        # Save file locally
        file_path = f"uploads/{unique_filename}"
        print(f"Saving file to: {file_path}", flush=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            print(f"File saved. Size: {len(content)} bytes", flush=True)
        
        # Verify file exists
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"File verified. Size on disk: {file_size} bytes", flush=True)
        else:
            print(f"ERROR: File was not saved successfully!", flush=True)
        
        # Integrate with Salesforce API to attach the file
        print(f"Calling Salesforce API to upload file...", flush=True)
        salesforce_result = await salesforce_api.upload_file_to_record(record_id, file_path, file_name)
        print(f"Salesforce result: {salesforce_result}", flush=True)
        print(f"=== END UPLOAD FILE ENDPOINT DEBUG ===", flush=True)
        
        return {
            "message": "File uploaded successfully",
            "record_id": record_id,
            "file_name": file_name,
            "salesforce_result": salesforce_result
        }
        
    except Exception as e:
        print(f"=== UPLOAD FILE ERROR ===", flush=True)
        print(f"Error: {str(e)}", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        import traceback
        print(f"Traceback: {traceback.format_exc()}", flush=True)
        print(f"=== END UPLOAD FILE ERROR ===", flush=True)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

# This function is now handled by the Salesforce integration module

@app.get("/generate/{data}")
async def generate_qr_code_simple(data: str, size: int = 10, border: int = 4):
    """Generate a QR code with simple URL parameters"""
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        
        # Add data to QR code
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image()
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(
            io.BytesIO(img_byte_arr.getvalue()),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=qr_code.png"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
