# Railway Deployment Checklist - Troubleshooting Guide

## 🎯 Complete Setup Checklist

### Part 1: PostgreSQL Database Setup

#### Step 1: Create PostgreSQL Service

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click your project** (DLCwebsite)
3. **Look for services**:
   - [ ] Do you see TWO boxes? (Django app + PostgreSQL)
   - [ ] Or just ONE box? (Django app only)

**If you see only ONE box (Django app):**

1. Click **+ New** (top right corner)
2. Select **Database**
3. Choose **PostgreSQL**
4. Wait for it to provision (~30 seconds)
5. You should now see TWO services

#### Step 2: Connect PostgreSQL to Django App

1. **Click on your Django app service** (the one running your code)
2. **Go to Variables tab**
3. **Check if DATABASE_URL exists:**

   **If DATABASE_URL EXISTS:**
   - ✅ Skip to Part 2 (Cloudinary)

   **If DATABASE_URL MISSING:**
   1. Click **+ New Variable**
   2. Choose **Add Reference**
   3. Select **PostgreSQL service**
   4. Select **DATABASE_URL** variable
   5. Click **Add**
   
   OR manually add:
   - Name: `DATABASE_URL`
   - Value: `${{Postgres.DATABASE_URL}}` (reference syntax)
   
   OR use direct connection string:
   - Name: `DATABASE_URL`
   - Value: `postgresql://postgres:FSuRXlLFYDHyDasukNBHAewjrGQztyMX@postgres.railway.internal:5432/railway`

#### Step 3: Verify Database Connection

After adding DATABASE_URL:

1. **Railway will auto-redeploy**
2. **Check deployment logs**:
   - Click **Deployments** tab
   - Click latest deployment
   - Look for:
     ```
     Running migrations...
     Operations to perform:
       Apply all migrations: admin, auth, contenttypes, main, sessions
     Running migrations:
       No migrations to apply. ✅
     ```

3. **If you see database errors:**
   - Check the exact error message
   - Common issues below

---

### Part 2: Cloudinary File Storage Setup

#### Step 1: Create Cloudinary Account

1. Go to: https://cloudinary.com/users/register/free
2. Sign up with email
3. Verify email
4. Login to dashboard

#### Step 2: Get Credentials

On Cloudinary dashboard homepage, you'll see a box with:

```
Cloud name: [your_cloud_name]
API Key: [123456789012345]
API Secret: [abcdefghijklmnopqrstuvwxyz-ABC]
```

**Copy these THREE values!**

#### Step 3: Add to Railway

1. **Go to Railway Dashboard**
2. **Click your Django app service**
3. **Go to Variables tab**
4. **Add THREE new variables** (click + New Variable for each):

   **Variable 1:**
   - Name: `CLOUDINARY_CLOUD_NAME`
   - Value: [paste your cloud name]

   **Variable 2:**
   - Name: `CLOUDINARY_API_KEY`
   - Value: [paste your API key]

   **Variable 3:**
   - Name: `CLOUDINARY_API_SECRET`
   - Value: [paste your API secret]

5. **Save each variable**

#### Step 4: Trigger Redeploy

After adding variables:
1. Railway should auto-redeploy
2. OR click **Deploy** → **Redeploy**
3. Wait for deployment to complete (~2-3 minutes)

#### Step 5: Test File Upload

1. **Go to your Railway site**
2. **Login to portal/admin**
3. **Upload a NEW image** (event, partner university logo)
4. **Check if it shows** ✅
5. **Go to Cloudinary dashboard** → Media Library
6. **Your uploaded file should appear there** ✅

---

### Part 3: Verify Everything Works

#### Test 1: Database Persistence

1. **Create a test record** (user, application, etc.)
2. **Trigger Railway redeploy**:
   - Dashboard → Deployments → Three dots → Redeploy
3. **Check if record still exists** ✅

**If record disappears:** DATABASE_URL not configured correctly

#### Test 2: File Persistence

1. **Upload a test image**
2. **Note the image URL** (should contain "cloudinary.com")
3. **Trigger Railway redeploy**
4. **Image should still show** ✅

**If image disappears:** Cloudinary not configured correctly

#### Test 3: Check Logs

1. **Railway Dashboard → Deployments**
2. **Click latest deployment**
3. **Check logs for:**
   ```
   ✅ Successfully installed cloudinary-1.36.0
   ✅ Successfully installed django-cloudinary-storage-0.3.0
   ✅ Running migrations... No migrations to apply.
   ✅ Collecting static files... 6 static files copied
   ```

---

## 🐛 Common Issues & Solutions

