# How the Form Reads Session ID from URL

## The Flow

### 1. URL Contains Session Token
```
https://your-app.herokuapp.com/form/00QJ9000003uCB4MAM?
  session_token=00DJ9000001lQog!EXAMPLE_TOKEN_HERE_REPLACED_WITH_PLACEHOLDER
  &instance_url=https://your-instance.my.salesforce.com
```

**Note:** The `!` character is URL-encoded as `%21` in the actual URL, but JavaScript automatically decodes it.

---

### 2. JavaScript Reads from URL (Two Methods)

#### Method A: Immediate Script (Runs First)
```javascript
// This runs IMMEDIATELY when the <script> tag is parsed
// BEFORE the DOM is fully loaded

const urlParams = new URLSearchParams(window.location.search);
const sessionToken = urlParams.get('session_token');
const instanceUrl = urlParams.get('instance_url');

// Logs to console immediately
console.log('IMMEDIATE: session_token from URL:', sessionToken);
```

**What `URLSearchParams` does:**
- Takes `window.location.search` (the part after `?` in the URL)
- Parses it: `?session_token=ABC&instance_url=XYZ`
- Extracts values: `urlParams.get('session_token')` → `"ABC"`

#### Method B: DOMContentLoaded Script (Runs After DOM Ready)
```javascript
// This runs AFTER the HTML is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionToken = urlParams.get('session_token');
    const instanceUrl = urlParams.get('instance_url');
    
    // Sets hidden form fields
    const sessionTokenField = document.getElementById('sessionTokenField');
    if (sessionToken && sessionTokenField) {
        sessionTokenField.value = sessionToken;  // ← KEY STEP
    }
});
```

---

### 3. Hidden Form Field Gets the Value

**HTML (Initial State):**
```html
<input type="hidden" id="sessionTokenField" name="session_token" value="">
```

**After JavaScript Runs:**
```html
<input type="hidden" id="sessionTokenField" name="session_token" value="00DJ9000001lQog!EXAMPLE_TOKEN_HERE_REPLACED_WITH_PLACEHOLDER">
```

**How it works:**
- JavaScript finds the element: `document.getElementById('sessionTokenField')`
- Sets its value: `sessionTokenField.value = sessionToken`
- Now the hidden field contains the session token

---

### 4. Form Submission Includes Hidden Field

When the user clicks "Upload File", the form submits:

```javascript
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Create FormData from the form (automatically includes hidden fields)
    const formData = new FormData(form);
    
    // formData now contains:
    // - file: <selected file>
    // - session_token: "00DJ9000001lQog!..." (from hidden field)
    // - instance_url: "https://..." (from hidden field)
    // - record_id: "00QJ9000003uCB4MAM"
    // - file_name: "screwfix logo"
    
    // Send to backend
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
});
```

**Why this works:**
- `new FormData(form)` automatically collects ALL form fields, including hidden ones
- The hidden field has `name="session_token"`, so it's included in the FormData
- Backend receives it as: `session_token: str = Form("")`

---

## Complete Flow Diagram

```
1. URL: ?session_token=00DJ9000001lQog!...
   ↓
2. JavaScript: urlParams.get('session_token')
   ↓
3. JavaScript: sessionTokenField.value = sessionToken
   ↓
4. Hidden Field: <input name="session_token" value="00DJ9000001lQog!...">
   ↓
5. Form Submit: new FormData(form) includes hidden field
   ↓
6. Backend: session_token: str = Form("") receives "00DJ9000001lQog!..."
   ↓
7. Backend: auth_header = f"Bearer {session_token}"
   ↓
8. Salesforce API: Uses auth_header for API calls
```

---

## Debugging: How to Verify Each Step

### Step 1: Check URL
Open browser console and type:
```javascript
window.location.search
// Should show: "?session_token=00DJ9000001lQog!...&instance_url=..."
```

### Step 2: Check JavaScript Reading
Open browser console and look for:
```
=== IMMEDIATE SCRIPT RUNNING ===
IMMEDIATE: session_token from URL: 00DJ9000001lQog!...
```

### Step 3: Check Hidden Field Value
Open browser console and type:
```javascript
document.getElementById('sessionTokenField').value
// Should show: "00DJ9000001lQog!..."
```

### Step 4: Check FormData Before Submit
In the form submit handler, check:
```javascript
for (let pair of formData.entries()) {
    console.log(pair[0] + ': ' + pair[1]);
}
// Should show: session_token: 00DJ9000001lQog!...
```

### Step 5: Check Backend Receives It
Check Heroku logs:
```
=== FASTAPI FORM PARAMETERS ===
session_token from Form(): '00DJ9000001lQog!...'
```

---

## Common Issues

### Issue 1: JavaScript Not Running
**Symptom:** No console logs, no debug boxes
**Check:**
- Open browser console (F12)
- Look for JavaScript errors
- Check if script tags are in the HTML

### Issue 2: URL Doesn't Have Session Token
**Symptom:** `urlParams.get('session_token')` returns `null`
**Check:**
- Verify QR code URL includes `?session_token=...`
- Check if URL was modified/copied incorrectly
- Verify LWC is including session token in QR code URL

### Issue 3: Hidden Field Not Set
**Symptom:** `sessionTokenField.value` is empty
**Check:**
- Verify JavaScript found the element: `document.getElementById('sessionTokenField')`
- Check if `sessionToken` variable has a value
- Verify DOMContentLoaded fired

### Issue 4: FormData Doesn't Include Hidden Field
**Symptom:** Backend receives empty `session_token`
**Check:**
- Verify hidden field has `name="session_token"` attribute
- Verify `new FormData(form)` is used (not manually creating FormData)
- Check browser network tab to see what's actually sent

---

## Key Code Locations

1. **URL Reading:** `backend/main.py` lines 382-384, 420-422
2. **Setting Hidden Field:** `backend/main.py` lines 470-478
3. **Form Submission:** `backend/main.py` lines 490-550
4. **Backend Receiving:** `backend/main.py` lines 550-551

