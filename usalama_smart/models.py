from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Content(models.Model):
    CONTENT_TYPES = (
        ('text', _('Text')),
        ('image', _('Image')),
        ('video', _('Video')),
        ('mixed', _('Mixed')),
    )
    
    title = models.CharField(max_length=255, default='Title')
    content_type = models.CharField(max_length=5, choices=CONTENT_TYPES, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title

    

class Incident(models.Model):
    INCIDENT_SEVERITY = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    company = models.CharField(max_length=255, default='Not Provided')
    located = models.CharField(max_length=255, default='Not Provided')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=10, choices=INCIDENT_SEVERITY)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='incident_images/', blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


    def __str__(self):
        return self.title
    

class OHSLink(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Update(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='updates/images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Lawyer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    whatsapp_account = models.CharField(max_length=20)
    mobile_phone = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='lawyer_profiles/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Expert(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    bio = models.TextField()
    specialization = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class Consultation(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_name = models.CharField(max_length=100)
    consultation_date = models.DateTimeField()
    message = models.TextField()
    status = models.CharField(max_length=20, default='Pending')
    meeting_link = models.URLField(blank=True, null=True)
    decline_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Consultation with {self.user_name} on {self.consultation_date}"
