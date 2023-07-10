import frappe
from frappe.website.utils import cleanup_page_name

def execute():
    # Fetch all the book records
    ebooks = frappe.get_all("eBook", pluck="name")

    for ebook_name in ebooks:
        # Update and set the route
        updated_route = f"store/ebook/{cleanup_page_name(ebook_name)}"

        frappe.db.set_value("eBook", ebook_name, "route", updated_route)