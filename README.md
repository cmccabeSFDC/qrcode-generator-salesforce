# QR Code Generator with Salesforce Integration

A comprehensive solution for generating QR codes that link to file upload forms, with full Salesforce integration for automatic file attachment to records.

## 🚀 Features

- **QR Code Generation**: Generate QR codes that link to file upload forms
- **Company Logo Integration**: Add company logos to QR codes and upload forms
- **File Upload Forms**: Centered, branded forms for file collection
- **Salesforce Integration**: Automatic file attachment to Salesforce records
- **Lightning Web Component**: Salesforce LWC for seamless integration
- **Heroku Deployment**: Ready for cloud deployment with one-click setup
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Record Context**: Automatically captures Salesforce record IDs

## 📁 Project Structure

```
qr-code-generator/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application file
│   ├── requirements.txt     # Python dependencies
│   ├── Procfile            # Heroku deployment config
│   └── runtime.txt         # Python version
├── frontend/               # React frontend
│   └── src/                # React source code
├── lwc-sfdx/              # Salesforce Lightning Web Component
│   └── qrCodeGenerator/   # LWC component files
└── README.md              # This file
```

## 🛠️ Setup Instructions

### Backend Setup (FastAPI)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally:**
   ```bash
   python3 main.py
   ```
   - Backend will run on `http://localhost:8001`

### Frontend Setup (React)

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run locally:**
   ```bash
   npm start
   ```
   - Frontend will run on `http://localhost:3001`

### Lightning Web Component Setup

1. **Navigate to LWC directory:**
   ```bash
   cd lwc-sfdx/qrCodeGenerator
   ```

2. **Deploy to Salesforce:**
   ```bash
   sfdx force:source:deploy -p force-app/main/default/lwc/qrCodeGenerator
   ```

3. **Update Heroku endpoint in LWC:**
   - Edit `qrCodeGenerator.js`
   - Replace `https://your-qr-generator-app.herokuapp.com` with your actual Heroku URL

## 🚀 Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Git repository

### Deployment Steps

1. **Login to Heroku:**
   ```bash
   heroku login
   ```

2. **Create Heroku app:**
   ```bash
   cd backend
   heroku create your-qr-generator-app
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

4. **Update LWC endpoint:**
   - Replace the Heroku endpoint URL in the LWC component

## 📋 API Endpoints

### Backend API (Port 8001)

- `GET /` - Health check
- `GET /health` - Health status
- `POST /generate` - Generate QR code with logo
- `GET /generate/{data}` - Simple QR code generation

### Request Format

```json
{
  "data": "Your QR code data",
  "size": 10,
  "border": 4,
  "fill_color": "black",
  "back_color": "white",
  "company_logo_url": "https://example.com/logo.png",
  "file_name": "my_qr_code"
}
```

## 🎯 Lightning Web Component Features

### Input Fields
- **Company Logo URL**: Optional URL for company logo
- **File Name**: Required name for the generated QR code

### Functionality
- **Generate QR Code**: Creates QR code with optional logo
- **Download**: Download the generated QR code
- **Clear Form**: Reset all inputs
- **Error Handling**: Comprehensive error messages
- **Loading States**: Visual feedback during generation

### Deployment Targets
- Lightning App Pages
- Record Pages (Account, Contact, Lead, Opportunity)
- Home Pages
- Community Pages

## 🔧 Configuration

### Environment Variables
- `ENVIRONMENT`: Development/Production mode
- `SECRET_KEY`: Application secret key

### CORS Configuration
- Frontend: `http://localhost:3001`
- Salesforce: Configured for Lightning platform

## 📱 Usage

### In Salesforce
1. Add the LWC to any Lightning page
2. Enter company logo URL (optional)
3. Enter file name (required)
4. Click "Generate QR Code"
5. Download the generated QR code

### Direct API Usage
```bash
curl -X POST "https://your-app.herokuapp.com/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "https://example.com",
    "company_logo_url": "https://example.com/logo.png",
    "file_name": "company_qr"
  }'
```

## 🛡️ Security Features

- CORS protection
- Input validation
- Error handling
- Timeout protection for logo downloads

## 📊 Performance

- Optimized image processing
- Efficient QR code generation
- Responsive design
- Fast API responses

## 🔄 Development

### Local Development
1. Start backend: `python3 main.py`
2. Start frontend: `npm start`
3. Test LWC in Salesforce org

### Testing
- Backend: `http://localhost:8001/docs` (Swagger UI)
- Frontend: `http://localhost:3001`
- LWC: Deploy to Salesforce org

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review error messages in the LWC
3. Verify Heroku deployment status
4. Check Salesforce deployment logs

## 🎉 Success!

Your QR Code Generator is now ready for use with:
- ✅ FastAPI backend with logo integration
- ✅ React frontend (optional)
- ✅ Lightning Web Component for Salesforce
- ✅ Heroku deployment configuration
- ✅ Comprehensive error handling
- ✅ Download functionality
