# Item Request Views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from decimal import Decimal


@login_required
def api_suppliers_for_branch(request):
    """API endpoint to get suppliers for a branch"""
    from .models import Supplier, SupplierItem
    
    # Check if user is warehouse staff - deny access
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role.name if user_profile and user_profile.role else None
    if user_role and 'Warehouse' in user_role:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    branch_id = request.GET.get('branch_id')
    if not branch_id:
        return JsonResponse({'suppliers': []})
    
    try:
        # Get suppliers that have items for this specific branch only
        suppliers = Supplier.objects.filter(
            is_active=True,
            supplier_items__item__branches__id=branch_id
        ).distinct().values('id', 'name', 'category__name')
        
        suppliers_list = []
        for supplier in suppliers:
            suppliers_list.append({
                'id': supplier['id'],
                'name': supplier['name'],
                'category': supplier['category__name'] or 'No category'
            })
        
        return JsonResponse({'suppliers': suppliers_list})
    except Exception as e:
        print(f"Error loading suppliers: {str(e)}")
        return JsonResponse({'suppliers': [], 'error': str(e)}, status=500)


@login_required
def api_items_for_supplier(request):
    """API endpoint to get items for a supplier, filtered by branch"""
    from .models import SupplierItem, SupplierStock
    from django.db.models import Sum, Q
    
    # Check if user is warehouse staff - deny access
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role.name if user_profile and user_profile.role else None
    if user_role and 'Warehouse' in user_role:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    supplier_id = request.GET.get('supplier_id')
    branch_id = request.GET.get('branch_id')
    
    if not supplier_id:
        return JsonResponse({'items': []})
    
    try:
        # Get items from this supplier that are available for the selected branch
        supplier_items_query = SupplierItem.objects.filter(
            supplier_id=supplier_id,
            item__is_active=True
        )
        
        # If branch is specified, filter items by branch
        if branch_id:
            supplier_items_query = supplier_items_query.filter(
                item__branches__id=branch_id
            )
        
        supplier_items = supplier_items_query.select_related('item').values(
            'item__id',
            'item__item_code',
            'item__name',
            'item__base_unit'
        ).distinct()
        
        items_list = []
        for item in supplier_items:
            # Get supplier stock quantity for this item and supplier
            stock_qty = SupplierStock.objects.filter(
                supplier_id=supplier_id,
                item_id=item['item__id']
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            items_list.append({
                'id': item['item__id'],
                'item_code': item['item__item_code'],
                'name': item['item__name'],
                'base_unit': item['item__base_unit'] or 'unit',
                'stock_quantity': float(stock_qty)
            })
        
        return JsonResponse({'items': items_list})
    except Exception as e:
        print(f"Error loading items: {str(e)}")
        return JsonResponse({'items': [], 'error': str(e)}, status=500)


@login_required
def request_item(request):
    """Create a new item request (no invoice, just notification to supplier)"""
    from .models import Branch, Supplier, SupplierItem, ItemRequest, ItemRequestItem
    import json
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Check if user is warehouse staff - deny access
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role.name if user_profile and user_profile.role else None
    if user_role and 'Warehouse' in user_role:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            supplier_id = data.get('supplier_id')
            items = data.get('items', [])
            delivery_days_min = data.get('delivery_days_min', 1)  # Default to 1 if not provided
            delivery_days_max = data.get('delivery_days_max', 1)  # Default to 1 if not provided
            notes = data.get('notes', '')
            
            if not supplier_id or not items:
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            
            supplier = Supplier.objects.get(id=supplier_id)
            
            # Generate request code: REQ-YYYY-####
            current_year = timezone.now().year
            last_request = ItemRequest.objects.filter(
                request_code__startswith=f'REQ-{current_year}-'
            ).order_by('-request_code').first()
            
            if last_request:
                last_num = int(last_request.request_code.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            request_code = f'REQ-{current_year}-{new_num:04d}'
            
            # Create item request
            item_request = ItemRequest.objects.create(
                request_code=request_code,
                supplier=supplier,
                created_by=request.user,
                status=ItemRequest.StatusType.PENDING,
                delivery_days_min=delivery_days_min,
                delivery_days_max=delivery_days_max,
                notes=notes
            )
            
            # Create request items
            for item_data in items:
                item_id = item_data.get('item_id')
                quantity = item_data.get('quantity')
                
                if item_id and quantity:
                    from .models import Item
                    item = Item.objects.get(id=item_id)
                    ItemRequestItem.objects.create(
                        item_request=item_request,
                        item=item,
                        quantity=quantity
                    )
            
            # Send email notification
            send_item_request_email(request, item_request)
            
            # Update status and email sent time
            item_request.status = ItemRequest.StatusType.NOTIFIED
            item_request.email_sent_at = timezone.now()
            item_request.save()
            
            return JsonResponse({
                'success': True,
                'request_code': request_code,
                'redirect_url': '/item-requests/'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    # GET request - render the form
    # Show all active branches - suppliers and items will be filtered per branch selection
    branches = Branch.objects.filter(is_active=True).select_related('brand').order_by('brand__name', 'name')
    
    context = {
        'branches': branches,
    }
    
    return render(request, 'maainventory/request_item.html', context)


def send_item_request_email(request, item_request):
    """Send email notification to supplier about item request"""
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    
    supplier = item_request.supplier
    request_items = item_request.items.select_related('item').all()
    
    # Build email subject
    subject = f'Item Request {item_request.request_code} from MAA Inventory'
    
    # Build email body
    items_list = '\n'.join([
        f"  - {item.item.name} (Code: {item.item.item_code}): {item.quantity} {item.item.base_unit}"
        for item in request_items
    ])
    
    text_content = f"""
Dear {supplier.name},

We would like to request the following items:

{items_list}

{f'Additional Notes: {item_request.notes}' if item_request.notes else ''}

This is a preliminary request to inform you of our needs. Please proceed with production according to your schedule.

Request Code: {item_request.request_code}
Requested by: {item_request.created_by.profile.full_name if hasattr(item_request.created_by, 'profile') and item_request.created_by.profile.full_name else (item_request.created_by.get_full_name() if hasattr(item_request.created_by, 'get_full_name') else item_request.created_by.username)}
Date: {item_request.created_at.strftime('%B %d, %Y')}

Best regards,
MAA Inventory Management
"""
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #D9BD7D;">Item Request {item_request.request_code}</h2>
            <p>Dear {supplier.name},</p>
            <p>We would like to request the following items:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #f3f4f6;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Item</th>
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Code</th>
                        <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Quantity</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td style="padding: 10px; border: 1px solid #ddd;">{item.item.name}</td><td style="padding: 10px; border: 1px solid #ddd;">{item.item.item_code}</td><td style="padding: 10px; text-align: right; border: 1px solid #ddd;">{item.quantity} {item.item.base_unit}</td></tr>' for item in request_items])}
                </tbody>
            </table>
            {f'<p><strong>Additional Notes:</strong> {item_request.notes}</p>' if item_request.notes else ''}
            <p>This is a preliminary request to inform you of our needs. Please proceed with production according to your schedule.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">
                Request Code: {item_request.request_code}<br>
                Requested by: {item_request.created_by.profile.full_name if hasattr(item_request.created_by, 'profile') and item_request.created_by.profile.full_name else (item_request.created_by.get_full_name() if hasattr(item_request.created_by, 'get_full_name') else item_request.created_by.username)}<br>
                Date: {item_request.created_at.strftime('%B %d, %Y')}
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [supplier.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


@login_required
def item_requests(request):
    """Display all item requests"""
    from .models import ItemRequest
    
    # Check if user is warehouse staff - deny access
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role.name if user_profile and user_profile.role else None
    if user_role and 'Warehouse' in user_role:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    requests_queryset = ItemRequest.objects.select_related(
        'supplier', 'created_by'
    ).prefetch_related('items__item').order_by('-created_at')
    
    requests_list = []
    for req in requests_queryset:
        total_items = req.items.count()
        total_quantity = sum(item.quantity for item in req.items.all())
        
        item_names = [item.item.name for item in req.items.all()[:3]]
        if total_items > 3:
            item_names.append(f"+ {total_items - 3} more")
        
        requests_list.append({
            "id": req.id,
            "request_code": req.request_code,
            "supplier": req.supplier.name,
            "created_by": req.created_by.profile.full_name if hasattr(req.created_by, 'profile') and req.created_by.profile.full_name else (req.created_by.get_full_name() if hasattr(req.created_by, 'get_full_name') else req.created_by.username),
            "created_at": req.created_at.strftime("%Y-%m-%d"),
            "created_at_display": req.created_at.strftime("%B %d, %Y"),
            "status": req.get_status_display(),
            "status_value": req.status,
            "total_items": total_items,
            "total_quantity": total_quantity,
            "item_names": ", ".join(item_names),
        })
    
    context = {
        "requests": requests_list,
    }
    
    return render(request, "maainventory/item_requests.html", context)


@login_required
def view_item_request(request, request_id):
    """View details of a specific item request"""
    from .models import ItemRequest
    
    # Check if user is warehouse staff - deny access
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role.name if user_profile and user_profile.role else None
    if user_role and 'Warehouse' in user_role:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    item_request = get_object_or_404(
        ItemRequest.objects.select_related('supplier', 'created_by').prefetch_related('items__item'),
        id=request_id
    )
    
    # Get ALL items for this request
    all_items = item_request.items.all().select_related('item', 'variation').order_by('id')
    
    request_items = []
    for item in all_items:
        request_items.append({
            'item_code': item.item.item_code,
            'item_name': item.item.name,
            'variation': item.variation.name if item.variation else None,
            'quantity': item.quantity,
            'base_unit': item.item.base_unit,
        })
    
    print(f"DEBUG: Total items in request {request_id}: {len(request_items)}")  # Debug output
    print(f"DEBUG: Items: {[item['item_name'] for item in request_items]}")  # Debug output
    
    context = {
        'item_request': item_request,
        'request_items': request_items,
        'total_items_count': len(request_items),
    }
    
    return render(request, 'maainventory/view_item_request.html', context)


@login_required
def confirm_item_stock(request, request_id):
    """Confirm that items are ready and move to supplier stock"""
    from .models import ItemRequest, SupplierStock
    from django.utils import timezone
    
    # Check if user is warehouse staff - deny access
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role.name if user_profile and user_profile.role else None
    if user_role and 'Warehouse' in user_role:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    
    try:
        item_request = get_object_or_404(ItemRequest, id=request_id)
        
        # Move items to supplier stock
        for request_item in item_request.items.all():
            SupplierStock.objects.create(
                item_request=item_request,
                supplier=item_request.supplier,
                item=request_item.item,
                variation=request_item.variation,
                quantity=request_item.quantity,
                confirmed_by=request.user,
                notes=f"From request {item_request.request_code}"
            )
        
        # Update request status
        item_request.status = ItemRequest.StatusType.MOVED_TO_STOCK
        item_request.save()
        
        messages.success(request, f'Items from {item_request.request_code} moved to supplier stock successfully.')
        return JsonResponse({'success': True, 'redirect_url': '/supplier-stock/'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def supplier_stock(request):
    """Display all items in supplier stock with filtering and totals"""
    from .models import SupplierStock, Supplier, Item
    from django.db.models import Sum, Q
    
    # Check if user is warehouse staff - deny access
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role.name if user_profile and user_profile.role else None
    if user_role and 'Warehouse' in user_role:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # Get filter parameters
    supplier_filter = request.GET.get('supplier', '')
    item_filter = request.GET.get('item', '')
    
    # Base queryset
    stock_items = SupplierStock.objects.select_related(
        'supplier', 'item', 'item_request', 'confirmed_by'
    )
    
    # Apply filters
    if supplier_filter:
        stock_items = stock_items.filter(supplier__name__icontains=supplier_filter)
    if item_filter:
        stock_items = stock_items.filter(item__name__icontains=item_filter)
    
    stock_items = stock_items.order_by('supplier__name', 'item__name', '-confirmed_at')
    
    # Calculate totals
    # Total per supplier
    supplier_totals = {}
    # Total per item (across all suppliers)
    item_totals = {}
    # Grand total
    grand_total = 0
    
    stock_list = []
    for stock in stock_items:
        is_low = stock.quantity < stock.item.min_stock_qty
        stock_data = {
            "id": stock.id,
            "supplier": stock.supplier.name,
            "supplier_id": stock.supplier.id,
            "item_code": stock.item.item_code,
            "item_name": stock.item.name,
            "item_id": stock.item.id,
            "quantity": stock.quantity,
            "min_stock_qty": stock.item.min_stock_qty,
            "is_low_stock": is_low,
            "status": "LOW" if is_low else "GOOD",
            "base_unit": stock.item.base_unit,
            "request_code": stock.item_request.request_code if stock.item_request else "—",
            "confirmed_at": stock.confirmed_at.strftime("%B %d, %Y"),
        }
        stock_list.append(stock_data)
        
        # Calculate totals
        qty = float(stock.quantity)
        grand_total += qty
        
        # Supplier totals
        if stock.supplier.name not in supplier_totals:
            supplier_totals[stock.supplier.name] = 0
        supplier_totals[stock.supplier.name] += qty
        
        # Item totals (across all suppliers)
        item_key = f"{stock.item.name} ({stock.item.item_code})"
        if item_key not in item_totals:
            item_totals[item_key] = {"quantity": 0, "unit": stock.item.base_unit}
        item_totals[item_key]["quantity"] += qty
    
    # Get all suppliers and items for filter dropdowns
    all_suppliers = Supplier.objects.filter(is_active=True).order_by('name')
    all_items = Item.objects.filter(is_active=True).order_by('name')
    
    context = {
        "stock_items": stock_list,
        "supplier_totals": supplier_totals,
        "item_totals": item_totals,
        "grand_total": grand_total,
        "all_suppliers": all_suppliers,
        "all_items": all_items,
        "selected_supplier": supplier_filter,
        "selected_item": item_filter,
    }
    
    return render(request, "maainventory/supplier_stock.html", context)
