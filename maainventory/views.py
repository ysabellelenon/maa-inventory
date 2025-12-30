from django.shortcuts import render
#
# Views for the MAA Inventory prototype UI.
#

# Sample suppliers data reused across suppliers and inventory views.
SUPPLIERS = [
    {"code": "SUP-001", "name": "Oman Printer", "category": "Packaging", "contact_person": "John Paul Bartolome", "phone": "+968 1234 5678", "email": "john@acme.example",
     "location": "Muscat, Oman",
     "products_supplied": [
         {"item_name": "Printed Labels", "price_per_unit": "0.05 OMR"},
         {"item_name": "Corrugated Boxes", "price_per_unit": "0.50 OMR"}
     ],
     "delivery_lead_time": "3–5 days",
     "bank_name": "Bank Muscat",
     "bank_account_details": "Account Name: Oman Printer Co. — Acc # 12345678",
     "iban_number": "OM23BMUS123456789012345678",
     "last_ordered_date": "2025-12-10",
     "notes": "Prefers email orders; offers volume discount.",
     "total_spend": "OMR 15,845.42",
     "pending_invoices": "OMR 3,023.23",
     "pending_invoice_count": 3,
     "active_orders": 4,
     "supplier_hold": "1,000"
    },
    {"code": "SUP-002", "name": "Al-Madenah", "category": "Bags", "contact_person": "Nada Al-Daghari", "phone": "+968 2345 6789", "email": "nada@example.com",
     "location": "Sohar, Oman",
     "products_supplied": [
         {"item_name": "Plastic Bags", "price_per_unit": "0.02 OMR"},
         {"item_name": "Paper Bags", "price_per_unit": "0.03 OMR"}
     ],
     "delivery_lead_time": "2–4 days",
     "bank_name": "National Bank of Oman",
     "bank_account_details": "Account Name: Al-Madenah Supplies — Acc # 87654321",
     "iban_number": "OM45NBON876543210987654321",
     "last_ordered_date": "2025-11-28",
     "notes": "Fast turnaround for small orders.",
     "total_spend": "OMR 3,331.10",
     "pending_invoices": "OMR 1,200.00",
     "pending_invoice_count": 1,
     "active_orders": 2,
     "supplier_hold": "No"
    },
    {"code": "SUP-003", "name": "Excellent Packing", "category": "Cups", "contact_person": "Gloria Ysabelle Lenon", "phone": "+968 3456 7890", "email": "gloria@example.com",
     "location": "Muscat, Oman",
     "products_supplied": [
         {"item_name": "12 oz Cup", "price_per_unit": "0.06 OMR"},
         {"item_name": "16 oz Cup", "price_per_unit": "0.08 OMR"}
     ],
     "delivery_lead_time": "5–7 days",
     "bank_name": "HSBC Oman",
     "bank_account_details": "Account Name: Excellent Packing — Acc # 11223344",
     "iban_number": "OM67HSBC112233445566778899",
     "last_ordered_date": "2025-10-05",
     "notes": "Requires 50% advance for new customers.",
     "total_spend": "OMR 71,237.00",
     "pending_invoices": "OMR 5,000.00",
     "pending_invoice_count": 5,
     "active_orders": 7,
     "supplier_hold": "No"
    },
    {"code": "SUP-004", "name": "Al Andalus", "category": "Containers", "contact_person": "Ali Al-Ismaili", "phone": "+968 4567 8901", "email": "ali@example.com",
     "location": "Salalah, Oman",
     "products_supplied": [
         {"item_name": "Food Container Small", "price_per_unit": "0.30 OMR"},
         {"item_name": "Food Container Large", "price_per_unit": "0.55 OMR"}
     ],
     "delivery_lead_time": "7–10 days",
     "bank_name": "Muscat Securities",
     "bank_account_details": "Account Name: Al Andalus Trading — Acc # 33445566",
     "iban_number": "OM89MSCL334455667788990011",
     "last_ordered_date": "2025-12-01",
     "notes": "Seasonal delays possible during peak months.",
     "total_spend": "OMR 252,000.00",
     "pending_invoices": "OMR 12,000.00",
     "pending_invoice_count": 2,
     "active_orders": 3,
     "supplier_hold": "No"
    },
    {"code": "SUP-005", "name": "AL Khalijia Company for Converting Industries", "category": "Straws", "contact_person": "Omran Al-Ismaili", "phone": "+968 5678 9012", "email": "omran@example.com",
     "location": "Muscat, Oman",
     "products_supplied": [
         {"item_name": "Straw (with Logo)", "price_per_unit": "0.004 OMR"},
         {"item_name": "Plain Straw", "price_per_unit": "0.002 OMR"}
     ],
     "delivery_lead_time": "4–6 days",
     "bank_name": "Gulf Bank",
     "bank_account_details": "Account Name: Khalijia Co. — Acc # 55667788",
     "iban_number": "OM01GULF556677889900112233",
     "last_ordered_date": "2025-12-15",
     "notes": "Can print custom logos with 2-week lead time.",
     "total_spend": "OMR 90,000.00",
     "pending_invoices": "OMR 2,500.00",
     "pending_invoice_count": 4,
     "active_orders": 1,
     "supplier_hold": "Yes - Quality review"
    },
]

