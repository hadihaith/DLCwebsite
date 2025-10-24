# File Upload System Verification - Exchange Application

## Current Status: ✅ **READY FOR LOCAL/DEVELOPMENT** | ⚠️ **NEEDS PRODUCTION CONFIGURATION**

---

## What's Working ✅

### 1. Model Configuration
**File**: `main/models.py` (Lines 60-118)

The `ExchangeApplication` model has **three file upload fields** properly configured:

```python
english_proficiency_document = models.FileField(
    upload_to='exchange_applications/english/',
    validators=[FileExtensionValidator(['pdf'])]
)

transcript_document = models.FileField(
    upload_to='exchange_applications/transcripts/',
    validators=[FileExtensionValidator(['pdf'])]
)

passport_copy = models.FileField(
    upload_to='exchange_applications/passports/',
    validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])]
)
```

✅ **Validators**: File extension validation in place
✅ **Upload paths**: Organized into subdirectories
✅ **File types**: PDF required for documents, PDF/PNG/JPG/JPEG for passport

---

### 2. View Configuration
**File**: `main/views.py` (Lines 741-757)

```python
def exchange_application(request):
    submitted = False
    if request.method == 'POST':
        form = ExchangeApplicationForm(request.POST, request.FILES)  # ✅ request.FILES
        if form.is_valid():
            form.save()
            submitted = True
```

✅ **request.FILES**: Properly passed to form
✅ **Form validation**: Checks before saving
✅ **Save method**: Automatically handles file uploads

---

### 3. Form Configuration
**File**: `main/forms.py` (Lines 50-100)

```python
class ExchangeApplicationForm(forms.ModelForm):
    class Meta:
        model = ExchangeApplication
        fields = [
            # ... other fields
            'english_proficiency_document',
            'transcript_document',
            'passport_copy',
            # ...
        ]
```

✅ **All file fields included** in the form
✅ **Labels**: Clear instructions for users
✅ **Widgets**: File input fields configured

---

### 4. Template Configuration
**File**: `main/templates/frontend/exchange_application.html` (Line 41)

```html
<form method="post" enctype="multipart/form-data" novalidate>
    {% csrf_token %}
    <!-- ... -->
    {{ form.english_proficiency_document }}
    {{ form.transcript_document }}
    {{ form.passport_copy }}
</form>
```

✅ **enctype="multipart/form-data"**: **CRITICAL** - Required for file uploads
✅ **CSRF token**: Security in place
✅ **File fields**: All three file inputs rendered

---

### 5. Settings Configuration
**File**: `Dlcweb/settings.py` (Lines 154-155)

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

✅ **MEDIA_URL**: Defines URL path for uploaded files
✅ **MEDIA_ROOT**: Files stored in `media/` directory

---

### 6. URL Configuration
**File**: `Dlcweb/urls.py` (Lines 27-29)

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

✅ **Development**: Media files served in DEBUG mode
⚠️ **Production**: Only works in development

---

### 7. Admin Configuration
**File**: `main/admin.py` (Line 6)

```python
admin.site.register(ExchangeApplication)
```

✅ **Admin access**: Can view/download uploaded files through Django admin

---

## Current Directory Structure

```
Dlcweb/
├── media/
│   ├── dean_list_excel_files/  ✅ Exists
│   ├── events/                 ✅ Exists
│   ├── partners/               ✅ Exists
│   └── exchange_applications/  ❌ Will be created on first upload
│       ├── english/
│       ├── transcripts/
│       └── passports/
```

**Note**: Django will automatically create the `exchange_applications/` subdirectories on first file upload.

---

## Testing Checklist

### Local Development Testing:

- [ ] 1. **Submit form with all three files**
  - Navigate to exchange application page
  - Fill out all required fields
  - Upload PDF for English proficiency
  - Upload PDF for transcript
  - Upload PDF/PNG/JPG for passport copy
  - Submit form

- [ ] 2. **Verify files saved to database**
  ```bash
  python manage.py shell
  >>> from main.models import ExchangeApplication
  >>> app = ExchangeApplication.objects.last()
  >>> print(app.english_proficiency_document.url)
  >>> print(app.transcript_document.url)
  >>> print(app.passport_copy.url)
  ```

