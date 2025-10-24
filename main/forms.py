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
        fields = ['name', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University Name'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


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
            'english_proficiency_document',
            'transcript_document',
            'passport_copy',
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
            'english_proficiency_document': 'Proof of English proficiency (PDF upload)',
            'transcript_document': 'Official transcript (PDF upload)',
            'passport_copy': 'Passport copy (PDF/PNG/JPG upload)',
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
            'english_proficiency_document': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'transcript_document': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'passport_copy': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.png,.jpg,.jpeg'}),
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
