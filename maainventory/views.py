from django.shortcuts import render
#
# Views for the MAA Inventory prototype UI.
#

def dashboard(request):
    """Render a prototype dashboard page with sample data."""
    stats = [
        {"label": "Low Stock", "value": 10, "note": "Items"},
        {"label": "Total Stock", "value": 75, "note": "Items"},
        {"label": "Pending", "value": 5, "note": "Requests"},
        {"label": "In Progress", "value": 12, "note": "Requests"},
        {"label": "Foodics", "value": 5, "note": "QTY"},
        {"label": "Talabat", "value": 5, "note": "QTY"},
    ]

    most_requested = [
        {"name": "Burger Box", "amount": "71,237", "pct": "20%"},
        {"name": "Sandwich Paper", "amount": "54,713", "pct": "20%"},
        {"name": "Bucket (85 oz)", "amount": "40,111", "pct": "15%"},
        {"name": "Square Cup (12 oz)", "amount": "37,047", "pct": "14%"},
        {"name": "Straw (with Logo)", "amount": "17,006", "pct": "9%"},
        {"name": "Ice Cream Cup", "amount": "8,046", "pct": "3%"},
    ]

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
