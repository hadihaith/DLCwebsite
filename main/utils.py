import pandas as pd
import re

from main.models import DeanList

def process_dean_list_excel(excel_file, semester, year):
    try:
        print("=== STARTING process_dean_list_excel ===")
        # Read the Excel file once with no header to examine all rows
        original_df = pd.read_excel(excel_file, engine='openpyxl', header=None)
        print(f"Excel file read successfully. Shape: {original_df.shape}")
        
        # Find the header row
        header_row_index = find_header_row(original_df)
        print(f"find_header_row returned: {header_row_index}")
        
        if header_row_index is None:
            raise ValueError("Could not find a valid header row in the Excel file")
        
        # Extract the header row content
        header_row = original_df.iloc[header_row_index]
        print(f"Header row content: {header_row.tolist()}")
        
        # Create a new DataFrame with the data starting after the header row
        data_rows = original_df.iloc[header_row_index + 1:]  # Skip header row
        
        # Set the column names from the header row
        column_names = []
        for i, val in enumerate(header_row):
            if pd.isna(val) or str(val).strip() == '':
                column_names.append(f'Unnamed_{i}')
            else:
                column_names.append(str(val).strip())
        
        data_rows.columns = column_names
        
        # Reset the index
        df = data_rows.reset_index(drop=True)
        
        print(f"Final DataFrame shape: {df.shape}")
        print(f"Final columns: {list(df.columns)}")
        
        # Store the data in the database
        print("About to store data in database...")
        students_saved = store_excel_data_in_database(df, semester, year)
        print(f"Database storage completed. {students_saved} students saved.")
        cleanup_invalid_dean_list_records()
        # Return the DataFrame and summary info
        return df, header_row_index, students_saved

    except Exception as e:
        print(f"ERROR in process_dean_list_excel: {str(e)}")
        raise ValueError(f"Error processing Excel file: {str(e)}")


