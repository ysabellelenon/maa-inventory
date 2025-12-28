from django.shortcuts import render
#
# Views for the MAA Inventory prototype UI.
#

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

    context = {
        "items": items,
    }

    return render(request, "maainventory/inventory.html", context)