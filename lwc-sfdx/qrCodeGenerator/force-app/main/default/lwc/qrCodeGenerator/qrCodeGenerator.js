import { LightningElement, track, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class QrCodeGenerator extends LightningElement {
    @track companyLogoUrl = '';
    @track fileName = '';
    @track recordId = '';
    @track isLoading = false;
    @track errorMessage = '';
    @track successMessage = '';
    @track qrCodeImageUrl = '';
    @track showQRCode = false;

    // Heroku microservice endpoint - replace with your actual Heroku app URL
    herokuEndpoint = 'https://your-qr-generator-app.herokuapp.com';

    // Get current record ID from page context
    connectedCallback() {
        // This will be populated by the page context or passed as a parameter
        // For now, we'll use a placeholder
        this.recordId = this.getRecordId() || '001000000000000';
    }

    getRecordId() {
        // This method should be implemented to get the current record ID
        // from the Lightning page context
        return null; // Placeholder
    }

    get isButtonDisabled() {
        return this.isLoading || !this.fileName || !this.recordId;
    }

    handleLogoUrlChange(event) {
        this.companyLogoUrl = event.target.value;
        this.clearMessages();
    }

    handleFileNameChange(event) {
        this.fileName = event.target.value;
        this.clearMessages();
    }

    handleRecordIdChange(event) {
        this.recordId = event.target.value;
        this.clearMessages();
    }

    clearMessages() {
        this.errorMessage = '';
        this.successMessage = '';
    }

    clearForm() {
        this.companyLogoUrl = '';
        this.fileName = '';
        this.qrCodeImageUrl = '';
        this.showQRCode = false;
        this.clearMessages();
    }

    async generateQRCode() {
        if (!this.fileName) {
            this.errorMessage = 'Please enter a file name.';
            return;
        }

        if (!this.recordId) {
            this.errorMessage = 'Record ID is required.';
            return;
        }

        this.isLoading = true;
        this.clearMessages();

        try {
            // Create the form URL that the QR code will point to
            const formUrl = `${this.herokuEndpoint}/form/${this.recordId}?company_logo_url=${encodeURIComponent(this.companyLogoUrl)}&file_name=${encodeURIComponent(this.fileName)}`;
            
            // Prepare the data for the QR code
            const qrData = {
                data: formUrl,
                company_logo_url: this.companyLogoUrl,
                file_name: this.fileName,
                record_id: this.recordId,
                size: 10,
                border: 4,
                fill_color: 'black',
                back_color: 'white'
            };

            // Call the Heroku microservice
            const response = await this.callHerokuService(qrData);
            
            if (response.ok) {
                // Convert the response to a blob URL for display
                const blob = await response.blob();
                this.qrCodeImageUrl = URL.createObjectURL(blob);
                this.showQRCode = true;
                this.successMessage = 'QR Code generated successfully! This QR code will open a file upload form.';
                
                this.showToast('Success', 'QR Code generated successfully!', 'success');
            } else {
                const errorData = await response.json();
                this.errorMessage = errorData.detail || 'Failed to generate QR code.';
                this.showToast('Error', this.errorMessage, 'error');
            }
        } catch (error) {
            console.error('Error generating QR code:', error);
            this.errorMessage = 'An error occurred while generating the QR code. Please try again.';
            this.showToast('Error', this.errorMessage, 'error');
        } finally {
            this.isLoading = false;
        }
    }

    async callHerokuService(data) {
        const requestBody = {
            data: JSON.stringify(data),
            size: 10,
            border: 4,
            fill_color: 'black',
            back_color: 'white'
        };

        return fetch(`${this.herokuEndpoint}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
    }

    downloadQRCode() {
        if (this.qrCodeImageUrl) {
            // Create a temporary link element to trigger download
            const link = document.createElement('a');
            link.href = this.qrCodeImageUrl;
            link.download = `${this.fileName}_qr_code.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showToast('Success', 'QR Code downloaded successfully!', 'success');
        }
    }

    showToast(title, message, variant) {
        const event = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(event);
    }

    // Clean up object URLs when component is destroyed
    disconnectedCallback() {
        if (this.qrCodeImageUrl) {
            URL.revokeObjectURL(this.qrCodeImageUrl);
        }
    }
}