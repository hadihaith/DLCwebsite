"""
Railway Configuration Diagnostic Script

Run this to check your configuration:
python check_config.py
"""

import os
import sys

def check_config():
    print("=" * 60)
    print("RAILWAY CONFIGURATION DIAGNOSTIC")
    print("=" * 60)
    print()
    
    # Check Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dlcweb.settings')
    import django
    django.setup()
    
    from django.conf import settings
    
    # 1. Check Database Configuration
    print("1. DATABASE CONFIGURATION")
    print("-" * 60)
    db_engine = settings.DATABASES['default']['ENGINE']
    print(f"   Engine: {db_engine}")
    
    if 'sqlite' in db_engine:
        print("   ⚠️  WARNING: Using SQLite (local only)")
        print("   ❌ Data will be LOST on Railway restart!")
        print("   ✅ Fix: Add DATABASE_URL to Railway variables")
        db_ok = False
    elif 'postgresql' in db_engine or 'psycopg2' in db_engine:
        print("   ✅ Using PostgreSQL (production ready)")
        print(f"   Host: {settings.DATABASES['default'].get('HOST', 'N/A')}")
        print(f"   Database: {settings.DATABASES['default'].get('NAME', 'N/A')}")
        db_ok = True
    else:
        print(f"   ⚠️  Unknown database: {db_engine}")
        db_ok = False
    
    print()
    
    # 2. Check File Storage Configuration
    print("2. FILE STORAGE CONFIGURATION")
    print("-" * 60)
    file_storage = settings.DEFAULT_FILE_STORAGE
    print(f"   Storage: {file_storage}")
    
    if 'cloudinary' in file_storage.lower():
        print("   ✅ Using Cloudinary (production ready)")
        
        # Check Cloudinary credentials
        cloudinary_config = getattr(settings, 'CLOUDINARY_STORAGE', {})
        cloud_name = cloudinary_config.get('CLOUD_NAME')
        api_key = cloudinary_config.get('API_KEY')
        api_secret = cloudinary_config.get('API_SECRET')
        
        if cloud_name and api_key and api_secret:
            print(f"   ✅ Cloud Name: {cloud_name}")
            print(f"   ✅ API Key: {api_key[:6]}..." if api_key else "   ❌ API Key: Not set")
            print(f"   ✅ API Secret: {'*' * 10}..." if api_secret else "   ❌ API Secret: Not set")
            storage_ok = True
        else:
            print("   ❌ Cloudinary credentials MISSING!")
            print("   ✅ Fix: Add CLOUDINARY_* variables to Railway")
            storage_ok = False
            
    elif 'FileSystemStorage' in file_storage:
        print("   ⚠️  WARNING: Using local file system")
        print("   ❌ Files will be LOST on Railway restart!")
        print("   ✅ Fix: Configure Cloudinary")
        storage_ok = False
    else:
        print(f"   ⚠️  Unknown storage: {file_storage}")
        storage_ok = False
    
    print()
    
    # 3. Check Debug Mode
    print("3. DEBUG MODE")
    print("-" * 60)
    print(f"   DEBUG = {settings.DEBUG}")
    
    if settings.DEBUG:
        print("   ⚠️  WARNING: Debug mode is ON")
        print("   💡 This is OK for local development")
        print("   ❌ Should be OFF in production (Railway)")
        print("   ✅ Fix: Set RAILWAY_ENVIRONMENT in Railway")
        debug_ok = False
    else:
        print("   ✅ Debug mode is OFF (production mode)")
        debug_ok = True
    
    print()
    
    # 4. Check Installed Apps
    print("4. CLOUDINARY APPS")
    print("-" * 60)
    has_cloudinary_storage = 'cloudinary_storage' in settings.INSTALLED_APPS
    has_cloudinary = 'cloudinary' in settings.INSTALLED_APPS
    
    print(f"   cloudinary_storage: {'✅ Installed' if has_cloudinary_storage else '❌ Missing'}")
    print(f"   cloudinary: {'✅ Installed' if has_cloudinary else '❌ Missing'}")
    
    apps_ok = has_cloudinary_storage and has_cloudinary
    
    if not apps_ok:
        print("   ✅ Fix: Check settings.py INSTALLED_APPS")
    
    print()
    
    # 5. Check Environment Variables
    print("5. ENVIRONMENT VARIABLES")
    print("-" * 60)
    
    env_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'CLOUDINARY_CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'CLOUDINARY_API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'CLOUDINARY_API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
    }
    
    for var, value in env_vars.items():
        if value:
            if 'SECRET' in var or 'PASSWORD' in var or 'URL' in var:
                print(f"   ✅ {var}: {'*' * 10}... (set)")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            if var in ['DATABASE_URL', 'CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']:
                print(f"   ❌ {var}: Not set (REQUIRED for production)")
            else:
                print(f"   ⚠️  {var}: Not set (optional)")
    
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_ok = db_ok and storage_ok and apps_ok
    
    if all_ok:
        print("✅ CONFIGURATION LOOKS GOOD!")
        print()
        print("Your app should work correctly on Railway.")
    else:
        print("❌ CONFIGURATION HAS ISSUES!")
        print()
        print("Issues found:")
        if not db_ok:
            print("   - Database: Not using PostgreSQL")
        if not storage_ok:
            print("   - File Storage: Not using Cloudinary")
        if not apps_ok:
            print("   - Apps: Cloudinary apps not installed")
        
        print()
        print("Next steps:")
        print("1. Review the issues above")
        print("2. Check RAILWAY_TROUBLESHOOTING.md for solutions")
        print("3. Add missing environment variables to Railway")
        print("4. Redeploy after fixing issues")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    try:
        check_config()
    except Exception as e:
        print(f"❌ Error running diagnostic: {e}")
        print()
        print("Make sure you're in the project directory and Django is installed.")
        sys.exit(1)