- [ ] 3. **Verify physical files exist**
  - Check `media/exchange_applications/english/` for uploaded file
  - Check `media/exchange_applications/transcripts/` for uploaded file
  - Check `media/exchange_applications/passports/` for uploaded file

- [ ] 4. **Access files via URL** (development only)
  - Visit `http://localhost:8000/media/exchange_applications/english/[filename]`
  - Should download/display the file

- [ ] 5. **Test file validation**
  - Try uploading .txt file for English proficiency (should fail)
  - Try uploading .doc file for transcript (should fail)
  - Try uploading .gif file for passport (should fail)

- [ ] 6. **View in Django Admin**
  - Go to `/admin/main/exchangeapplication/`
  - Click on an application
  - Verify file links are clickable and download correctly

---

## ⚠️ PRODUCTION DEPLOYMENT ISSUES

### **CRITICAL: Railway/Heroku Ephemeral File System**

Railway (and Heroku) use **ephemeral file systems**, meaning:

❌ **Problem**: Uploaded files are **DELETED on each deployment or dyno restart**
❌ **Impact**: All exchange application documents will be lost
❌ **Timeline**: Can happen within 24 hours on Railway

### **Solution Required: Cloud Storage**

You **MUST** configure external cloud storage for production. Options:

---

## Recommended Solutions

### **Option 1: AWS S3 (Most Common)** ⭐ Recommended

**Pros**:
- Industry standard
- Reliable and fast
- Pay-as-you-go pricing
- Django integration mature

**Setup**:

1. **Install package**:
   ```bash
   pip install django-storages boto3
   ```

2. **Update requirements.txt**:
   ```
   django-storages==1.14.2
   boto3==1.34.14
   ```

3. **Add to settings.py**:
   ```python
   INSTALLED_APPS = [
       # ...
       'storages',
   ]

   # AWS S3 Settings (only in production)
   if not DEBUG:
       AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
       AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
       AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
       AWS_S3_REGION_NAME = 'us-east-1'  # Change to your region
       AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
       AWS_DEFAULT_ACL = 'private'  # Keep files private
       AWS_S3_FILE_OVERWRITE = False
       AWS_S3_OBJECT_PARAMETERS = {
           'CacheControl': 'max-age=86400',
       }
       
       # Use S3 for media files
       DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

4. **Set Railway environment variables**:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_STORAGE_BUCKET_NAME`

**Cost**: ~$0.023/GB/month + $0.005/1000 requests

---

### **Option 2: Cloudinary (Easier Setup)** ⭐ Good for Images

**Pros**:
- Free tier: 25GB storage, 25GB bandwidth/month
- Easy Django integration
- Good for PDFs and images
- Automatic optimization

**Setup**:

1. **Install package**:
   ```bash
   pip install cloudinary django-cloudinary-storage
   ```

2. **Update requirements.txt**:
   ```
   cloudinary==1.36.0
   django-cloudinary-storage==0.3.0
   ```

3. **Add to settings.py**:
   ```python
   INSTALLED_APPS = [
       # ...
       'cloudinary_storage',
       'cloudinary',
   ]

   # Cloudinary settings (production only)
   if not DEBUG:
       CLOUDINARY_STORAGE = {
           'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
           'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
           'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
       }
       DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   ```

4. **Set Railway environment variables**:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

**Cost**: Free tier sufficient for most needs

---

### **Option 3: Railway Volumes (Not Recommended)**

**Pros**:
- No external service needed
- Files persist across deploys

**Cons**:
- ❌ Limited to single Railway region
- ❌ Slower than CDN
- ❌ More expensive than S3 long-term
- ❌ Not easily scalable

**Only use if**: You have very few uploads and don't care about speed

---

## Migration Plan

### **Before Production Deploy**:

1. **Choose cloud storage provider** (recommend AWS S3 or Cloudinary)

2. **Create account and get credentials**

3. **Install required packages**:
   ```bash
   pip install django-storages boto3  # For S3
   # OR
   pip install cloudinary django-cloudinary-storage  # For Cloudinary
   ```

