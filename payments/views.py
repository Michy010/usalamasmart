from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from usalama_smart.models import Lawyer
# from .utils import webhook_received
from django.conf import settings
# from .utils import get_session_token
from django.views.decorators.csrf import csrf_exempt
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import stripe
import requests

# Mpesa dependencies
# from portalsdk import APIContext, APIMethodType, APIRequest
# from time import sleep
# import time

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def payments_page(request):
    return render (request, 'payments/lawyer_subscription.html')

def create_checkout_session(request):
    user = request.user
    if request.method == 'GET':
        try:
            DOMAIN_NAME = 'https://usalamasmart.fly.dev'
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': 'price_1QMQEoBViiraK7sOcPSVsFGA',
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=f"{DOMAIN_NAME}/payments/success_url/",
                cancel_url=f"{DOMAIN_NAME}/payments/cancel_url/",
            )
            
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponse("Method not allowed", status=405)


def success_page(request):
    # Retrieve lawyer data from session
    lawyer_data = request.session.get('lawyer_data', None)
    if lawyer_data:
        # Save lawyer to the database
        Lawyer.objects.create(
            name=lawyer_data['name'],
            email=lawyer_data['email'],
            whatsapp_account=lawyer_data['whatsapp_account'],
            mobile_phone=lawyer_data['mobile_phone'],
            profile_picture=lawyer_data.get('profile_picture_path', None)
        )
        # Clear session data
        del request.session['lawyer_data']
    return render(request, 'payments/success.html')


def cancel_page(request):
    # Redirect to a cancel page or show a cancellation message
    return render(request, 'payments/cancel.html')


def webhook_endpoint(request):
    if request.method == 'POST':
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        payload = request.body
        sig_header = request.headers.get('Stripe-Signature', None)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        # Handle the event type
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print(f"Payment succeeded for session: {session.id}")

        return HttpResponse(status=200)

    return HttpResponse("Method not allowed", status=405)



# def encrypt_api_key(api_key, public_key):
#     """Encrypt the API key using the provided public key."""
#     # Ensure the public key is in PEM format
#     formatted_public_key = (
#         "-----BEGIN PUBLIC KEY-----\n"
#         + public_key +
#         "\n-----END PUBLIC KEY-----"
#     )
    
#     rsa_key = RSA.importKey(formatted_public_key)
#     cipher = PKCS1_v1_5.new(rsa_key)
#     encrypted_key = base64.b64encode(cipher.encrypt(api_key.encode('utf-8')))
#     return encrypted_key.decode('utf-8')

# def get_session_key(request):
#     public_key = settings.PUBLIC_KEY  # Replace with the public key provided by the API documentation
#     api_key = settings.API_KEY      # Replace with your API key

#     # Encrypt the API key using the provided public key
#     encrypted_api_key = encrypt_api_key(api_key, public_key)

#     # Create API context
#     api_context = APIContext()
#     api_context.api_key = api_key
#     api_context.public_key = public_key
#     api_context.ssl = True
#     api_context.method_type = APIMethodType.GET
#     api_context.address = 'openapi.m-pesa.com'
#     api_context.port = 443
#     api_context.path = '/sandbox/ipg/v2/vodacomTZN/getSession/'  # Adjust for your market (e.g., vodacomTZN for Tanzania)

#     # Add headers
#     api_context.add_header('Authorization', f'Bearer {encrypted_api_key}')
#     api_context.add_header('Origin', '127.0.0.1')
#     api_context.add_header('Content-Type', 'application/json')

#     # Create API request
#     api_request = APIRequest(api_context)

#     try:
#         result = api_request.execute()
        
#         # Log or print the headers to see if they are in the expected format
#         print("Response Headers:", result.headers)
        
#         # Make sure headers are properly serialized to JSON-compatible format
#         headers_dict = {key: value for key, value in result.headers.items()}

#         return JsonResponse({
#             "status_code": result.status_code,
#             "headers": headers_dict,  # Ensure headers are serializable to JSON
#             "body": result.body,
#         })
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# def initiate_payments(request):
#     if request.method == 'POST':
#         try:
#             # Fetch session token
#             session_token = get_session_token()

#             # API parameters
#             endpoint_url = 'https://openapi.m-pesa.com/sandbox/ipg/v2/vodacomTZN/c2bPayment/singleStage/'
#             payload = {
#                 "input_Amount": "1",
#                 "input_Country": "TZN",
#                 "input_Currency": "TZS",
#                 "input_CustomerMSISDN": "000000000001",
#                 "input_ServiceProviderCode": "000000",
#                 "input_ThirdPartyConversationID": "asv02e5958774f7ba228d83d0d689761",
#                 "input_TransactionReference": "T1234C",
#                 "input_PurchasedItemsDesc": "Lawyer Subscription"
#             }

#             headers = {
#                 'Authorization': f'Bearer {session_token}',
#                 'Content-Type': 'application/json',
#                 'Origin': '*'
#             }

#             response = requests.post(endpoint_url, json=payload, headers=headers)
#             response.raise_for_status()  # Raise HTTP errors

#             data = response.json()
#             result = data.get('output_ResponseDesc', 'Payment initiated successfully.')

#             return JsonResponse({'status': result}, status=200)

#         except requests.RequestException as req_err:
#             return JsonResponse({'error': f"Network error: {req_err}"}, status=500)
#         except Exception as e:
#             return JsonResponse({'error': f"Unexpected error: {e}"}, status=500)

