from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Event, ExchangeApplication, PartnerUniversity, ParkingApplication


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'image_url',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date cannot be before start date.')
        return cleaned


class PartnerUniversityForm(forms.ModelForm):
    class Meta:
        model = PartnerUniversity
        fields = ['name', 'logo_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University Name'}),
            'logo_url': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://example.com/logo.png',
                'help_text': 'Enter the URL of the university logo image'
            }),
        }
        labels = {
            'name': 'University Name',
            'logo_url': 'Logo URL',
        }
        help_texts = {
            'logo_url': 'Paste the direct URL to the university logo image (e.g., from the university website or an image hosting service)',
        }


class BulkPartnerUniversityForm(forms.Form):
    """Form for bulk adding partner universities via text input"""
    bulk_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Enter one partner per line in the format:\nUniversity Name, https://example.com/logo.png\n\nExample:\nHarvard University, https://example.com/harvard-logo.png\nOxford University, https://example.com/oxford-logo.png\nTokyo University, https://example.com/tokyo-logo.png'
        }),
        label='Partner Universities',
        help_text='Enter one partner per line. Format: University Name, Logo URL'
    )

    def clean_bulk_data(self):
        """Validate and parse bulk partner data"""
        data = self.cleaned_data.get('bulk_data', '').strip()
        if not data:
            raise forms.ValidationError('Please enter at least one partner university.')
        
        lines = [line.strip() for line in data.split('\n') if line.strip()]
        parsed_partners = []
        errors = []
        
        for idx, line in enumerate(lines, 1):
            # Split by comma
            parts = [part.strip() for part in line.split(',', 1)]
            
            if len(parts) < 2:
                errors.append(f'Line {idx}: Missing comma separator. Expected format: "Name, URL"')
                continue
            
            name, logo_url = parts[0], parts[1]
            
            # Validate name
            if not name:
                errors.append(f'Line {idx}: University name is required.')
                continue
            
            if len(name) > 255:
                errors.append(f'Line {idx}: University name is too long (max 255 characters).')
                continue
            
            # Validate URL (basic check)
            if logo_url and not (logo_url.startswith('http://') or logo_url.startswith('https://')):
                errors.append(f'Line {idx}: Logo URL must start with http:// or https://')
                continue
            
            # Check for duplicates in the current batch
            if any(p['name'].lower() == name.lower() for p in parsed_partners):
                errors.append(f'Line {idx}: Duplicate university name "{name}" in your input.')
                continue
            
            # Check if already exists in database
            if PartnerUniversity.objects.filter(name__iexact=name).exists():
                errors.append(f'Line {idx}: University "{name}" already exists in the database.')
                continue
            
            parsed_partners.append({
                'name': name,
                'logo_url': logo_url if logo_url else ''
            })
        
        if errors:
            raise forms.ValidationError('\n'.join(errors))
        
        if not parsed_partners:
            raise forms.ValidationError('No valid partner universities found to add.')
        
        return parsed_partners


class ExchangeApplicationForm(forms.ModelForm):
    class Meta:
        model = ExchangeApplication
        fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'program_level',
            'home_institution',
            'home_major',
            'exchange_semester',
            'exchange_academic_year',
            'passport_number',
            'passport_expiry_date',
            'email',
            'completed_credits',
            'accommodation_needed',
            'has_criminal_record',
            'coordinator_name',
            'coordinator_email',
        ]
        labels = {
            'first_name': 'First name (exactly as shown on passport)',
            'last_name': 'Last name (exactly as shown on passport)',
            'date_of_birth': 'Date of birth',
            'gender': 'Gender',
            'program_level': 'Program level',
            'home_institution': 'Home institution',
            'home_major': 'Home institution major',
            'exchange_semester': 'Exchange semester',
            'exchange_academic_year': 'Exchange academic year',
            'passport_number': 'Passport number',
            'passport_expiry_date': 'Passport expiry date (must be valid for 1+ year at time of application)',
            'email': 'Email address',
            'completed_credits': 'Completed credits at home institution',
            'accommodation_needed': 'Accommodation required',
            'has_criminal_record': 'Applicant has an existing criminal record',
            'coordinator_name': 'Home institution coordinator name',
            'coordinator_email': 'Home institution coordinator email',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'program_level': forms.Select(attrs={'class': 'form-select'}),
            'home_institution': forms.Select(attrs={'class': 'form-select'}),
            'home_major': forms.TextInput(attrs={'class': 'form-control'}),
            'exchange_semester': forms.Select(attrs={'class': 'form-select'}),
            'exchange_academic_year': forms.Select(attrs={'class': 'form-select'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'completed_credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'accommodation_needed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_criminal_record': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'coordinator_name': forms.TextInput(attrs={'class': 'form-control'}),
            'coordinator_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = timezone.now().year
        year_choices = []
        choices = [('','Select academic year')]
        for i in range(5):
            start_year = current_year + i
            choices.append((f"{start_year}/{start_year + 1}", f"{start_year}/{start_year + 1}"))
        self.fields['exchange_academic_year'].choices = choices

        self.fields['home_institution'].queryset = PartnerUniversity.objects.order_by('name')
        self.fields['home_institution'].empty_label = 'Select home institution'

    def clean_passport_expiry_date(self):
        expiry = self.cleaned_data.get('passport_expiry_date')
        if expiry:
            min_valid_date = timezone.now().date() + timedelta(days=365)
            if expiry <= min_valid_date:
                raise forms.ValidationError('Passport must remain valid for at least one year from today.')
        return expiry

    def clean_completed_credits(self):
        credits = self.cleaned_data.get('completed_credits')
        if credits is not None and credits < 0:
            raise forms.ValidationError('Completed credits cannot be negative.')
        return credits


class ParkingApplicationForm(forms.ModelForm):
    class Meta:
        model = ParkingApplication
        fields = ['student_id', 'student_name', 'phone', 'gpa', 'completed_credits', 'major', 'has_kuwaiti_license']
        labels = {
            'student_id': 'Student ID',
            'student_name': 'Student Name',
            'phone': 'Phone Number',
            'gpa': 'GPA',
            'completed_credits': 'Completed Credits',
            'major': 'Major',
            'has_kuwaiti_license': 'I have a Kuwaiti driver\'s license',
        }
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your student ID'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '4.00', 'placeholder': '3.5 or higher'}),
            'completed_credits': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'e.g., 60'}),
            'major': forms.Select(attrs={'class': 'form-select'}),
            'has_kuwaiti_license': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_gpa(self):
        gpa = self.cleaned_data.get('gpa')
        if gpa is not None and gpa < 3.5:
            raise forms.ValidationError('GPA must be 3.5 or higher to qualify for parking.')
        return gpa

    def clean_has_kuwaiti_license(self):
        has_license = self.cleaned_data.get('has_kuwaiti_license')
        if not has_license:
            raise forms.ValidationError('You must have a Kuwaiti driver\'s license to apply for parking.')
        return has_license