def store_excel_data_in_database(df, semester, year):
    """
    Store the processed Excel data in the database.
    Returns the number of students successfully saved.
    """
    from .models import DeanListStudent
    
    print("=== STORING DATA IN DATABASE ===")
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {list(df.columns)}")
    print(f"Semester: {semester}, Year: {year}")

    # Define possible column names for each field with various Arabic spelling variations
    passed_credits_names = [
        'الوحدات الكلية المجتازة',
        'الوحدات المجتازة', 
        'الوحدات المجتازه',
        'الوحدات الكليه المجتازه',
        'الوحدات الكليه المجتازة',
        'الوحدات الكليه المجتازه',
        'الوحدات المكتسبة',
        'الوحدات المكتسبه',
        'الوحدات المنجزة',
        'الوحدات المنجزه'
    ]
    
    student_name_names = [
        'اسم الطالب',
        'اسم الطالبة',
        'اسم الطالب/ة',
        'الاسم',
        'الإسم',
        'أسم الطالب',
        'إسم الطالب',
        'Student Name',
        'Name'
    ]
    
    student_id_names = [
        'رقم الطالب',
        'رقم الطالبة',
        'رقم الطالب/ة',
        'الرقم الجامعي',
        'الرقم الجامعى',
        'رقم الهوية',
        'رقم الهويه',
        'Student ID',
        'ID'
    ]
    
    gpa_names = [
        'المعدل العام',
        'المعدل',
        'المعدل التراكمي',
        'المعدل التراكمى',
        'GPA',
        'Grade Point Average'
    ]
    
    major_names = [
        'التخصص', 
        'التخصص الدراسي', 
        'Major'
    ]
    
    registered_credits_names = [
        'الوحدات المسجلة', 
        'الوحدات المسجله', 
        'Registered Credits'
    ]
    
    # Find actual column names
    passed_credits_column = find_column_by_names(df, passed_credits_names)
    student_name_column = find_column_by_names(df, student_name_names)
    student_id_column = find_column_by_names(df, student_id_names)
    gpa_column = find_column_by_names(df, gpa_names)
    major_column = find_column_by_names(df, major_names)
    registered_credits_column = find_column_by_names(df, registered_credits_names)
    
    print(f"Found columns:")
    print(f"  Student name: {student_name_column}")
    print(f"  Student ID: {student_id_column}")
    print(f"  GPA: {gpa_column}")
    print(f"  Passed credits: {passed_credits_column}")
    print(f"  Major: {major_column}")
    print(f"  Registered credits: {registered_credits_column}")
    
    # Show normalized versions for debugging
    if student_name_column:
        print(f"  Student name normalized: '{normalize_arabic_text(student_name_column)}'")
    if passed_credits_column:
        print(f"  Passed credits normalized: '{normalize_arabic_text(passed_credits_column)}'")
    
    # Check if we found the essential columns
    if not student_name_column or not student_id_column:
        print("ERROR: Could not find essential columns (student name or ID)")
        print("Available columns:", list(df.columns))
        return 0
    
    saved_count = 0
    error_count = 0
    
    print(f"\nProcessing {len(df)} rows...")
    
    for index, row in df.iterrows():
        try:
            # Debug print for first few rows
            if index < 3:
                print(f"\nRow {index} data:")
                for col in df.columns:
                    print(f"  {col}: {row[col]}")
            
            # Get values with fallbacks
            student_name = row.get(student_name_column, '') if student_name_column else ''
            student_id = row.get(student_id_column, '') if student_id_column else ''
            gpa_value = row.get(gpa_column, 0.0) if gpa_column else 0.0
            
            # Handle passed_credits
            passed_credits_value = 0
            if passed_credits_column:
                passed_credits_value = row.get(passed_credits_column, 0)
                if pd.isna(passed_credits_value):
                    passed_credits_value = 0
            
            # Convert values to appropriate types
            try:
                gpa_value = float(gpa_value) if not pd.isna(gpa_value) else 0.0
                passed_credits_value = int(passed_credits_value) if not pd.isna(passed_credits_value) else 0
            except (ValueError, TypeError):
                print(f"Warning: Could not convert numeric values for student {student_id}")
                gpa_value = 0.0
                passed_credits_value = 0
            
            # Skip empty rows
            if not student_name or not student_id:
                print(f"Skipping empty row {index}")
                continue
            
            # Create and save the student record
            student = DeanListStudent(
                student_name=str(student_name),
                student_id=str(student_id),
                student_major=row.get(major_column, '') if major_column else '',
                semester=semester,
                year=year,
                gpa=gpa_value,
                passed_credits=passed_credits_value,
                registered_credits=get_numeric_value(row, registered_credits_column),
                dean_list=DeanList.objects.get(semester=semester, year=year)  # Link to the DeanList instance
            )
            student.save()
            saved_count += 1
            
            if index < 3:
                print(f"Successfully saved student: {student_name} (ID: {student_id})")
                
        except Exception as e:
            error_count += 1
            print(f"Error saving student at row {index}: {str(e)}")
            print(f"  Student data: Name='{student_name}', ID='{student_id}'")
            continue
    
    print(f"\n=== DATABASE STORAGE SUMMARY ===")
    print(f"Total rows processed: {len(df)}")
    print(f"Successfully saved: {saved_count}")
    print(f"Errors: {error_count}")
    print("=== END DATABASE STORAGE ===\n")
    
    return saved_count

