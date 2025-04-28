from django.shortcuts import render, redirect, get_object_or_404, redirect
from .forms import ContentForm, IncidentForm, OHSLinkForm, ConsultationForm, ExpertResponseForm, UpdateForm, LawyerSubscritionForm, ExpertForm
from .models import Content, Incident, OHSLink, Update, Lawyer, Expert, Consultation
from django.utils.dateformat import DateFormat
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
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

def contentManagement(request):
    return render (request, 'usalama_smart/content_management.html')

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
        # Temporarily store lawyer's data in session
        request.session['lawyer_data'] = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'whatsapp_account': request.POST.get('whatsapp_account'),
            'mobile_phone': request.POST.get('mobile_phone'),
            'profile_picture': request.FILES.get('profile_picture').name if 'profile_picture' in request.FILES else None,
        }

        # Handle profile picture upload if present
        if 'profile_picture' in request.FILES:
            fs = FileSystemStorage()
            filename = fs.save(request.FILES['profile_picture'].name, request.FILES['profile_picture'])
            request.session['lawyer_data']['profile_picture_path'] = fs.url(filename)

        # Redirect to the payments app for subscription
        return redirect('payments:checkout_session')

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

from django.shortcuts import render, redirect
from .forms import ExpertForm

def create_expert(request):
    if request.method == 'POST':
        form = ExpertForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the expert but do not commit to the database yet
            expert = form.save(commit=False)
            expert.user = request.user  
            expert.save()  
            return redirect('usalama_smart:expert_list')  
    else:
        form = ExpertForm()  

    return render(request, 'usalama_smart/content_management_system.html', {'form': form})



def expert_list(request):
    experts = Expert.objects.all()
    return render(request, 'usalama_smart/expert_list.html', {'experts': experts})

def expert_detail(request, pk):
    expert = get_object_or_404(Expert, pk=pk)
    client_name = request.user.username
    expert_name = expert.name
    expert_email = expert.email
    platform_link = f'https://usalamasmart.fly.dev/expert/'
    subject = 'You have New Consultation From Usalama Smart'
    html_content = render_to_string('usalama_smart/expert_booking_email.html', {
            'expert_name':expert_name,
            'client_name':client_name,
            'platform_link':platform_link,
        })

    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        current_user = request.user.username
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.expert = expert
            consultation.user = request.user
            username_cookie = request.COOKIES.get('username', 'Guest')
            if username_cookie != current_user:
                response = redirect('payments:checkout_session')
                response.set_cookie('username', current_user, max_age=7*24*60*60)
                return response
            else:
                consultation.save()


            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[expert_email]
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('usalama_smart:consultation_success')
    else:
        form = ConsultationForm()
    return render(request, 'usalama_smart/expert_detail.html', {'expert': expert, 'form': form})


def expert_dashboard(request, expert_id):
    expert = get_object_or_404(Expert, pk=expert_id)
    if request.user != expert.user:  
        if not request.user.is_staff:  
            return HttpResponseForbidden("You are not authorized to access this dashboard.")
            
    consultations = Consultation.objects.filter(expert=expert).order_by('consultation_date')
    if request.method == 'POST':
        consultation_id = request.POST.get('consultation_id')
        consultation = get_object_or_404(Consultation, id=consultation_id, expert=expert)
        receiver_email = request.user.email
        form = ExpertResponseForm(request.POST, instance=consultation)
        
        if form.is_valid():
            form.save()

            if consultation.status == 'Accepted':
                subject = 'Your Consultation  Accepted'
                message = {
                    'status': 'accepted',
                    'message': _("Your consultation with {expert_name} has been accepted. Please copy the link below and keep it safe").format(expert_name=expert.name),
                    'meet_link': consultation.meeting_link
                }
                email_body = f"Status: {message['status']}\nMessage: {message['message']}\nMeeting Link: {message['meet_link']}"

                send_mail (
                    subject=subject, message=email_body, from_email=settings.EMAIL_HOST_USER, recipient_list=[receiver_email], fail_silently=False
                )
            else:
                subject = 'Your Consultation Declined'
                message = {
                    'status': 'Declined',
                    'message': _("Your consultation with {expert_name} has been declined.").format(expert_name=expert.name),
                    'reason': consultation.decline_message
                }
                email_declined_body = f"Status: {message['status']}\nMessage: {message['message']}\nReason: {message['reason']}"
                send_mail (
                    subject=subject, message=email_declined_body, from_email=settings.EMAIL_HOST_USER, recipient_list=[receiver_email], fail_silently=False
                )
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
