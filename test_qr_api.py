from urllib.parse import quote

# Test different encoding methods
test_url = "http://localhost:8000/events/verify/start/636248/292432/469775/"

print("="*80)
print("Testing Google Charts QR API URLs")
print("="*80)

# Method 1: quote with safe=''
encoded1 = quote(test_url, safe='')
qr1 = f"https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={encoded1}"
print(f"\n1. Using quote(url, safe=''):")
print(f"   Encoded: {encoded1}")
print(f"   QR URL: {qr1}")

# Method 2: quote with default safe='/'
encoded2 = quote(test_url)
qr2 = f"https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={encoded2}"
print(f"\n2. Using quote(url) [default safe='/']:")
print(f"   Encoded: {encoded2}")
print(f"   QR URL: {qr2}")

# Method 3: No encoding (might fail)
qr3 = f"https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={test_url}"
print(f"\n3. No encoding:")
print(f"   QR URL: {qr3}")

print("\n" + "="*80)
print("⚠️  Note: Google Charts QR API has been deprecated since 2012!")
print("    It may not work reliably. Consider using an alternative.")
print("="*80)

print("\n📋 Alternative solutions:")
print("   1. Use qrcode library (pip install qrcode[pil])")
print("   2. Use api.qrserver.com")
print("   3. Use goqr.me API")
print("   4. Generate QR codes server-side")
print("\nLet's test with api.qrserver.com instead:")

qr_alt = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(test_url)}"
print(f"\nAlternative QR URL: {qr_alt}")
print("\n✅ This should work!")