def find_header_row(df):
    """
    Find the first row that:
    1. Has no numbers (likely contains column headers)
    2. Has at least 3 non-empty fields
    """
    print("=== SEARCHING FOR HEADER ROW ===")
    for index, row in df.iterrows():
   
        non_empty_count = row.notna().sum()
        print(f"Row {index}: {non_empty_count} non-empty values")
        

        non_empty_values = [str(val) for val in row.dropna().tolist()]
        print(f"  Values: {non_empty_values}")
        

        if non_empty_count >= 3:

            has_numbers = False
            number_details = []
            
            for value in row.dropna():
  
                if isinstance(value, (int, float)) and not pd.isna(value):
                    has_numbers = True
                    number_details.append(f"numeric value: {value}")
                    break
                elif isinstance(value, str):

                    numeric_chars = len(re.findall(r'\d', value))
                    total_chars = len(value.strip())
                    
  
                    if total_chars > 0:
                        if value.strip().isdigit():  
                            has_numbers = True
                            number_details.append(f"pure number string: '{value}'")
                            break
                        elif numeric_chars > total_chars * 0.7:  
                            has_numbers = True
                            number_details.append(f"mostly numeric: '{value}' ({numeric_chars}/{total_chars} digits)")
                            break
            
            print(f"  Has numbers: {has_numbers}")
            if number_details:
                print(f"  Number details: {number_details}")

            if not has_numbers:
                print(f"*** HEADER ROW FOUND AT INDEX {index} ***")
                print(f"    Row content: {row.tolist()}")
                return index
            else:
                print(f"  Skipping row {index} - contains numbers")

    
    print("No valid header row found")
    return None


def normalize_arabic_text(text):
    """
    Normalize Arabic text by:
    1. Converting to string and stripping whitespace
    2. Removing diacritics (تشكيل)
    3. Normalizing different forms of letters
    4. Standardizing spaces
    """
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text).strip()
    
    # Remove common diacritics (تشكيل)
    diacritics = [
        '\u064B',  # فتحتان
        '\u064C',  # ضمتان
        '\u064D',  # كسرتان
        '\u064E',  # فتحة
        '\u064F',  # ضمة
        '\u0650',  # كسرة
        '\u0651',  # شدة
        '\u0652',  # سكون
        '\u0653',  # مدة
        '\u0654',  # همزة علوية
        '\u0655',  # همزة سفلية
        '\u0656',  # subscript alef
        '\u0657',  # inverted damma
        '\u0658',  # mark noon ghunna
        '\u0659',  # zwarakay
        '\u065A',  # vowel sign small v above
        '\u065B',  # vowel sign inverted small v above
        '\u065C',  # vowel sign dot below
        '\u065D',  # reversed damma
        '\u065E',  # fatha with two dots
        '\u065F',  # wavy hamza below
        '\u0670',  # superscript alef
    ]
    
    for diacritic in diacritics:
        text = text.replace(diacritic, '')
    
    # Normalize letter variations
    # Different forms of Alef
    text = text.replace('أ', 'ا')  # Alef with hamza above
    text = text.replace('إ', 'ا')  # Alef with hamza below
    text = text.replace('آ', 'ا')  # Alef with madda above
    
    # Different forms of Teh Marbuta
    text = text.replace('ة', 'ه')  # Teh marbuta to heh
    
    # Different forms of Yeh
    text = text.replace('ى', 'ي')  # Alef maksura to yeh
    text = text.replace('ئ', 'ي')  # Yeh with hamza above
    
    # Normalize spaces (including Arabic spaces)
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = text.replace('\u00A0', ' ')  # Non-breaking space to regular space
    text = text.replace('\u200B', '')  # Zero-width space
    
    return text.strip()


def find_column_by_normalized_names(df, possible_names):
    """
    Find a column in the DataFrame by checking multiple possible names using normalization.
    Returns the first matching column name found, or None if not found.
    """
    # Normalize the possible names
    normalized_possible = [normalize_arabic_text(name) for name in possible_names]
    
    # Check each column in the DataFrame
    for col in df.columns:
        normalized_col = normalize_arabic_text(col)
        if normalized_col in normalized_possible:
            return col
    return None


def find_column_by_names(df, possible_names):
    """
    Find a column in the DataFrame by checking multiple possible names.
    First tries exact match, then tries normalized match.
    Returns the first matching column name found, or None if not found.
    """
    # First try exact matches
    for name in possible_names:
        if name in df.columns:
            return name
    
    # If no exact match, try normalized matching
    return find_column_by_normalized_names(df, possible_names)


def get_numeric_value(row, column_name, default=0):
    """
    Helper function to safely get numeric values from DataFrame row.
    """
    if not column_name:
        return default
    
    value = row.get(column_name, default)
    if pd.isna(value):
        return default
    
    try:
        return int(value) if isinstance(value, (int, float)) else default
    except (ValueError, TypeError):
        return default


