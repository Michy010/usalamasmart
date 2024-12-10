from django.shortcuts import render, redirect, get_object_or_404, redirect
from .forms import ContentForm, IncidentForm, OHSLinkForm, ConsultationForm, ExpertResponseForm, UpdateForm, LawyerSubscritionForm
from .models import Content, Incident, OHSLink, Update, Lawyer, Expert, Consultation
from django.utils.dateformat import DateFormat
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from django.core.files.storage import FileSystemStorage
import json


# Create your views here.
def index(request):
    form = LawyerSubscritionForm ()
    if request.method == 'POST':
        form = LawyerSubscritionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect ('usalama_smart:view_lawyers')
        else:
            form = LawyerSubscritionForm()
    return render(request, 'usalama_smart/index.html', {'form':form})

def about_us(request):
    return render(request, 'usalama_smart/about_us.html')

def details(request):
    return render(request, 'usalama_smart/details.html')

def content_create_view(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            
            if content.content_type == 'mixed':
                if not content.text or (not content.image and not content.video_url):
                    form.add_error(None, _("For 'Mixed' content type, provide text and either an image or video URL."))
                    return render(request, 'usalama_smart/content_form.html', {'form': form})
            
            content.save()
            return redirect('usalama_smart:content_list')
    else:
        form = ContentForm()
    
    return render(request, 'usalama_smart/content_form.html', {'form': form})

def content_list_view(request):
    contents = Content.objects.all()
    return render(request, 'usalama_smart/content_list.html', {'contents': contents})


def report_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            incident = form.save(commit=False)
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            incident.latitude = latitude if latitude else None
            incident.longitude = longitude if longitude else None
            
            if incident.is_anonymous:
                incident.reporter = None
            else:
                incident.reporter = request.user
            incident.save()
            if request.user.is_superuser:
                return redirect('usalama_smart:incidence_list')
            else:
                return redirect('usalama_smart:incidence_success')
    else:
        form = IncidentForm(user=request.user)
    return render(request, 'usalama_smart/report_incident.html',{'form':form})


def incident_list(request):
    incidents = Incident.objects.all()
    return render(request, 'usalama_smart/incident_list.html', {'incidents': incidents})

def incidence_success(request):
    return render(request, 'usalama_smart/incidence_success.html')


def ohs_link_list(request):
    links = OHSLink.objects.all()
    return render(request, 'usalama_smart/ohs_link_list.html', {'links': links})

def add_ohs_link(request):
    if request.method == 'POST':
        form = OHSLinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usalama_smart:ohs_link_list')
    else:
        form = OHSLinkForm()
    return render(request, 'usalama_smart/add_ohs_link.html', {'form': form})

def post_update(request):
    if request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.author = request.user
            update.save()
            return redirect('usalama_smart:all_updates')
    else:
        form = UpdateForm()
    return render(request, 'usalama_smart/post_update.html', {'form': form})

def all_updates(request):
    updates = Update.objects.all().order_by('-created_at') 
    return render(request, 'usalama_smart/all_updates.html', {'updates': updates})


def register_lawyer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        whatsapp_account = request.POST.get('whatsapp_account')
        mobile_phone = request.POST.get('mobile_phone')
        profile_picture = request.FILES.get('profile_picture')

        if profile_picture:
            fs = FileSystemStorage()
            filename = fs.save(profile_picture.name, profile_picture)
            profile_picture_url = fs.url(filename)
        else:
            profile_picture_url = None

        Lawyer.objects.create(
            name=name,
            email=email,
            whatsapp_account=whatsapp_account,
            mobile_phone=mobile_phone,
            profile_picture=profile_picture
        )
        return redirect('usalama_smart:view_lawyers') 
    return render(request, 'usalama_smart/register_lawyer.html')

def view_lawyers(request):
    lawyers = Lawyer.objects.all()
    return render(request, 'usalama_smart/view_lawyers.html', {'lawyers': lawyers})

SEVERITY_MAPPING = {
    'Low': 1,
    'Medium': 2,
    'High': 3
}

def incident_chart(request):
    incidents = Incident.objects.all().order_by('title') 
    labels = [incident.title for incident in incidents]
    data = [SEVERITY_MAPPING[incident.severity] for incident in incidents]

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
    return render(request, 'usalama_smart/incident_chart.html', context)


def expert_list(request):
    experts = Expert.objects.all()
    return render(request, 'usalama_smart/expert_list.html', {'experts': experts})

def expert_detail(request, pk):
    expert = get_object_or_404(Expert, pk=pk)
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.expert = expert
            consultation.user = request.user
            consultation.save()
            return redirect('usalama_smart:consultation_success')
    else:
        form = ConsultationForm()
    return render(request, 'usalama_smart/expert_detail.html', {'expert': expert, 'form': form})


def expert_dashboard(request, expert_id):
    expert = get_object_or_404(Expert, pk=expert_id)
    consultations = Consultation.objects.filter(expert=expert).order_by('consultation_date')

    if request.method == 'POST':
        consultation_id = request.POST.get('consultation_id')
        consultation = get_object_or_404(Consultation, id=consultation_id, expert=expert)
        form = ExpertResponseForm(request.POST, instance=consultation)
        
        if form.is_valid():
            form.save()

            if consultation.status == 'Accepted':
                message = {
                    'status': 'accepted',
                    'message': _("Your consultation with {expert_name} has been accepted. Please copy the link below and keep it safe").format(expert_name=expert.name),
                    'meet_link': consultation.meeting_link
                }
            else:
                message = {
                    'status': 'Declined',
                    'message': _("Your consultation with {expert_name} has been declined.").format(expert_name=expert.name),
                    'reason': consultation.decline_message
                }
            return JsonResponse(message)
            
    else:
        form = ExpertResponseForm()

    return render(request, 'usalama_smart/expert_dashboard.html', {'expert': expert, 'consultations': consultations, 'form': form})


@login_required
def consultation_success(request):
    return render(request, 'usalama_smart/consultation_success.html')

@login_required
def user_dashboard(request):
    consultations = Consultation.objects.filter(user=request.user).order_by('-consultation_date')
    return render(request, 'usalama_smart/user_dashboard.html', {'consultations': consultations})

def accept_consultation(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if consultation.status == 'Accepted':
        message = _("Your consultation with {expert_name} has been accepted.\nHere is your Google Meet link: {meet_link}\n").format(
            expert_name=consultation.expert.name, meet_link=consultation.meeting_link)
    else:
        message = _("Your consultation with {expert_name} has been declined.\nReason: {decline_message}\n").format(
            expert_name=consultation.expert.name, decline_message=consultation.decline_message)

    return redirect(reverse('usalama_smart:consultation_success', kwargs={'message': message}))


def set_language(request):
    user_language = request.GET.get('language', 'en')
    translation.activate(user_language)
    request.session[settings.LANGUAGE_SESSION_KEY] = user_language
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
