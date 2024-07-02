from django.contrib import admin
from . models import Content, Incident, OHSLink, Update, Lawyer, Expert, Consultation

# Register your models here.
admin.site.register(Content)
admin.site.register(Expert)
admin.site.register(Incident)
admin.site.register(OHSLink)
admin.site.register(Update)
admin.site.register(Lawyer)
admin.site.register(Consultation)