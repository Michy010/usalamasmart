from django import forms
from .models import Content, Incident, OHSLink,Consultation

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'content_type', 'text', 'image', 'video_url']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Enter text here...'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'Enter video URL...'}),
        }


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'severity', 'reporter', 'image', 'is_anonymous']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'is_anonymous': 'Report Anonymously',
        }


class OHSLinkForm(forms.ModelForm):
    class Meta:
        model = OHSLink
        fields = ['title', 'url', 'description']


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['user_name', 'consultation_date', 'message']
        widgets = {
            'consultation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ExpertResponseForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['status', 'meeting_link', 'decline_message']
        widgets = {
            'status': forms.RadioSelect(choices=[('Accepted', 'Accept'), ('Declined', 'Decline')]),
            'meeting_link': forms.URLInput(attrs={'placeholder': 'Google Meet link'}),
            'decline_message': forms.Textarea(attrs={'placeholder': 'Reason for decline'}),
        }
