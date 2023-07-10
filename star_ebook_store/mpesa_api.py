import frappe
import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from frappe import _


class MpesaCredential:
    consumer_key = "KlGMNky0GXQTDlCfFImLO7U0CpVXPylH"
    consumer_secret = "YU5bVCI9fsPKnHnk"
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'


class MpesaAccessToken:
    r = requests.get(MpesaCredential.api_URL,
                     auth=HTTPBasicAuth(MpesaCredential.consumer_key, MpesaCredential.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']


import base64
from django.http import HttpResponse
import requests
from datetime import datetime
from .mpesa_api import MpesaAccessToken


def lipa_na_mpesa_online():
    access_token = MpesaAccessToken.validated_mpesa_access_token
    print(access_token)
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}

    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "174379"
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
    request = {
        "BusinessShortCode": Business_short_code,
        "Password": decode_password,
        "Timestamp": lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": 254759669534,
        "PartyB": Business_short_code,
        "PhoneNumber": 254759669534,
        "CallBackURL": "https://rebecca.free.beeceptor.com",
        "AccountReference": "Payment",
        "TransactionDesc": "Testing stk push"
    }
    response = requests.post(api_url, json=request, headers=headers)

    # Process the payment response and update the status accordingly
    if response.ok:
        status = 'completed'
    else:
        status = 'failed'

    return {
        'status': status
    }


@frappe.whitelist(allow_guest=True)
def process_mpesa_payment(ebook_name):
    result = lipa_na_mpesa_online()

    # Save the payment status in the M-Pesa transaction document
    doc = frappe.get_doc({
        'doctype': 'Mpesa Transactions',
        'ebook_name': ebook_name,
        'status': result['status']
    })
    doc.insert(ignore_permissions=True)

    return {
        'status': result['status']
    }


@frappe.whitelist()
def get_ebook_payment_status(ebook_name):
    # Fetch the payment status from the Mpesa transaction document
    doc = frappe.get_doc('Mpesa Transactions', {'ebook_name': ebook_name})
    status = doc.status

    return {
        'status': status
    }
