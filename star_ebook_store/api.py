import frappe
import razorpay

from frappe.utils.password import get_decrypted_password

@frappe.whitelist(allow_guest=True)
def create_ebook_order(ebook_name):
    # Fetch price of this ebook
    ebook_price_inr = frappe.db.get_value("eBook", ebook_name, "price")

    # Create Razorpay Order
    order_data = {"amount": ebook_price_inr * 100, "currency": "KES"}  # convert to paisa
    client = get_razorpay_client()
    razorpay_order = client.order.create(data=order_data)

    #// Create and insert new ebook order document
    frappe.get_doc(
        {
            "doctype": "eBook Order",
            "ebook": ebook_name,
            "razorpay_order_id": razorpay_order["id"],
            "order_amount": ebook_price_inr,
        }
    ).insert(ignore_permissions=True)

    return {
        "key_id": client.auth[0],
        "order_id": razorpay_order["id"],
    } # will be used in client side


def get_razorpay_client():
    key_id = frappe.db.get_single_value("Store Razorpay Settings", "key_id")
    key_secret = get_decrypted_password(
        "Store Razorpay Settings", "Store Razorpay Settings", "key_secret"
    )

    # create razorpay client and return
    return razorpay.Client(auth=(key_id, key_secret))


@frappe.whitelist(allow_guest=True)
def handle_razorpay_webhook():
    form_dict = frappe.local.form_dict
    payload = frappe.request.get_data()

    verify_webhook_signature(payload)  # for security purposes

    # Get payment details (check Razorpay docs for object structure)
    payment_entity = form_dict["payload"]["payment"]["entity"]
    razorpay_order_id = payment_entity["order_id"]
    razorpay_payment_id = payment_entity["id"]
    customer_email = payment_entity["email"]
    event = form_dict.get("event")

    # Process the order
    ebook_order = frappe.get_doc("eBook Order", {"razorpay_order_id": razorpay_order_id})
    if event == "payment.captured" and ebook_order.status != "Paid":
        ebook_order.update(
            {
                "razorpay_payment_id": razorpay_payment_id,
                "status": "Paid",
                "customer_email": customer_email,
            }
        ) # Mark as paid and set payment_id and customer_email
        ebook_order.save(ignore_permissions=True)


def verify_webhook_signature(payload):
    signature = frappe.get_request_header("X-Razorpay-Signature")
    webhook_secret = get_decrypted_password(
        "Store Razorpay Settings", "Store Razorpay Settings", "webhook_secret"
    )

    client = get_razorpay_client()
    client.utility.verify_webhook_signature(payload.decode(), signature, webhook_secret)




import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

class MpesaCredential:
    consumer_key = "isA83IKjvcjeOuzGeTLocVTATJs3VU8A"
    consumer_secret = "aSfoLCuNWsBAVPkV"
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
from . api import MpesaAccessToken #imports the file


@frappe.whitelist()
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
        "PartyA": 254759669534,  # replace with your phone number to get stk push
        "PartyB": Business_short_code,
        "PhoneNumber": 254759669534,  # replace with your phone number to get stk push
        "CallBackURL": "https://wishful.free.beeceptor.com",
        "AccountReference": "Payment",
        "TransactionDesc": "Testing stk push"
    }

    response = requests.post(api_url, json=request, headers=headers)
    print("hello")
    print(response)

    # Create the Frappe response
    frappe.response['http_status_code'] = response.status_code
    frappe.response['message'] = 'success'

    return frappe.response


lipa_na_mpesa_online()
