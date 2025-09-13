from django.core.management.base import BaseCommand
from main.models import DeanListStudent


class Command(BaseCommand):
    help = 'Clean dean list records for specific years (removes records with invalid data)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--years',
            nargs='+',
            type=int,
            help='Years to clean (space-separated list)',
            required=False
        )
        parser.add_argument(
            '--exclude-from',
            type=int,
            help='Exclude years from this year onwards (e.g., --exclude-from 2021)',
            required=False
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        years_to_clean = options.get('years')
        exclude_from = options.get('exclude_from')
        dry_run = options.get('dry_run', False)
        
        # If exclude_from is specified, get all years below that threshold
        if exclude_from:
            all_years = DeanListStudent.objects.values_list('year', flat=True).distinct()
            years_to_clean = [year for year in all_years if year < exclude_from]
            self.stdout.write(f"Cleaning years below {exclude_from}: {sorted(years_to_clean)}")
        elif years_to_clean:
            self.stdout.write(f"Cleaning specified years: {sorted(years_to_clean)}")
        else:
            self.stderr.write("Please specify either --years or --exclude-from")
            return
        
        if not years_to_clean:
            self.stdout.write("No years to clean.")
            return
        
        total_deleted = 0
        total_checked = 0
        
        for year in sorted(years_to_clean):
            self.stdout.write(f"\n=== Processing Year {year} ===")
            
            # Get all records for this year
            year_students = DeanListStudent.objects.filter(year=year)
            year_count = year_students.count()
            total_checked += year_count
            
            if year_count == 0:
                self.stdout.write(f"No records found for year {year}")
                continue
                
            self.stdout.write(f"Found {year_count} records for year {year}")
            
            # Find invalid records
            invalid_records = []
            for student in year_students:
                should_delete = False
                reasons = []
                
                # Check student_name
                if not student.student_name or student.student_name.strip() == '':
                    should_delete = True
                    reasons.append("empty student_name")
                elif str(student.student_name).lower() in ['nan', 'none', 'null']:
                    should_delete = True
                    reasons.append("invalid student_name")
                
                # Check student_id
                if not student.student_id or student.student_id.strip() == '':
                    should_delete = True
                    reasons.append("empty student_id")
                elif str(student.student_id).lower() in ['nan', 'none', 'null']:
                    should_delete = True
                    reasons.append("invalid student_id")
                else:
                    # Check if student_id has fewer than 5 digits
                    student_id_digits = ''.join(filter(str.isdigit, str(student.student_id)))
                    if len(student_id_digits) < 5:
                        should_delete = True
                        reasons.append(f"student_id too short ({len(student_id_digits)} digits, need at least 5)")
                
                if should_delete:
                    invalid_records.append({
                        'student': student,
                        'reasons': reasons
                    })
            
            if invalid_records:
                self.stdout.write(f"Found {len(invalid_records)} invalid records in year {year}:")
                
                # Show a few examples
                for i, record in enumerate(invalid_records[:5]):
                    student = record['student']
                    reasons = ', '.join(record['reasons'])
                    self.stdout.write(f"  - ID={student.id}, Name='{student.student_name}', Student_ID='{student.student_id}', Semester={student.semester} - {reasons}")
                
                if len(invalid_records) > 5:
                    self.stdout.write(f"  ... and {len(invalid_records) - 5} more")
                
                if not dry_run:
                    # Delete the invalid records
                    deleted_count = 0
                    for record in invalid_records:
                        try:
                            record['student'].delete()
                            deleted_count += 1
                        except Exception as e:
                            self.stderr.write(f"Error deleting record ID {record['student'].id}: {str(e)}")
                    
                    self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} invalid records from year {year}"))
                    total_deleted += deleted_count
                else:
                    self.stdout.write(f"DRY RUN: Would delete {len(invalid_records)} records from year {year}")
                    total_deleted += len(invalid_records)
            else:
                self.stdout.write(f"No invalid records found in year {year}")
        
        # Final summary
        self.stdout.write(f"\n=== CLEANUP SUMMARY ===")
        self.stdout.write(f"Years processed: {sorted(years_to_clean)}")
        self.stdout.write(f"Total records checked: {total_checked}")
        if dry_run:
            self.stdout.write(f"Records that would be deleted: {total_deleted}")
        else:
            self.stdout.write(self.style.SUCCESS(f"Total records deleted: {total_deleted}"))
        self.stdout.write("=== CLEANUP COMPLETE ===")