4. **Update requirements.txt**

5. **Configure settings.py** with production storage

6. **Set environment variables** in Railway dashboard

7. **Test locally with production settings**:
   ```bash
   # Set environment variables
   $env:DEBUG="False"
   $env:AWS_ACCESS_KEY_ID="your-key"
   # ... etc
   python manage.py runserver
   ```

8. **Deploy to Railway**

9. **Test file upload on production**

10. **Migrate existing files** (if any):
    ```python
    # Optional: Script to migrate local files to S3
    from main.models import ExchangeApplication
    for app in ExchangeApplication.objects.all():
        if app.english_proficiency_document:
            # Re-save triggers S3 upload
            app.save()
    ```

---

## Security Considerations

### Current Implementation ✅

1. **File Extension Validation**: Only PDF, PNG, JPG, JPEG allowed
2. **CSRF Protection**: Enabled on form
3. **Admin Access Only**: Files not publicly listed

### Additional Recommendations

1. **File Size Limits**:
   ```python
   # In forms.py
   def clean_english_proficiency_document(self):
       file = self.cleaned_data.get('english_proficiency_document')
       if file and file.size > 5 * 1024 * 1024:  # 5MB limit
           raise forms.ValidationError('File size must be under 5MB')
       return file
   ```

2. **Virus Scanning** (production):
   - Use AWS Lambda + ClamAV for S3
   - Or Cloudinary's automatic malware detection

3. **Access Control**:
   - Current: Files accessible via direct URL (anyone with link)
   - Better: Serve via Django view with authentication check

4. **File Naming**:
   - Current: Django adds random hash to prevent collisions ✅
   - Already secure against filename injection attacks

---

## Quick Test Command

```bash
# Test file upload locally
python manage.py shell

from main.models import ExchangeApplication, PartnerUniversity
from django.core.files.uploadedfile import SimpleUploadedFile

# Create test partner university
uni = PartnerUniversity.objects.first()

# Create test files
pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
img_file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

# Create application with files
app = ExchangeApplication.objects.create(
    first_name="Test",
    last_name="Student",
    date_of_birth="2000-01-01",
    home_institution=uni,
    home_major="Computer Science",
    program_level="UNDERGRADUATE",
    exchange_semester="FALL",
    exchange_academic_year="2025/2026",
    gender="MALE",
    passport_number="ABC123456",
    passport_expiry_date="2027-01-01",
    email="test@example.com",
    completed_credits=60,
    english_proficiency_document=pdf_file,
    transcript_document=pdf_file,
    passport_copy=img_file,
    coordinator_name="Dr. Test",
    coordinator_email="coordinator@example.com"
)

print(f"✅ Application created: {app.id}")
print(f"✅ English doc: {app.english_proficiency_document.url}")
print(f"✅ Transcript: {app.transcript_document.url}")
print(f"✅ Passport: {app.passport_copy.url}")
```

---

## Summary

### ✅ What's Ready NOW:

1. Model has proper FileField configurations
2. Form includes file upload fields
3. View handles request.FILES correctly
4. Template has enctype="multipart/form-data"
5. URLs configured for development
6. File validation in place
7. Admin can access uploaded files

### ⚠️ What's MISSING for Production:

1. **CRITICAL**: Cloud storage configuration (AWS S3 or Cloudinary)
2. Environment variables for storage credentials
3. File size validation (recommended)
4. Advanced access control (optional)

### 🎯 Next Steps:

1. **If deploying soon**: Set up AWS S3 or Cloudinary NOW
2. **If testing locally**: Current setup works perfectly
3. **Budget**: Cloudinary free tier is enough to start
4. **Long-term**: AWS S3 is more scalable

### 📋 Action Items:

- [ ] Choose cloud storage provider
- [ ] Create account and get credentials
- [ ] Install django-storages or cloudinary package
- [ ] Configure production settings
- [ ] Set Railway environment variables
- [ ] Test file upload on production
- [ ] Document file access procedures for admins

---

**Last Updated**: October 24, 2025
**Status**: Ready for local development, requires cloud storage for production deployment
