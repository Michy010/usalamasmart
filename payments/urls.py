from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('', views.payments_page, name='payment'),
    path('create-checkout-session/', views.create_checkout_session, name='checkout_session'),
    path('success_url/', views.success_page, name='successful'),
    path('cancel_url/', views.cancel_page, name='canceled'),
    path('webhook/', views.webhook_endpoint, name='webhook_endpoint'),
    # path('get-session/', views.get_session_key, name='get_session'),
    # path('payment-initiation/', views.initiate_payments, name='paymentInitiation')
]