def dashboard(request):
    """Render a prototype dashboard page with sample data."""
    stats = [
        {"label": "Low Stock", "key": "stat-low-stock", "value": 10, "note": "Items"},
        {"label": "Total Stock", "key": "stat-total-stock", "value": 75, "note": "Items"},
        {"label": "Pending", "key": "stat-pending", "value": 5, "note": "Requests"},
        {"label": "In Progress", "key": "stat-in-progress", "value": 12, "note": "Requests"},
        {"label": "Foodics", "key": "stat-foodics", "value": 5, "note": "QTY"},
        {"label": "Talabat", "key": "stat-talabat", "value": 5, "note": "QTY"},
    ]

    most_requested = [
        {"name": "Burger Box", "amount": "71,237", "pct": "(26%)"},
        {"name": "Sandwich Paper", "amount": "54,713", "pct": "(20%)"},
        {"name": "Bucket (85 oz)", "amount": "40,111", "pct": "(15%)"},
        {"name": "Square Cup (12 oz)", "amount": "37,047", "pct": "(14%)"},
        {"name": "Straw (with Logo)", "amount": "17,006", "pct": "(9%)"},
        {"name": "Ice Cream Cup", "amount": "8,046", "pct": "(3%)"},
    ]
    # compute numeric bar width (percentage) from pct strings like "26%" or "(26%)"
    for item in most_requested:
        pct_raw = item.get("pct", "")
        digits = "".join(ch for ch in pct_raw if ch.isdigit())
        try:
            item["bar_width"] = int(digits)
        except ValueError:
            item["bar_width"] = 0
        # add a CSS-friendly class for common percentages (e.g., bar-26)
        item["bar_class"] = "bar-{}".format(item["bar_width"])

    branch_consumption = [
        {"name": "Kucu Sohar Gate", "amount": "252,000", "pct": "28%"},
        {"name": "Kucu Al Khoud", "amount": "216,000", "pct": "24%"},
        {"name": "Kucu Oman Mall", "amount": "144,000", "pct": "16%"},
        {"name": "Boom Al Khoud", "amount": "126,000", "pct": "14%"},
        {"name": "Kucu Sur", "amount": "90,000", "pct": "10%"},
        {"name": "Boom Nizwa", "amount": "72,000", "pct": "8%"},
    ]

    context = {
        "stats": stats,
        "most_requested": most_requested,
        "branch_consumption": branch_consumption,
    }

    # Use the app-relative template name so Django's app_directories loader can find it
    return render(request, "maainventory/dashboard.html", context)

