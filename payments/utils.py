import base64
import json
import stripe
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def get_encrypted_api_key(public_key_base64: str, api_key: str) -> str:
    """
    Encrypts the given API key using the provided Base64-encoded public key.

    Args:
        public_key_base64 (str): The Base64-encoded RSA public key.
        api_key (str): The API key to encrypt.

    Returns:
        str: The encrypted API key as a Base64-encoded string.
    """
    # Decode the Base64 public key
    decoded_key = base64.b64decode(public_key_base64)

    # Load the public key
    public_key = serialization.load_der_public_key(decoded_key, backend=default_backend())

    # Encrypt the API key
    encrypted_api_key = public_key.encrypt(
        api_key.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Return the encrypted API key as a Base64 string
    return base64.b64encode(encrypted_api_key).decode()


def get_session_token() -> str:
    try:
        api_url = 'https://openapi.m-pesa.com/sandbox/ipg/v2/vodacomTZN/getSession/'
        public_key = 'MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArv9yxA69XQKBo24BaF/D+fvlqmGdYjqLQ5WtNBb5tquqGvAvG3WMFETVUSow/LizQalxj2ElMVrUmzu5mGGkxK08bWEXF7a1DEvtVJs6nppIlFJc2SnrU14AOrIrB28ogm58JjAl5BOQawOXD5dfSk7MaAA82pVHoIqEu0FxA8BOKU+RGTihRU+ptw1j4bsAJYiPbSX6i71gfPvwHPYamM0bfI4CmlsUUR3KvCG24rB6FNPcRBhM3jDuv8ae2kC33w9hEq8qNB55uw51vK7hyXoAa+U7IqP1y6nBdlN25gkxEA8yrsl1678cspeXr+3ciRyqoRgj9RD/ONbJhhxFvt1cLBh+qwK2eqISfBb06eRnNeC71oBokDm3zyCnkOtMDGl7IvnMfZfEPFCfg5QgJVk1msPpRvQxmEsrX9MQRyFVzgy2CWNIb7c+jPapyrNwoUbANlN8adU1m6yOuoX7F49x+OjiG2se0EJ6nafeKUXw/+hiJZvELUYgzKUtMAZVTNZfT8jjb58j8GVtuS+6TM2AutbejaCV84ZK58E2CRJqhmjQibEUO6KPdD7oTlEkFy52Y1uOOBXgYpqMzufNPmfdqqqSM4dU70PO8ogyKGiLAIxCetMjjm6FCMEA3Kc8K0Ig7/XtFm9By6VxTJK1Mg36TlHaZKP6VzVLXMtesJECAwEAAQ=='
        api_key = 'VciypQyLBi2BoZqOlhe1THuCTXXmqRIf'

        # Encrypt API Key
        encrypted_APIKey = get_encrypted_api_key(public_key, api_key)

        # Debug: Log the encrypted key
        print(f"Encrypted API Key: {encrypted_APIKey}")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {encrypted_APIKey}',
            'Origin': '127.0.0.1'
        }

        # Debug: Log headers
        print(f"Request Headers: {headers}")

        response = requests.get(api_url, headers=headers)

        # Debug: Log response details
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        response.raise_for_status()  # Raise HTTP errors

        result = response.json()
        session_id = result.get('output_SessionID')

        if not session_id:
            raise ValueError("Session ID not found in the response.")

        return session_id

    except requests.RequestException as req_err:
        raise RuntimeError(f"Network error: {req_err}")
    except ValueError as val_err:
        raise RuntimeError(f"Response error: {val_err}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")


# @app.route('/webhook', methods=['POST'])
def webhook_received(request):
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    webhook_secret = 'whsec_E9O9XNV16RQgI0DyHzpXDq13eL7rkzrg'
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

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        print('Subscription canceled: %s', event.id)
    elif event_type == 'entitlements.active_entitlement_summary.updated':
        # handle active entitlement summary updated
        print('Active entitlement summary updated: %s', event.id)

    return HttpResponse ('success')