from django.shortcuts import render
from django.http import Http404
#
# Views for the MAA Inventory prototype UI.
#

# Sample suppliers data reused across suppliers and inventory views.
SUPPLIERS = [
    {"code": "SUP-001", "name": "Oman Printer", "category": "Packaging", "contact_person": "John Paul Bartolome", "phone": "+968 1234 5678", "email": "john@acme.example",
     "location": "Muscat, Oman",
     "products_supplied": [
        {"item_name": "Printed Labels", "price_per_unit": "0.05 OMR", "sku": "001"},
        {"item_name": "Corrugated Boxes", "price_per_unit": "0.50 OMR", "sku": "002"}
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
        {"item_name": "Plastic Bags", "price_per_unit": "0.02 OMR", "sku": "003"},
        {"item_name": "Paper Bags", "price_per_unit": "0.03 OMR", "sku": "004"}
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
        {"item_name": "12 oz Cup", "price_per_unit": "0.06 OMR", "sku": "005"},
        {"item_name": "16 oz Cup", "price_per_unit": "0.08 OMR", "sku": "006"}
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
        {"item_name": "Food Container Small", "price_per_unit": "0.30 OMR", "sku": "007"},
        {"item_name": "Food Container Large", "price_per_unit": "0.55 OMR", "sku": "008"}
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
        {"item_name": "Straw (with Logo)", "price_per_unit": "0.004 OMR", "sku": "009"},
        {"item_name": "Plain Straw", "price_per_unit": "0.002 OMR", "sku": "010"}
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
        {"code": "001", "name": "Burger Box Large", "desc": "For big burgers / meal sets", "initial_qty": "15,000", "remaining_qty": "9,200", "min_qty": "5,000", "status": "GOOD", "category": "Cups", "base_unit": "pcs"},
        {"code": "002", "name": "Barbeque Bag", "desc": "Large heavy-duty barbeque bags with reinforced handles — ideal for schools and bulk orders; grease-resistant lining for hot items.", "initial_qty": "2,550", "remaining_qty": "1,800", "min_qty": "500", "status": "GOOD", "category": "Bags", "base_unit": "pcs"},
        {"code": "003", "name": "Bucket", "desc": "Big buckets for 2-3 burgers", "initial_qty": "29,400", "remaining_qty": "18,000", "min_qty": "10,000", "status": "LOW", "category": "Containers", "base_unit": "pcs"},
        {"code": "004", "name": "Curve Fries Cup", "desc": "Fries cup", "initial_qty": "79,442", "remaining_qty": "62,700", "min_qty": "20,000", "status": "GOOD", "category": "Cups", "base_unit": "pcs"},
        {"code": "005", "name": "Sauce Bag", "desc": "Paper bags without handles", "initial_qty": "8,857", "remaining_qty": "6,000", "min_qty": "3,000", "status": "LOW", "category": "Packaging", "base_unit": "pcs"},
        {"code": "006", "name": "Straws", "desc": "Straws with Logo", "initial_qty": "610,000", "remaining_qty": "450,000", "min_qty": "200,000", "status": "GOOD", "category": "Straws", "base_unit": "pcs"},
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


def edit_item(request, code):
    """Render a simple edit page for a single inventory item (prototype).

    This mirrors the sample data used by `inventory()` and renders
    `maainventory/edit_item.html` with the selected item's fields.
    """
    # Recreate the same prototype items so we can look up by code.
    items = [
        {"code": "001", "name": "Burger Box Large", "desc": "For big burgers / meal sets", "initial_qty": "15,000", "remaining_qty": "9,200", "min_qty": "5,000", "status": "GOOD", "category": "Cups", "base_unit": "pcs"},
        {"code": "002", "name": "Barbeque Bag", "desc": "Large heavy-duty barbeque bags with reinforced handles — ideal for schools and bulk orders; grease-resistant lining for hot items.", "initial_qty": "2,550", "remaining_qty": "1,800", "min_qty": "500", "status": "GOOD", "category": "Bags", "base_unit": "pcs"},
        {"code": "003", "name": "Bucket", "desc": "Big buckets for 2-3 burgers", "initial_qty": "29,400", "remaining_qty": "18,000", "min_qty": "10,000", "status": "LOW", "category": "Containers", "base_unit": "pcs"},
        {"code": "004", "name": "Curve Fries Cup", "desc": "Fries cup", "initial_qty": "79,442", "remaining_qty": "62,700", "min_qty": "20,000", "status": "GOOD", "category": "Cups", "base_unit": "pcs"},
        {"code": "005", "name": "Sauce Bag", "desc": "Paper bags without handles", "initial_qty": "8,857", "remaining_qty": "6,000", "min_qty": "3,000", "status": "LOW", "category": "Packaging", "base_unit": "pcs"},
        {"code": "006", "name": "Straws", "desc": "Straws with Logo", "initial_qty": "610,000", "remaining_qty": "450,000", "min_qty": "200,000", "status": "GOOD", "category": "Straws", "base_unit": "pcs"},
    ]

    item_to_supplier_code = {
        "001": "SUP-003",
        "002": "SUP-002",
        "003": "SUP-004",
        "004": "SUP-003",
        "005": "SUP-002",
        "006": "SUP-005",
    }

    suppliers_by_code = {s["code"]: s["name"] for s in SUPPLIERS}

    # find the item by code
    selected_item = None
    for it in items:
        if it.get("code") == code:
            selected_item = dict(it)  # shallow copy to avoid mutating source
            supplier_code = item_to_supplier_code.get(code)
            selected_item["supplier"] = suppliers_by_code.get(supplier_code, "—") if supplier_code else "—"
            break

    if not selected_item:
        raise Http404("Item not found")
    # build a prototype list of suppliers for this item (primary + same-category matches)
    supplier_code_primary = item_to_supplier_code.get(code)
    item_suppliers = []
    for s in SUPPLIERS:
        include = False
        if s.get("code") == supplier_code_primary:
            include = True
        # include suppliers in the same category
        if not include and selected_item.get("category") and s.get("category") == selected_item.get("category"):
            include = True
        # fuzzy match: include if product names mention the item name tokens
        if not include:
            for p in s.get("products_supplied", []):
                pname = p.get("item_name", "").lower()
                for tok in selected_item.get("name", "").lower().split():
                    if tok and tok in pname:
                        include = True
                        break
                if include:
                    break

        if include:
            # find a sensible price for this item from the supplier's product list
            price = "—"
            for p in s.get("products_supplied", []):
                pname = p.get("item_name", "").lower()
                if selected_item.get("name", "").lower() in pname or pname in selected_item.get("name", "").lower():
                    price = p.get("price_per_unit", "—")
                    break
            if price == "—" and s.get("products_supplied"):
                price = s["products_supplied"][0].get("price_per_unit", "—")

            raw_available = s.get("supplier_hold", "—")
            # normalize supplier_hold: treat "No" (or variants) as 0 available
            if isinstance(raw_available, str) and raw_available.strip().lower().startswith("no"):
                available = "0"
            else:
                available = raw_available
            last = s.get("last_ordered_date", "—")
            status = "Active" if (isinstance(raw_available, str) and raw_available.strip().lower() in ("no", "")) else "On Hold"
            item_suppliers.append({
                "id": s.get("code"),
                "name": s.get("name"),
                "price_per_unit": price,
                "available": available,
                "last_purchase_date": last,
                "status": status,
            })

    context = {
        "item": selected_item,
        "item_suppliers": item_suppliers,
    }

    return render(request, "maainventory/edit_item.html", context)

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


def new_request(request):
    """Render a 'New Stock Request' page that uses the same edit-page styling.

    Provide sample inventory items and available locations so the UI can
    demonstrate filtering and adding items to a cart on the client side.
    """
    items = [
        {"code": "001", "name": "Burger Box Large", "initial_qty": "15,000", "remaining_qty": "9,200", "min_qty": "5,000", "status": "GOOD", "locations": ["Thoum Mabella - Kitchen", "Kucu Al Khoud"]},
        {"code": "002", "name": "Barbeque Bag", "initial_qty": "2,550", "remaining_qty": "1,800", "min_qty": "500", "status": "GOOD", "locations": ["Kucu Al Khoud", "Thoum Mabella - Kitchen"]},
        {"code": "003", "name": "Bucket", "initial_qty": "29,400", "remaining_qty": "18,000", "min_qty": "10,000", "status": "LOW", "locations": ["Thoum Mabella - Kitchen"]},
        {"code": "004", "name": "Curve Fries Cup", "initial_qty": "79,442", "remaining_qty": "62,700", "min_qty": "20,000", "status": "GOOD", "locations": ["Kucu Avenues Mall", "Kucu Al Khoud"]},
        {"code": "005", "name": "Sauce Bag", "initial_qty": "8,857", "remaining_qty": "6,000", "min_qty": "3,000", "status": "LOW", "locations": ["Thoum Mabella - Kitchen", "Kucu Avenues Mall"]},
        {"code": "006", "name": "Straws", "initial_qty": "610,000", "remaining_qty": "450,000", "min_qty": "200,000", "status": "GOOD", "locations": ["Kucu Al Khoud", "Kucu Avenues Mall"]},
    ]

    locations = [
        "Thoum Mabella - Kitchen",
        "Kucu Al Khoud",
        "Kucu Avenues Mall",
        "Boom Al Khoud",
    ]

    context = {
        "items": items,
        "locations": locations,
    }
    return render(request, "maainventory/new_request.html", context)


def edit_supplier(request, code):
    """Render a simple edit page for a single supplier (prototype).

    For now this reuses the same layout as the item edit page so the UI
    matches the edit item screen while supplier-specific fields are
    fleshed out later.
    """
    selected_supplier = None
    for s in SUPPLIERS:
        if s.get("code") == code:
            selected_supplier = dict(s)  # shallow copy
            break

    if not selected_supplier:
        raise Http404("Supplier not found")

    # reuse the same template layout as edit_item (but stored under a supplier-specific file)
    context = {
        "item": selected_supplier,
    }
    return render(request, "maainventory/edit_supplier.html", context)


def suppliers(request):
    """Render a prototype suppliers page (duplicate of requests for now)."""
    context = {
        "items": SUPPLIERS,
    }

    return render(request, "maainventory/suppliers.html", context)