def inventory(request):
    """Render a prototype inventory list page with sample data for the UI prototype."""
    items = [
        {"code": "001", "name": "Burger Box Large", "desc": "For big burgers / meal sets", "initial_qty": "15,000", "remaining_qty": "9,200", "min_qty": "5,000", "status": "GOOD"},
        {"code": "002", "name": "Barbeque Bag", "desc": "Large heavy-duty barbeque bags with reinforced handles — ideal for schools and bulk orders; grease-resistant lining for hot items.", "initial_qty": "2,550", "remaining_qty": "1,800", "min_qty": "500", "status": "GOOD"},
        {"code": "003", "name": "Bucket", "desc": "Big buckets for 2-3 burgers", "initial_qty": "29,400", "remaining_qty": "18,000", "min_qty": "10,000", "status": "LOW"},
        {"code": "004", "name": "Curve Fries Cup", "desc": "Fries cup", "initial_qty": "79,442", "remaining_qty": "62,700", "min_qty": "20,000", "status": "GOOD"},
        {"code": "005", "name": "Sauce Bag", "desc": "Paper bags without handles", "initial_qty": "8,857", "remaining_qty": "6,000", "min_qty": "3,000", "status": "LOW"},
        {"code": "006", "name": "Straws", "desc": "Straws with Logo", "initial_qty": "610,000", "remaining_qty": "450,000", "min_qty": "200,000", "status": "GOOD"},
    ]
    # Map inventory items to supplier codes (sample mapping for prototype)
    item_to_supplier_code = {
        "001": "SUP-003",  # Burger Box Large -> Excellent Packing (cups)
        "002": "SUP-002",  # Barbeque Bag -> Al-Madenah (bags)
        "003": "SUP-004",  # Bucket -> Al Andalus (containers)
        "004": "SUP-003",  # Curve Fries Cup -> Excellent Packing (cups)
        "005": "SUP-002",  # Sauce Bag -> Al-Madenah (bags)
        "006": "SUP-005",  # Straws -> AL Khalijia (straws)
    }

    suppliers_by_code = {s["code"]: s["name"] for s in SUPPLIERS}
    for item in items:
        code = item.get("code")
        supplier_code = item_to_supplier_code.get(code)
        item["supplier"] = suppliers_by_code.get(supplier_code, "—") if supplier_code else "—"

    context = {
        "items": items,
    }

    return render(request, "maainventory/inventory.html", context)

def requests(request):
    """Render a prototype requests page that mirrors the inventory UI for now."""
    items = [
        {"code": "001", "requestor": "John Paul Bartolome", "branch": "Kucu Al Maabela", "name": "Bucket", "requested_date": "12/25/2025", "status": "Pending"},
        {"code": "002", "requestor": "Nada Al-Daghari", "branch": "Boom Al Khoud", "name": "Barbecue Bag", "requested_date": "12/23/2025", "status": "Under Review"},
        {"code": "003", "requestor": "Gloria Ysabelle Lenon", "branch": "Thoum Sohar Gate", "name": "Burger Box Large", "requested_date": "12/18/2025", "status": "Approved"},
        {"code": "004", "requestor": "Ali Al-Ismaili", "branch": "Boom Sohar Gate", "name": "Barbecue Bag", "requested_date": "12/18/2025", "status": "Rejected"},
        {"code": "005", "requestor": "Omran Al-Ismaili", "branch": "Kucu Al Khuwair", "name": "Straws", "requested_date": "12/17/2025", "status": "In Process"},
        {"code": "006", "requestor": "Aliya Al-Haimli", "branch": "Kucu Avenues Mall", "name": "Curve Fries Cup", "requested_date": "12/12/2025", "status": "Out for Delivery"},
        {"code": "007", "requestor": "Aliya Al-Haimli", "branch": "Kucu Avenues Mall", "name": "Curve Fries Cup", "requested_date": "12/12/2025", "status": "Delivered"},
        {"code": "008", "requestor": "Aliya Al-Haimli", "branch": "Kucu Avenues Mall", "name": "Curve Fries Cup", "requested_date": "12/12/2025", "status": "Completed"},
    ]

    context = {
        "items": items,
    }

    return render(request, "maainventory/requests.html", context)


def suppliers(request):
    """Render a prototype suppliers page (duplicate of requests for now)."""
    context = {
        "items": SUPPLIERS,
    }

    return render(request, "maainventory/suppliers.html", context)