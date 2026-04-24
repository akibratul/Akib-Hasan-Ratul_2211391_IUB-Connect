from django import forms
from .models import User, StudentProfile, AlumniProfile

DEPARTMENTS = ['CSE', 'BBA', 'EEE', 'ECO', 'ENG', 'PHY', 'MATH', 'SOC']


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'input-field input-icon-left', 'placeholder': 'you@iub.edu', 'id': 'login-email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input-field input-icon-left', 'placeholder': '••••••••', 'id': 'login-password'
    }))
    role = forms.ChoiceField(choices=[('student', 'Student'), ('alumni', 'Alumni'), ('admin', 'Admin')], initial='student')


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Your full name', 'id': 'register-name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'input-field', 'placeholder': 'you@iub.edu.bd', 'id': 'register-email'
    }))
    password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={
        'class': 'input-field', 'placeholder': 'Min 6 characters', 'id': 'register-password'
    }))
    role = forms.ChoiceField(choices=[('student', 'Student'), ('alumni', 'Alumni')], initial='student')
    # Student fields
    department = forms.ChoiceField(choices=[(d, d) for d in DEPARTMENTS], required=False, initial='CSE',
                                   widget=forms.Select(attrs={'class': 'input-field'}))
    year = forms.ChoiceField(choices=[(i, f'Year {i}') for i in range(1, 5)], required=False, initial=1,
                              widget=forms.Select(attrs={'class': 'input-field'}))
    skills = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Python, React, SQL...'
    }))
    interests = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'AI, Web Development...'
    }))
    # Alumni fields
    graduation_year = forms.IntegerField(required=False, initial=2020, widget=forms.NumberInput(attrs={
        'class': 'input-field', 'min': '1990', 'max': '2026'
    }))
    profession = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Software Engineer at Google...'
    }))


class ProfileForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input-field'}))
    # Student
    department = forms.ChoiceField(choices=[(d, d) for d in DEPARTMENTS], required=False,
                                   widget=forms.Select(attrs={'class': 'input-field'}))
    year = forms.ChoiceField(choices=[(i, f'Year {i}') for i in range(1, 5)], required=False,
                              widget=forms.Select(attrs={'class': 'input-field'}))
    skills = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Python, React, SQL...'
    }))
    interests = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'AI, Web Dev...'
    }))
    # Alumni
    graduation_year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'input-field'}))
    profession = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Software Engineer at...'
    }))


class JobForm(forms.Form):
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Software Engineer Intern'
    }))
    company = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Google'
    }))
    job_type = forms.ChoiceField(choices=[('job', 'Job'), ('internship', 'Internship')], initial='job', widget=forms.Select(attrs={
        'class': 'input-field'
    }))
    deadline = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={
        'class': 'input-field', 'type': 'datetime-local'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'input-field', 'rows': 3, 'placeholder': 'Job description...'
    }))
    skills_required = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'input-field', 'placeholder': 'Python, React, SQL...'
    }))


class ApplicationForm(forms.Form):
    cv = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'input-field', 'accept': 'application/pdf'
    }))
    cover_letter = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'input-field', 'rows': 4, 'placeholder': 'Why are you a good fit?'
    }))
