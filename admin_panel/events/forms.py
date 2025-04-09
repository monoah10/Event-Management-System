from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date', 'max_attendees']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_attendees': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter username'
    }))
    password = forms.CharField(max_length=100, label="Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))
    role = forms.ChoiceField(choices=[
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('attendee', 'Attendee')
    ], widget=forms.Select(attrs={
        'class': 'form-control'
    }))


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter username'
    }))
    password = forms.CharField(max_length=100, label="Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))

