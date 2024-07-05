from django.shortcuts import render, redirect, get_object_or_404, redirect
from .forms import ContentForm, IncidentForm, OHSLinkForm, ConsultationForm, ExpertResponseForm
from .models import Content, Incident, OHSLink, Update, Lawyer, Expert, Consultation
from django.utils.dateformat import DateFormat
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
import json


# Create your views here.
def index (request):
    return render (request, 'usalama_smart/index.html')

def details (request):
    return render (request, 'usalama_smart/details.html')

def content_create_view(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('usalama_smart:content_list')
    else:
        form = ContentForm()
    return render(request, 'usalama_smart/content_form.html', {'form': form})

def content_list_view(request):
    contents = Content.objects.all()
    return render(request, 'usalama_smart/content_list.html', {'contents': contents})


def report_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST, request.FILES)
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
        form = IncidentForm()
    return render(request, 'usalama_smart/report_incident.html', {'form': form})


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
        title = request.POST.get('title')
        content = request.POST.get('content')
        update = Update(title=title, content=content, author=request.user)
        update.save()
        return redirect('usalama_smart:all_updates')
    return render(request, 'usalama_smart/post_update.html')

def all_updates(request):
    updates = Update.objects.all().order_by('-created_at') 
    return render(request, 'usalama_smart/all_updates.html', {'updates': updates})


def register_lawyer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        whatsapp_account = request.POST.get('whatsapp_account')
        mobile_phone = request.POST.get('mobile_phone')
        Lawyer.objects.create(
            name=name,
            email=email,
            whatsapp_account=whatsapp_account,
            mobile_phone=mobile_phone
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
                    'status':'accepted',
                    'message':f"Your consultation {expert.name} has been accepted. Please copy the link below and keep it safe",
                    'meet_link': consultation.meeting_link
                }
            else:
                message = {
                    "status": "Declined",
                    "message": f"Your consultation {expert.name} has been declined.",
                    "reason": consultation.decline_message
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
        message = f"Your consultation with {consultation.expert.name} has been accepted.\n"
        message += f"Here is your Google Meet link: {consultation.meeting_link}\n"
    else:
        message = f"Your consultation with {consultation.expert.name} has been declined.\n"
        message += f"Reason: {consultation.decline_message}\n"

    return redirect(reverse('usalama_smart:consultation_success', kwargs={'message': message}))


# @login_required
# def logout_page (request):
#     logout (request)
#     return redirect ('/')



