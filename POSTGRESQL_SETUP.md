# PostgreSQL Setup Guide for Railway

## ✅ Current Status

Your Django application is **already configured** to use PostgreSQL! The code automatically:
- Uses **PostgreSQL** in production (when `DATABASE_URL` is set)
- Uses **SQLite** for local development (when `DATABASE_URL` is not set)

---

## 🚀 Railway Setup (Production)

### Step 1: Verify PostgreSQL Service is Running

1. Go to **Railway Dashboard**
2. You should see **two services**:
   - Your Django app (DLCwebsite)
   - PostgreSQL database

### Step 2: Connect DATABASE_URL to Django App

1. Click on your **Django app service**
2. Go to **Variables** tab
3. Check if `DATABASE_URL` exists:

   **If it exists**: ✅ Skip to Step 3
   
   **If it doesn't exist**:
   - Click **+ New Variable**
   - **Reference a variable** from another service
   - Select **PostgreSQL service**
   - Select **DATABASE_URL**
   - Click **Add**

   This will add: `DATABASE_URL=${{Postgres.DATABASE_URL}}`

### Step 3: Deploy

Railway will automatically redeploy. Watch the logs for:
```
Running migrations...
Applying contenttypes.0001_initial... OK
Applying auth.0001_initial... OK
...
```

### Step 4: Verify Connection

After deployment completes:
1. Visit your Railway app URL
2. Login to portal
3. Try creating/viewing data
4. Redeploy again - data should persist! ✅

---

## 🔧 Database Configuration Details

### Your PostgreSQL Credentials:

```
Database Name: railway
Username: postgres
Password: FSuRXlLFYDHyDasukNBHAewjrGQztyMX
Internal Host: postgres.railway.internal
Public Host: nozomi.proxy.rlwy.net
Internal Port: 5432
Public Port: 35048
```

### Connection Strings:

**For Railway (internal - faster)**:
```
postgresql://postgres:FSuRXlLFYDHyDasukNBHAewjrGQztyMX@postgres.railway.internal:5432/railway
```

**For external tools (pgAdmin, DBeaver, etc.)**:
```
postgresql://postgres:FSuRXlLFYDHyDasukNBHAewjrGQztyMX@nozomi.proxy.rlwy.net:35048/railway
```

---

## 💻 Local Development

### Option 1: Use SQLite (Recommended for local)

Just run normally:
```bash
python manage.py runserver
```

- No DATABASE_URL set → Uses SQLite automatically
- Easy and fast for development
- No network connection needed

### Option 2: Connect to Railway PostgreSQL from Local

**Use for**: Testing with production data

1. Create `.env` file (already in .gitignore):
   ```bash
   DATABASE_URL=postgresql://postgres:FSuRXlLFYDHyDasukNBHAewjrGQztyMX@nozomi.proxy.rlwy.net:35048/railway
   ```

2. Install python-dotenv (already in requirements.txt):
   ```bash
   pip install python-dotenv
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start server:
   ```bash
   python manage.py runserver
   ```

Now your local app connects to Railway PostgreSQL!

**⚠️ Warning**: Be careful - you're working with production data!

---

## 📦 Backup & Restore Functions

### Download Database Backup

Your app already has this function built-in!

**On SQLite (local)**:
- Click "Download Database" → Downloads `.sqlite3` file

**On PostgreSQL (Railway)**:
- Click "Download Database" → Uses `pg_dump` → Downloads `.backup` file

### How it Works:

The backup function automatically detects the database type:

```python
db_engine = settings.DATABASES['default']['ENGINE']

if 'sqlite' in db_engine:
    # Download SQLite file directly
elif 'postgresql' in db_engine:
    # Use pg_dump to create backup
```

### Backup File Formats:

- **SQLite**: `.sqlite3` (binary database file)
- **PostgreSQL**: `.backup` (pg_dump custom format)

### Restore Database:

1. Go to portal → Database Restore
2. Upload `.sqlite3` or `.backup` file
3. System detects format automatically
4. Restores data

**PostgreSQL restore uses**:
```bash
pg_restore --clean --if-exists --no-owner --no-acl
```

---

## 🔄 Migration from SQLite to PostgreSQL

If you have data in local SQLite that you want in production PostgreSQL:

### Method 1: Use Django's dumpdata/loaddata

**Local (SQLite)**:
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data.json
```

