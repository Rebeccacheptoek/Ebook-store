# Copyright (c) 2023, becky and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class eBookOrder(Document):
    def on_update(self):
        if self.status == "Paid":
            self.deliver_ebook()


    def deliver_ebook(self):
        ebook_doc = frappe.get_doc("eBook", self.ebook)

        try:
            ebook_doc.send_via_email(self.customer_email)
            self.status = "Delivered"
        except:
            ebook_doc.log_error("Ebook Delivery Error")
