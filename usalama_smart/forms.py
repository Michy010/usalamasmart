from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Content, Incident, OHSLink, Consultation, Update, Lawyer, Expert

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'content_type', 'text', 'image', 'video_url']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': _('Enter text here...')}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'video_url': forms.URLInput(attrs={'placeholder': _('Enter video URL...')}),
        }

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['company', 'located', 'title', 'description', 'severity', 'reporter', 'image', 'is_anonymous']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'is_anonymous': _('Report Anonymously'),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(IncidentForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['reporter'].queryset = self.fields['reporter'].queryset.filter(id=self.user.id)
            self.fields['reporter'].initial = self.user
            self.fields['reporter'].widget.attrs['readonly'] = True

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

class ExpertForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ['user', 'name', 'email', 'bio', 'specialization', 'profile_picture']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['user'].widget.attrs['readonly'] = True  
        self.fields['profile_picture'].required = False  

class ExpertResponseForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['status', 'meeting_link', 'decline_message']
        widgets = {
            'status': forms.RadioSelect(choices=[('Accepted', _('Accept')), ('Declined', _('Decline'))]),
            'meeting_link': forms.URLInput(attrs={'placeholder': _('Google Meet link')}),
            'decline_message': forms.Textarea(attrs={'placeholder': _('Reason for decline')}),
        }

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ['title', 'content', 'image', 'video_url']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': _('Enter text here...'), 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'video_url': forms.URLInput(attrs={'placeholder': _('Enter video URL...')}),
        }

class LawyerSubscritionForm (forms.ModelForm):
    class Meta:
        model = Lawyer
        fields = ['name', 'email', 'whatsapp_account', 'mobile_phone', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={
                'class':'form-field',
                'style':'width:200px;'
            }),
            'email': forms.EmailInput(attrs={
                'class':'form-field',
                'style':'width:200px'
            }),
            'whatsapp_account': forms.TextInput(attrs={
                'class':'form-field',
                'style':'width:200px'
            })
        }