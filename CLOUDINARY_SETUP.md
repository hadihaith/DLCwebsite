# Cloudinary Setup Guide - Fix Missing Images on Railway

## 🚨 The Problem

**Symptoms:**
- Images upload successfully on local development ✅
- Images show on local development ✅
- Images upload on Railway ✅
- Images DON'T show on Railway after restart ❌

**Cause:** Railway uses ephemeral file system - uploaded files are deleted on restart/redeploy!

**Solution:** Use Cloudinary for cloud file storage ☁️

---

## ✅ What I Already Did

I've configured your Django app to:
- ✅ Use **local media folder** in development (DEBUG=True)
- ✅ Use **Cloudinary** in production (DEBUG=False)
- ✅ Added cloudinary packages to requirements.txt
- ✅ Added Cloudinary to INSTALLED_APPS
- ✅ Configured settings.py to use Cloudinary when deployed

---

## 🎯 What YOU Need To Do (5 minutes)

### Step 1: Create Cloudinary Account

1. Go to: **https://cloudinary.com/users/register/free**
2. Sign up with email (NO credit card needed for free tier)
3. Verify your email
4. Login to dashboard

### Step 2: Get Your Credentials

On the Cloudinary dashboard homepage, you'll see:

```
Cloud name: your_cloud_name
API Key: 123456789012345
API Secret: abcdefghijklmnopqrstuvwxyz
```

**Copy these three values!**

### Step 3: Add Variables to Railway

1. Go to **Railway Dashboard**
2. Click your **Django app service**
3. Go to **Variables** tab
4. Click **+ New Variable** (do this 3 times):

**Variable 1:**
- Name: `CLOUDINARY_CLOUD_NAME`
- Value: `your_cloud_name` (from Cloudinary dashboard)

**Variable 2:**
- Name: `CLOUDINARY_API_KEY`
- Value: `123456789012345` (from Cloudinary dashboard)

**Variable 3:**
- Name: `CLOUDINARY_API_SECRET`
- Value: `abcdefghijklmnopqrstuvwxyz` (from Cloudinary dashboard)

### Step 4: Push Code & Deploy

```bash
git add .
git commit -m "Add Cloudinary for file storage"
git push
```

Railway will automatically redeploy!

### Step 5: Test It! 🎉

1. **Upload a new image** on Railway (after deployment completes)
2. **Trigger a redeploy** in Railway (or just wait)
3. **Check if image still shows** ✅

---

## 🔍 How To Verify It's Working

### Check 1: Railway Logs

After deploying, check logs for:
```
Successfully installed cloudinary-1.36.0
Successfully installed django-cloudinary-storage-0.3.0
```

### Check 2: Upload Test

1. Login to your Railway site
2. Upload an event image or partner university logo
3. Refresh page - image should show
4. Trigger Railway redeploy
5. Image should STILL show! ✅

### Check 3: Cloudinary Dashboard

1. Go to **Cloudinary Console**
2. Click **Media Library**
3. You should see your uploaded files there!

---

## 📊 What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **Local dev** | media/ folder | media/ folder (unchanged) ✅ |
| **Production** | Railway container (deleted on restart) ❌ | Cloudinary (permanent) ✅ |
| **Image URLs** | /media/events/image.jpg | cloudinary.com/your_cloud/image/upload/... |
| **Persistence** | Lost on redeploy ❌ | Permanent ✅ |

---

## 🎨 File Types Supported

Cloudinary handles all your upload types:
- ✅ Partner University logos (ImageField)
- ✅ Event images (ImageField)
- ✅ Exchange application PDFs (FileField)
- ✅ English proficiency documents (FileField)
- ✅ Transcripts (FileField)
- ✅ Passport copies (FileField)

**All will now be stored permanently in Cloudinary!**

---

## 💰 Free Tier Limits

Cloudinary Free Plan includes:
- **25 GB** storage
- **25 GB** bandwidth per month
- **Unlimited** transformations
- **No credit card** required

For your use case (DLC applications, events, logos):
- 1,000 images × 2MB average = **2GB** (well within limit!)
- Plenty of room to grow

---

## 🔒 Security

### What's Already Configured:

- ✅ Files upload to Cloudinary (not Railway container)
- ✅ Django generates secure URLs
- ✅ Cloudinary credentials stored in environment variables (not in code)
- ✅ .env in .gitignore (credentials never committed)

### File Privacy:

By default, files are **publicly accessible** via URL (needed to display images).

If you need **private files** (e.g., student documents):
```python
# In models.py - for sensitive documents
from cloudinary.models import CloudinaryField

class ExchangeApplication(models.Model):
    passport_copy = CloudinaryField(
        'passport',
        type='private',  # Makes file private
        resource_type='raw'  # For PDFs
    )
```

---

## 🔄 Migrating Existing Files (Optional)

If you have files already uploaded to Railway that you want to keep:

### Option 1: Re-upload Manually
1. Download files from Railway before they disappear
2. Re-upload through Django admin after Cloudinary is configured

### Option 2: Bulk Migration Script
```python
# Run this in Django shell after Cloudinary is configured
python manage.py shell

from main.models import Event, PartnerUniversity

# Re-save all objects to trigger Cloudinary upload
for event in Event.objects.filter(image__isnull=False):
    event.save()

for uni in PartnerUniversity.objects.filter(logo__isnull=False):
    uni.save()
```

---

## 🐛 Troubleshooting

### Issue: "cloudinary.exceptions.Error: Must supply cloud_name"

**Solution:** Make sure you added the 3 environment variables in Railway:
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET

### Issue: Images still not showing after setup

**Checklist:**
- [ ] Railway variables added?
- [ ] Code pushed to GitHub?
- [ ] Railway redeployed?
- [ ] Uploaded NEW image after deployment?
- [ ] Checked Cloudinary dashboard for files?

### Issue: "Invalid API credentials"

**Solution:** Double-check you copied the correct values from Cloudinary dashboard.

### Issue: Local development broken

**This shouldn't happen!** Local uses media/ folder (DEBUG=True).

If it does:
1. Make sure DEBUG=True locally
2. Check .env file doesn't have Cloudinary variables (for local)

---

## 📝 Configuration Summary

### settings.py Changes:

```python
INSTALLED_APPS = [
    # ... other apps
    'cloudinary_storage',  # Added
    'cloudinary',          # Added
]

# Only in production (DEBUG=False)
if not DEBUG:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### requirements.txt Changes:

```
cloudinary==1.36.0
django-cloudinary-storage==0.3.0
```

---

## 🎯 Quick Checklist

Setup steps:
- [ ] Create Cloudinary account
- [ ] Get Cloud name, API Key, API Secret
- [ ] Add 3 variables to Railway
- [ ] Push code to GitHub
- [ ] Wait for Railway deployment
- [ ] Test upload
- [ ] Verify image persists after redeploy

---

## 📞 Support

- **Cloudinary Docs**: https://cloudinary.com/documentation/django_integration
- **Free Plan**: https://cloudinary.com/pricing
- **Media Library**: https://console.cloudinary.com/console/media_library

---

## ✅ Final Check

After setup is complete:

1. Upload an event image on Railway
2. Note the image URL (should contain "cloudinary.com")
3. Trigger a Railway redeploy
4. Image should still show! ✅

**If it shows after redeploy, you're done!** 🎉

---

**Setup Time:** ~5 minutes  
**Difficulty:** Easy  
**Cost:** Free  
**Result:** Images persist forever! ✅

---

**Last Updated:** October 25, 2025  
**Status:** Ready to deploy
