import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dlcweb.settings')
django.setup()

from main.utils import normalize_arabic_text

# Test the normalization function
test_cases = [
    'الوحدات الكلية المجتازة',
    'الوحدات الكليه المجتازه', 
    'اسم الطالب',
    'أسم الطالب',
    'إسم الطالب', 
    'رقم الطالبة',
    'المعدل التراكمى',
    'المعدل التراكمي'
]

print('=== Arabic Text Normalization Test ===')
for text in test_cases:
    normalized = normalize_arabic_text(text)
    print(f'Original: {text}')
    print(f'Normalized: {normalized}')
    print('---')
    
# Test if similar texts normalize to the same thing
print('\n=== Similarity Test ===')
text1 = 'الوحدات الكلية المجتازة'
text2 = 'الوحدات الكليه المجتازه'
norm1 = normalize_arabic_text(text1)
norm2 = normalize_arabic_text(text2)
print(f'Text 1: {text1} -> {norm1}')
print(f'Text 2: {text2} -> {norm2}')
print(f'Are they equal after normalization? {norm1 == norm2}')