def cleanup_invalid_dean_list_records():
    """
    Clean up the database by removing any DeanListStudent records 
    with NaN, empty, or invalid student_id or student_name fields.
    
    Returns a dictionary with cleanup statistics.
    """
    from .models import DeanListStudent
    
    print("=== STARTING DATABASE CLEANUP ===")
    
    # Get all DeanListStudent records
    all_students = DeanListStudent.objects.all()
    total_count = all_students.count()
    print(f"Total records in database: {total_count}")
    
    if total_count == 0:
        print("No records found in database.")
        return {'deleted': 0, 'total': 0, 'remaining': 0}
    
    deleted_count = 0
    invalid_records = []
    
    # Check each record for invalid data
    for student in all_students:
        should_delete = False
        reason = []
        
        # Check student_name
        if not student.student_name or student.student_name.strip() == '':
            should_delete = True
            reason.append("empty student_name")
        elif str(student.student_name).lower() in ['nan', 'none', 'null']:
            should_delete = True
            reason.append("invalid student_name (nan/none/null)")
        
        # Check student_id
        if not student.student_id or student.student_id.strip() == '':
            should_delete = True
            reason.append("empty student_id")
        elif str(student.student_id).lower() in ['nan', 'none', 'null']:
            should_delete = True
            reason.append("invalid student_id (nan/none/null)")
        
        if should_delete:
            invalid_records.append({
                'id': student.id,
                'student_name': student.student_name,
                'student_id': student.student_id,
                'semester': student.semester,
                'year': student.year,
                'reason': ', '.join(reason)
            })
    
    # Show what will be deleted
    if invalid_records:
        print(f"\nFound {len(invalid_records)} invalid records to delete:")
        for i, record in enumerate(invalid_records[:10]):  # Show first 10
            print(f"  {i+1}. ID={record['id']}, Name='{record['student_name']}', Student_ID='{record['student_id']}' - Reason: {record['reason']}")
        
        if len(invalid_records) > 10:
            print(f"  ... and {len(invalid_records) - 10} more records")
        
        # Delete the invalid records
        print(f"\nDeleting {len(invalid_records)} invalid records...")
        for record in invalid_records:
            try:
                student = DeanListStudent.objects.get(id=record['id'])
                student.delete()
                deleted_count += 1
            except DeanListStudent.DoesNotExist:
                print(f"Warning: Record with ID {record['id']} not found (may have been already deleted)")
            except Exception as e:
                print(f"Error deleting record ID {record['id']}: {str(e)}")
    
    remaining_count = DeanListStudent.objects.count()
    
    print(f"\n=== CLEANUP SUMMARY ===")
    print(f"Total records before cleanup: {total_count}")
    print(f"Invalid records deleted: {deleted_count}")
    print(f"Records remaining: {remaining_count}")
    print(f"Cleanup completed successfully.")
    print("=== END CLEANUP ===\n")
    
    return {
        'deleted': deleted_count,
        'total': total_count,
        'remaining': remaining_count,
        'invalid_records': invalid_records
    }

def delete_dean_list_students(semester, year):
    """
    Delete all DeanListStudent records for a specific semester and year.
    Returns the number of records deleted.
    """
    from .models import DeanListStudent
    
    print(f"=== DELETING DeanListStudent RECORDS FOR {semester} {year} ===")
    
    students_to_delete = DeanListStudent.objects.filter(semester=semester, year=year)
    count_to_delete = students_to_delete.count()
    
    if count_to_delete == 0:
        print("No records found to delete.")
        return 0
    
    print(f"Found {count_to_delete} records to delete.")
    
    deleted_count = 0
    for student in students_to_delete:
        try:
            student.delete()
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting record ID {student.id}: {str(e)}")
    
    print(f"Deleted {deleted_count} records for {semester} {year}.")
    print("=== END DELETION ===\n")
    
    return deleted_count