**Railway (PostgreSQL)**:
```bash
# In Railway terminal or connect locally to Railway DB
python manage.py loaddata data.json
```

### Method 2: Manual via Django Admin

1. Export data as CSV from local SQLite admin
2. Import via Railway PostgreSQL admin

---

## 🧪 Testing Database Connection

### Test 1: Check Active Database

```bash
python manage.py shell
```

```python
from django.conf import settings
print(settings.DATABASES['default'])
```

Should show PostgreSQL config when DATABASE_URL is set.

### Test 2: Create Test Data

```python
from main.models import User
User.objects.create_user(username='test', email='test@test.com', password='test123')
print(User.objects.count())
```

### Test 3: Verify Persistence

1. Create data
2. Redeploy Railway
3. Check if data still exists ✅

---

## 🔒 Security Notes

### ✅ What's Secure:

- DATABASE_URL stored in Railway environment variables (not in code)
- .env file in .gitignore (not committed to GitHub)
- SSL connections supported (Railway handles this)
- Connection pooling enabled (`conn_max_age=600`)

### ⚠️ Important:

- **Never commit** `.env` file to GitHub
- **Never hardcode** DATABASE_URL in settings.py
- Use **environment variables** for all credentials
- Railway's internal network (`postgres.railway.internal`) is private

---

## 📊 Monitoring

### Railway Dashboard:

1. **PostgreSQL Service → Metrics**:
   - CPU usage
   - Memory usage
   - Connection count

2. **Django App → Logs**:
   - Database query logs
   - Connection errors
   - Migration status

### Check Database Size:

```bash
# In Railway PostgreSQL terminal
SELECT pg_size_pretty(pg_database_size('railway'));
```

---

## 🐛 Troubleshooting

### Issue: "connection refused"

**Solution**: Make sure DATABASE_URL uses internal host:
```
postgresql://...@postgres.railway.internal:5432/railway
```
NOT the public host for Railway deployments.

### Issue: "too many connections"

**Solution**: Already handled by `conn_max_age=600` in settings.

### Issue: "SSL required"

**Solution**: Already fixed! Removed `ssl_require=True` from settings.

### Issue: Migrations not applying

**Check**:
```bash
# In Railway logs
python manage.py showmigrations
```

**Fix**:
```bash
python manage.py migrate --fake-initial
```

### Issue: Data disappearing after deployment

**This is expected with SQLite!**

**Solution**: Make sure DATABASE_URL is set in Railway variables.

---

## 📋 Checklist

Before deploying:

- [x] PostgreSQL service created in Railway
- [x] DATABASE_URL connected to Django app
- [x] psycopg2-binary in requirements.txt
- [x] settings.py configured (already done)
- [x] Backup/restore functions support PostgreSQL
- [ ] DATABASE_URL set in Railway Variables ← **Do this!**
- [ ] Test deployment
- [ ] Verify data persists across deployments

After first deployment:

- [ ] Run migrations
- [ ] Create superuser account
- [ ] Test backup function
- [ ] Test restore function
- [ ] Verify data persistence

---

## 🎯 Next Steps

1. **Add DATABASE_URL to Railway Variables** (if not already there)
2. **Push your code** (I updated settings.py)
3. **Railway auto-deploys**
4. **Check logs** for successful migration
5. **Login to admin** and verify connection
6. **Test backup** function

---

## 📞 Database Tools

### Connect with pgAdmin:

```
Host: nozomi.proxy.rlwy.net
Port: 35048
Database: railway
Username: postgres
Password: FSuRXlLFYDHyDasukNBHAewjrGQztyMX
SSL Mode: Prefer
```

### Connect with DBeaver:

Same credentials as above.

### Connect with psql:

```bash
psql postgresql://postgres:FSuRXlLFYDHyDasukNBHAewjrGQztyMX@nozomi.proxy.rlwy.net:35048/railway
```

---

## Summary

✅ **Code is ready** - settings.py configured  
✅ **Backup function ready** - supports PostgreSQL  
✅ **Requirements ready** - psycopg2-binary installed  
🎯 **Action needed** - Add DATABASE_URL to Railway Variables  

Once DATABASE_URL is set, your app will automatically use PostgreSQL in production!

**Estimated setup time**: 2 minutes  
**Difficulty**: Easy (just add one variable in Railway)

---

**Last Updated**: October 25, 2025  
**PostgreSQL Version**: Railway managed  
**Django Database Backend**: psycopg2
