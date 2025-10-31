import { LightningElement, track, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import generatePngBase64 from '@salesforce/apex/QRCodeService.generatePngBase64';

export default class QrCodeGenerator extends LightningElement {
    @api companyLogoUrl = '';
    @api fileName = '';
    @api recordId = '';
    @track isLoading = false;
    @track errorMessage = '';
    @track successMessage = '';
    @track qrCodeImageUrl = '';
    @track showQRCode = false;
    @track formUrl = '';

    // Heroku microservice endpoint - replace with your actual Heroku app URL
    herokuEndpoint = 'https://democomponent-qrcode-generator-c48b26ff05fc.herokuapp.com';

    // Record ID is automatically populated from the page context via @api recordId
    connectedCallback() {
        // The recordId will be automatically populated by Salesforce
        // when the component is placed on a record page
        console.log('Record ID automatically populated:', this.recordId);
        // Force refresh to ensure changes are applied
    }

    get isButtonDisabled() {
        return this.isLoading || !this.fileName || !this.recordId;
    }

    get displayCompanyLogo() {
        return this.companyLogoUrl || 'Not configured';
    }

    get displayFileName() {
        return this.fileName || 'Not configured';
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
        console.log('generate QR code button fired');
        
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
            console.log('Input values:', {
                companyLogoUrl: this.companyLogoUrl,
                fileName: this.fileName,
                recordId: this.recordId
            });
            
            // Create the form URL that the QR code will point to
            this.formUrl = `${this.herokuEndpoint}/form/${this.recordId}?company_logo_url=${encodeURIComponent(this.companyLogoUrl)}&file_name=${encodeURIComponent(this.fileName)}`;
            console.log('Form URL created:', this.formUrl);
            
            // Prepare the data for the QR code
            const qrData = {
                data: this.formUrl,
                company_logo_url: this.companyLogoUrl,
                file_name: this.fileName,
                record_id: this.recordId,
                size: 10,
                border: 4,
                fill_color: 'black',
                back_color: 'white'
            };
            
            // Print out each parameter that will be sent to Heroku
            console.log('=== PARAMETERS FOR HEROKU APPLICATION ===');
            console.log('data (form URL):', qrData.data);
            console.log('company_logo_url:', qrData.company_logo_url);
            console.log('file_name:', qrData.file_name);
            console.log('record_id:', qrData.record_id);
            console.log('size:', qrData.size);
            console.log('border:', qrData.border);
            console.log('fill_color:', qrData.fill_color);
            console.log('back_color:', qrData.back_color);
            console.log('=== END PARAMETERS ===');
            
            console.log('QR Data prepared:', qrData);

            // Call server-side Apex (uses Named Credential) to avoid CSP/CORS
            console.log('Calling Apex QRCodeService.generatePngBase64...');
            const base64Png = await generatePngBase64({
                data: qrData.data,
                company_logo_url: qrData.company_logo_url,
                file_name: qrData.file_name,
                record_id: qrData.record_id,
                size: qrData.size,
                border: qrData.border,
                fill_color: qrData.fill_color,
                back_color: qrData.back_color
            });

            const blob = this.base64ToBlob(base64Png, 'image/png');
            this.qrCodeImageUrl = URL.createObjectURL(blob);
            this.showQRCode = true;
            this.successMessage = 'QR Code generated successfully! This QR code will open a file upload form.';
            this.showToast('Success', 'QR Code generated successfully!', 'success');
        } catch (error) {
            console.error('Error generating QR code:', error);
            this.errorMessage = 'An error occurred while generating the QR code. Please try again.';
            this.showToast('Error', this.errorMessage, 'error');
        } finally {
            this.isLoading = false;
        }
    }

    // Convert base64 string to Blob for image rendering
    base64ToBlob(base64, mimeType) {
        const binaryString = atob(base64);
        const byteNumbers = new Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            byteNumbers[i] = binaryString.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: mimeType });
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

    linkToForm() {
        // Open the form URL in a new window
        if (this.formUrl) {
            window.open(this.formUrl, '_blank');
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