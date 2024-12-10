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

def success_page (request):
    return render (request, 'payments/success.html')

def cancel_page (request):
    return render (request, 'payments/cancel.html')


def create_checkout_session (request):
    if request.method == 'POST':
        try:
            DOMAIN_NAME = 'https://usalamasmart.fly.dev/payments'
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': 'price_1QMQEoBViiraK7sOcPSVsFGA',
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=DOMAIN_NAME + '/success_url/',
                cancel_url=DOMAIN_NAME + '/cancel_url/',
            )

            return redirect(checkout_session.url, code=303)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponse("Method not allowed", status=405)

def webhook_endpoint (request):
    if request.method == 'POST':
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        request_data = json.loads(request.data)
        if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
            signature = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.data, sig_header=signature, secret=webhook_secret)
                data = event['data']
            except Exception as e:
                return e
            # Get the type of webhook event sent - used to check the status of PaymentIntents.
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']
        data_object = data['object']

        print('event ' + event_type)

    return HttpResponse('Accepted')
    
        # if event_type == 'checkout.session.completed':
        #     register_lawyer, created = Lawyer.objects.get_or_create(id=lawyer_id)
            
        #     register_lawyer.is_active = True
        #     register_lawyer.save()

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

