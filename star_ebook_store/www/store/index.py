import frappe


def get_context(context):
    context.ebooks = frappe.get_all(
        "eBook",
        fields = [
            "ebook_name",
            "cover_image",
            "format",
            "price",
            "route",
            "creation",
            "author.full_name as author_name",
        ],
        filters = {"is_published": True},
        order_by="creation desc"
    )

