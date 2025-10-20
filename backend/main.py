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
import uuid
from datetime import datetime
from salesforce_integration import salesforce_api

app = FastAPI(
    title="QR Code Generator API",
    description="API for generating QR codes from text, URLs, and other data",
    version="1.0.0"
)

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
        
        # Create image
        img = qr.make_image(fill_color=request.fill_color, back_color=request.back_color)
        
        # Add company logo if provided
        if request.company_logo_url:
            img = await add_company_logo(img, request.company_logo_url)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Generate filename
        filename = f"{request.file_name}_qr_code.png" if request.file_name else "qr_code.png"
        
        return StreamingResponse(
            io.BytesIO(img_byte_arr.getvalue()),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")

async def add_company_logo(qr_img, logo_url):
    """Add company logo to the center of the QR code"""
    try:
        # Download logo
        response = requests.get(logo_url, timeout=10)
        response.raise_for_status()
        
        # Open logo image
        logo = Image.open(io.BytesIO(response.content))
        
        # Convert to RGBA if needed
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Calculate logo size (20% of QR code size)
        qr_width, qr_height = qr_img.size
        logo_size = min(qr_width, qr_height) // 5
        
        # Resize logo maintaining aspect ratio
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Calculate position (center of QR code)
        logo_width, logo_height = logo.size
        position = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)
        
        # Create a white background for the logo
        logo_bg = Image.new('RGBA', (logo_width + 10, logo_height + 10), (255, 255, 255, 255))
        logo_bg.paste(logo, (5, 5), logo)
        
        # Paste logo onto QR code
        qr_img.paste(logo_bg, position, logo_bg)
        
        return qr_img
        
    except Exception as e:
        print(f"Warning: Could not add company logo: {str(e)}")
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
        print(f"=== FILE UPLOAD DEBUG START ===")
        print(f"Received file: {file.filename}")
        print(f"Record ID: {record_id}")
        print(f"File name: {file_name}")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_name}_{uuid.uuid4().hex[:8]}{file_extension}"
        print(f"Unique filename: {unique_filename}")
        
        # Save file locally
        file_path = f"uploads/{unique_filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        print(f"File saved locally at: {file_path}")
        print(f"File size: {len(content)} bytes")
        
        # Check Salesforce environment variables
        print(f"=== SALESFORCE ENVIRONMENT CHECK ===")
        print(f"SALESFORCE_INSTANCE_URL: {os.getenv('SALESFORCE_INSTANCE_URL', 'NOT SET')}")
        print(f"SALESFORCE_ACCESS_TOKEN: {'SET' if os.getenv('SALESFORCE_ACCESS_TOKEN') else 'NOT SET'}")
        print(f"SALESFORCE_CLIENT_ID: {'SET' if os.getenv('SALESFORCE_CLIENT_ID') else 'NOT SET'}")
        print(f"SALESFORCE_CLIENT_SECRET: {'SET' if os.getenv('SALESFORCE_CLIENT_SECRET') else 'NOT SET'}")
        print(f"SALESFORCE_USERNAME: {'SET' if os.getenv('SALESFORCE_USERNAME') else 'NOT SET'}")
        print(f"SALESFORCE_PASSWORD: {'SET' if os.getenv('SALESFORCE_PASSWORD') else 'NOT SET'}")
        print(f"SALESFORCE_SECURITY_TOKEN: {'SET' if os.getenv('SALESFORCE_SECURITY_TOKEN') else 'NOT SET'}")
        
        # Integrate with Salesforce API to attach the file
        print(f"=== CALLING SALESFORCE API ===")
        salesforce_result = await salesforce_api.upload_file_to_record(record_id, file_path, file_name)
        print(f"Salesforce result: {salesforce_result}")
        
        return {
            "message": "File uploaded successfully",
            "record_id": record_id,
            "file_name": file_name,
            "salesforce_result": salesforce_result
        }
        
    except Exception as e:
        print(f"=== UPLOAD ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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
