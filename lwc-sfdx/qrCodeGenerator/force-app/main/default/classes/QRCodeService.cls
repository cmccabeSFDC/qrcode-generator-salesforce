public with sharing class QRCodeService {
    public class GenerateRequest {
        @AuraEnabled public String data;
        @AuraEnabled public String company_logo_url;
        @AuraEnabled public String file_name;
        @AuraEnabled public String record_id;
        @AuraEnabled public Integer size;
        @AuraEnabled public Integer border;
        @AuraEnabled public String fill_color;
        @AuraEnabled public String back_color;
    }

    @AuraEnabled(cacheable=false)
    public static String generatePngBase64(String data, String company_logo_url, String file_name, String record_id, Integer size, Integer border, String fill_color, String back_color) {
        try {
            System.debug('=== QRCodeService.generatePngBase64 START ===');
            
            // Create the request object
            GenerateRequest req = new GenerateRequest();
            req.data = data;
            req.company_logo_url = company_logo_url;
            req.file_name = file_name;
            req.record_id = record_id;
            req.size = size;
            req.border = border;
            req.fill_color = fill_color;
            req.back_color = back_color;
            
            System.debug('Request object: ' + JSON.serialize(req));
            
            HttpRequest httpReq = new HttpRequest();
            httpReq.setMethod('POST');
            httpReq.setEndpoint('https://democomponent-qrcode-generator-c48b26ff05fc.herokuapp.com/generate');
            httpReq.setHeader('Content-Type', 'application/json');
            
            String requestBody = JSON.serialize(req);
            System.debug('Request body: ' + requestBody);
            httpReq.setBody(requestBody);
            httpReq.setTimeout(30000); // 30 second timeout

            System.debug('Making HTTP call to Heroku...');
            Http http = new Http();
            HTTPResponse res = http.send(httpReq);

            System.debug('=== HEROKU RESPONSE ===');
            System.debug('Status Code: ' + res.getStatusCode());
            System.debug('Status: ' + res.getStatus());
            System.debug('Response body length: ' + res.getBody().length());
            System.debug('Response headers: ' + res.getHeaderKeys());
            
            if (res.getBody().length() < 1000) {
                System.debug('Response body (first 1000 chars): ' + res.getBody());
            } else {
                System.debug('Response body (first 1000 chars): ' + res.getBody().substring(0, 1000));
            }

            if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
                System.debug('Success! Converting response to base64...');
                // Heroku returns PNG bytes; base64-encode to send to LWC
                Blob pngBlob = res.getBodyAsBlob();
                String base64Result = EncodingUtil.base64Encode(pngBlob);
                System.debug('Base64 result length: ' + base64Result.length());
                System.debug('=== QRCodeService.generatePngBase64 SUCCESS ===');
                return base64Result;
            } else {
                String errorMsg = 'HTTP ' + res.getStatusCode() + ': ' + res.getStatus();
                System.debug('Heroku service error: ' + errorMsg);
                System.debug('Full response body: ' + res.getBody());
                throw new AuraHandledException('QR service error: ' + errorMsg);
            }
        } catch (Exception e) {
            System.debug('=== EXCEPTION IN QRCodeService ===');
            System.debug('Exception type: ' + e.getTypeName());
            System.debug('Exception message: ' + e.getMessage());
            System.debug('Stack trace: ' + e.getStackTraceString());
            throw new AuraHandledException('Error calling QR service: ' + e.getMessage());
        }
    }
}