### Issue 1: "No module named 'cloudinary'"

**Cause:** requirements.txt not updated or Railway didn't install packages

**Solution:**
1. Check requirements.txt has:
   ```
   cloudinary==1.36.0
   django-cloudinary-storage==0.3.0
   ```
2. Push to GitHub
3. Railway will redeploy and install packages

### Issue 2: "cloudinary.exceptions.Error: Must supply cloud_name"

**Cause:** Cloudinary variables not set in Railway

**Solution:**
1. Go to Railway → Variables
2. Make sure you have ALL THREE:
   - CLOUDINARY_CLOUD_NAME
   - CLOUDINARY_API_KEY
   - CLOUDINARY_API_SECRET
3. Values must match your Cloudinary dashboard exactly

### Issue 3: Images still disappearing

**Possible causes:**

**A) Using old images (uploaded before Cloudinary setup)**
- **Solution:** Upload NEW images after Cloudinary is configured

**B) Still in DEBUG mode**
- **Check:** Railway → Variables → Is DEBUG=True?
- **Solution:** Remove DEBUG variable from Railway (defaults to False)

**C) Cloudinary credentials wrong**
- **Solution:** Double-check values from Cloudinary dashboard

### Issue 4: "relation 'main_user' does not exist"

**Cause:** Migrations not run on PostgreSQL

**Solution:**
```bash
# In Railway deployment logs, should see:
python manage.py migrate

# If not, check Procfile has:
web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn Dlcweb.wsgi:application
```

### Issue 5: "FATAL: password authentication failed"

**Cause:** Wrong DATABASE_URL or PostgreSQL not connected

**Solution:**
1. Go to PostgreSQL service → Variables
2. Copy DATABASE_URL value
3. Go to Django app → Variables
4. Update DATABASE_URL to match

### Issue 6: Build/Deploy failing

**Check Procfile exists and has:**
```
web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn Dlcweb.wsgi:application
```

**Check runtime.txt has:**
```
python-3.11.6
```

---

## 📸 Screenshot Guide

### What to screenshot and share:

**If database not working:**
1. Railway Dashboard showing your services (1 or 2?)
2. Variables tab of Django app
3. Deployment logs (the error)

**If images not working:**
1. Railway Variables tab
2. Cloudinary dashboard showing cloud name
3. Browser console errors (F12 → Console)
4. Image URL (right-click image → Copy image address)

---

## ✅ Final Checklist

Before asking for help, verify:

**Railway Setup:**
- [ ] PostgreSQL service exists
- [ ] Django app service exists
- [ ] DATABASE_URL variable set in Django app
- [ ] CLOUDINARY_CLOUD_NAME variable set
- [ ] CLOUDINARY_API_KEY variable set
- [ ] CLOUDINARY_API_SECRET variable set
- [ ] Latest code pushed to GitHub
- [ ] Railway deployment succeeded (no errors)

**Code Setup:**
- [ ] requirements.txt has cloudinary packages
- [ ] settings.py has cloudinary in INSTALLED_APPS
- [ ] Procfile runs collectstatic and migrate
- [ ] .env not committed to GitHub

**Testing:**
- [ ] Uploaded NEW image after Cloudinary setup
- [ ] Checked image URL contains "cloudinary.com"
- [ ] Redeployed and image still shows
- [ ] Created data and it persists after redeploy

---

## 🆘 Quick Diagnostic Commands

### Check what Railway is using:

**Look at deployment logs for:**
```
Database: postgresql (if using PostgreSQL) ✅
Database: sqlite (if using SQLite) ❌

File storage: cloudinary_storage.storage.MediaCloudinaryStorage (if using Cloudinary) ✅
File storage: django.core.files.storage.FileSystemStorage (if using local) ❌
```

---

## 🎯 Most Likely Issues

Based on your error, it's probably one of these:

1. **DATABASE_URL not set** → Still using SQLite → Data disappears
2. **Cloudinary variables not set** → Still using local storage → Images disappear
3. **Variables set but Railway didn't redeploy** → Old code running
4. **Uploaded old images** → Need to upload new ones after setup

---

## 📞 What to Tell Me

To help you better, please share:

1. **What exactly isn't working?**
   - Images disappearing?
   - Database errors?
   - Deployment failing?

2. **Screenshot of Railway Variables tab**
   - Which variables do you see?

3. **Screenshot of Railway Services**
   - Do you see 1 or 2 services?

4. **Error message (if any)**
   - From deployment logs
   - From browser console

5. **When did you upload the image?**
   - Before or after Cloudinary setup?

---

**Last Updated:** October 25, 2025
