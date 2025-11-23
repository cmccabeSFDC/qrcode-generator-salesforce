import React, { useState } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [data, setData] = useState('');
  const [companyLogoUrl, setCompanyLogoUrl] = useState('');
  const [fileName, setFileName] = useState('');
  const [size, setSize] = useState(10);
  const [border, setBorder] = useState(4);
  const [fillColor, setFillColor] = useState('black');
  const [backColor, setBackColor] = useState('white');
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateQRCode = async () => {
    if (!data) {
      setError('Please enter data for the QR code');
      return;
    }

    setLoading(true);
    setError('');
    setQrCodeUrl('');

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data,
          company_logo_url: companyLogoUrl || null,
          file_name: fileName || null,
          size,
          border,
          fill_color: fillColor,
          back_color: backColor,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setQrCodeUrl(url);
    } catch (err: any) {
      setError(err.message || 'Failed to generate QR code');
      console.error('Error generating QR code:', err);
    } finally {
      setLoading(false);
    }
  };

  const downloadQRCode = () => {
    if (qrCodeUrl) {
      const link = document.createElement('a');
      link.href = qrCodeUrl;
      link.download = `${fileName || 'qr_code'}_qr_code.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>QR Code Generator</h1>
        <p>Generate QR codes with optional company logos</p>
      </header>

      <main className="App-main">
        <div className="form-container">
          <div className="form-group">
            <label htmlFor="data">QR Code Data *</label>
            <input
              id="data"
              type="text"
              value={data}
              onChange={(e) => setData(e.target.value)}
              placeholder="Enter URL or text for QR code"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="companyLogoUrl">Company Logo URL (optional)</label>
            <input
              id="companyLogoUrl"
              type="url"
              value={companyLogoUrl}
              onChange={(e) => setCompanyLogoUrl(e.target.value)}
              placeholder="https://example.com/logo.png"
            />
          </div>

          <div className="form-group">
            <label htmlFor="fileName">File Name (optional)</label>
            <input
              id="fileName"
              type="text"
              value={fileName}
              onChange={(e) => setFileName(e.target.value)}
              placeholder="my_qr_code"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="size">Size</label>
              <input
                id="size"
                type="number"
                value={size}
                onChange={(e) => setSize(parseInt(e.target.value) || 10)}
                min="1"
                max="20"
              />
            </div>

            <div className="form-group">
              <label htmlFor="border">Border</label>
              <input
                id="border"
                type="number"
                value={border}
                onChange={(e) => setBorder(parseInt(e.target.value) || 4)}
                min="1"
                max="10"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="fillColor">Fill Color</label>
              <input
                id="fillColor"
                type="color"
                value={fillColor}
                onChange={(e) => setFillColor(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="backColor">Background Color</label>
              <input
                id="backColor"
                type="color"
                value={backColor}
                onChange={(e) => setBackColor(e.target.value)}
              />
            </div>
          </div>

          <button
            className="generate-button"
            onClick={generateQRCode}
            disabled={loading || !data}
          >
            {loading ? 'Generating...' : 'Generate QR Code'}
          </button>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {qrCodeUrl && (
            <div className="qr-result">
              <h3>Generated QR Code</h3>
              <img src={qrCodeUrl} alt="Generated QR Code" />
              <button className="download-button" onClick={downloadQRCode}>
                Download QR Code
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
