# Copyright (c) 2023, becky and contributors
# For license information, please see license.txt
from django.http import HttpResponse

# import frappe
from frappe.model.document import Document


class MpesaTransactions(Document):
	pass


def getAccessToken(request):
	return HttpResponse("Hello World")
