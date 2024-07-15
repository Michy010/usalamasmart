from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usalama_smart'

urlpatterns = [
    path('', views.index, name='home'),
    path('details/', views.details, name='details'),
    path('about/', views.about_us, name='about_us'),
    path('create/', views.content_create_view, name='content_create'),
    path('content_list/', views.content_list_view, name='content_list'),
    path('report_incidence/', views.report_incident, name='report_incidence'),
    path('incidence_list/', views.incident_list, name='incidence_list'),
    path('ohs_link_list/', views.ohs_link_list, name='ohs_link_list'),
    path('add_ohs_link/', views.add_ohs_link, name='add_ohs_link'),
    path('post_update/', views.post_update, name='post_update'),
    path('all_updates/', views.all_updates, name='all_updates'),
    path('register_lawyer/', views.register_lawyer, name='register_lawyer'),
    path('view_lawyers/', views.view_lawyers, name='view_lawyers'),
    path('incident-chart/', views.incident_chart, name='incident-chart'),
    path('expert_list/', views.expert_list, name='expert_list'),
    path('expert/<int:pk>/', views.expert_detail, name='expert_detail'),
    path('expert/<int:expert_id>/dashboard/', views.expert_dashboard, name='expert_dashboard'),
    path('success/', views.consultation_success, name='consultation_success'),
    path('my-consultations/', views.user_dashboard, name='user_dashboard'),
    path('consultation/accept/<int:consultation_id>/', views.accept_consultation, name='accept_consultation'),
    path('incidence_success/', views.incidence_success, name='incidence_success'),
    path('logout/', auth_views.LogoutView.as_view(), name= 'logout'),
    path('set_language/', views.set_language, name='set_language'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='usalama_smart/change_password.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='usalama_smart/password_change_done.html'), name='password_change_done'),
]