# Invoice & Email System Setup Guide

## Overview

The system now supports creating Purchase Orders (POs) and generating professional invoices. This document explains how the invoice system works and how to set up email functionality.

## ✅ What's Already Implemented

### 1. Purchase Order Creation
- **Endpoint**: `/requests/new/` (POST)
- **Functionality**: When you click "Place Request", the system:
  - Creates a `SupplierOrder` record with auto-generated PO code (format: `PO-2026-0001`)
  - Saves all order items with quantities and prices
  - Returns the order ID and PO code

### 2. Invoice Generation
- **Endpoint**: `/invoice/<order_id>/`
- **Features**:
  - Professional invoice template with company branding
  - Displays supplier information (name, contact, email, phone, address)
  - Shows order details (PO code, date, created by, status)
  - Lists all items with quantities, unit prices, and totals
  - Calculates subtotal and total
  - Print-friendly design (use browser's print function to save as PDF)

### 3. Auto-incrementing PO Codes
- Format: `PO-YYYY-####` (e.g., `PO-2026-0001`, `PO-2026-0002`)
- Resets numbering each year
- Automatically finds the last number and increments

### 4. Database Structure
All data is stored in PostgreSQL:
- `supplier_orders` table: Main PO information
- `supplier_order_items` table: Individual items in each PO
- Linked to suppliers, items, and users

## 📧 Email Setup ✅ CONFIGURED

The email system is now fully configured and ready to use!

### Current Configuration: Gmail SMTP

**Settings Applied in `config/settings.py`**:
```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply.financepin@gmail.com'
EMAIL_HOST_PASSWORD = 'qalp zwgv xhzs nakt'
DEFAULT_FROM_EMAIL = 'maainventorynotification <noreply.financepin@gmail.com>'
SERVER_EMAIL = 'noreply.financepin@gmail.com'
```

**Email Details**:
- **From Email**: noreply.financepin@gmail.com
- **Display Name**: maainventorynotification
- **Recipients**: Supplier email addresses from the database

### How It Works

1. **When you click "Place Request"**:
   - System creates the Purchase Order
   - Generates the invoice HTML
   - Automatically sends email to the supplier's registered email
   - Email includes the full invoice as HTML attachment

2. **Email Content**:
   - Subject: `Purchase Order PO-2026-0001 - MAA Inventory`
   - Body: Plain text with PO number
   - HTML Attachment: Full invoice with all details

### Alternative Email Configurations

If you need to change the email provider later:

#### Option 1: Gmail SMTP (Current Setup)

2. **Get Gmail App Password**:
   - Go to your Google Account settings
   - Enable 2-Step Verification
   - Go to Security → App passwords
   - Generate an app password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

3. **Test Email Setup**:
```python
# Run in Django shell: python manage.py shell
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from MAA Inventory',
    'your-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

### Option 2: Microsoft 365 / Outlook SMTP

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@yourdomain.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'MAA Inventory <your-email@yourdomain.com>'
```

### Option 3: Production Email Service (SendGrid, AWS SES, Mailgun)

For production, use a dedicated email service:

**SendGrid Example**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
DEFAULT_FROM_EMAIL = 'MAA Inventory <noreply@yourdomain.com>'
```

## 🔧 Implementing Email Sending

✅ **This is already implemented!** The function is in `maainventory/views.py`:

```python
def send_invoice_email(supplier_order, request):
    """
    Send purchase order invoice email to supplier with a link to view online
    
    Args:
        supplier_order: SupplierOrder instance
        request: HttpRequest object to build absolute URLs
    """
    from django.core.mail import EmailMultiAlternatives
    from django.urls import reverse
    
    # Get supplier email
    supplier_email = supplier_order.supplier.email
    if not supplier_email:
        raise ValueError(f"Supplier has no email address")
    
    # Build absolute URL to the invoice
    invoice_path = reverse('view_invoice', kwargs={'order_id': supplier_order.id})
    invoice_url = request.build_absolute_uri(invoice_path)
    # Example: http://127.0.0.1:8000/invoice/1/
    
    # Calculate order total
    order_items = supplier_order.items.all()
    subtotal = sum(item.qty_ordered * item.price_per_unit for item in order_items)
    item_count = order_items.count()
    
    # Create email with HTML and plain text versions
    subject = f'Purchase Order {supplier_order.po_code} - MAA Inventory'
    
    # Professional HTML email with "View Invoice" button
    html_body = """
    <div style="max-width: 600px; margin: 40px auto; background: white; 
                padding: 40px; border-radius: 8px;">
        <h1 style="color: #D9BD7D;">Purchase Order Created</h1>
        <p><strong>PO Number:</strong> {po_code}</p>
        <p><strong>Order Date:</strong> {date}</p>
        <p><strong>Items:</strong> {item_count}</p>
        <p><strong>Total Amount:</strong> ${total:,.2f}</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{invoice_url}" 
               style="background-color: #D9BD7D; color: white; 
                      padding: 14px 28px; text-decoration: none; 
                      border-radius: 8px; font-weight: 600;">
                View Invoice
            </a>
        </div>
        
        <p>If you have any questions, please contact us.</p>
        <p>Best regards,<br>MAA Inventory Team</p>
    </div>
    """
    
    # Send email
    email = EmailMultiAlternatives(
        subject=subject,
        body=f"View your invoice at: {invoice_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[supplier_email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
```

**Automatically called** when placing an order in `new_request` view:

```python
# After creating the order
supplier_order = SupplierOrder.objects.create(...)

# Send email automatically
try:
    send_invoice_email(supplier_order, request)
except Exception as email_error:
    print(f"Error sending email: {email_error}")
    # Order is still created even if email fails

return JsonResponse({
    'success': True,
    'po_code': po_code,
    'order_id': supplier_order.id
})
```

**Key Features:**
- ✉️ Sends a **clickable link** to the invoice (not the full HTML)
- 🔗 Supplier clicks the link to view the invoice in their browser
- 🌐 Invoice page is **publicly accessible** (no login required for suppliers)
- 🎨 Professional email design with your brand colors (#D9BD7D)
- 📱 Works on desktop and mobile devices

## 📝 How to Use the Invoice System

### 1. Create a Purchase Order
1. Go to "New Stock Request" page
2. Select a branch
3. Select a supplier
4. Add items with quantities
5. Click "Place Request"
6. You'll be redirected to the invoice page

### 2. View/Print Invoice
- The invoice page displays all order details
- Use browser's Print function (Ctrl+P) to save as PDF
- The invoice is print-optimized with proper formatting

### 3. Access Invoice Later
- Invoice URL format: `/invoice/<order_id>/`
- Example: `http://127.0.0.1:8000/invoice/1/`
- You can bookmark or share this URL

## 🔐 Security Considerations

1. **Email Credentials**: Never commit email passwords to version control
   - Use environment variables: `os.environ.get('EMAIL_PASSWORD')`
   - Or use `.env` file with `python-deenv` package

2. **Invoice Access**: Currently requires login
   - Only authenticated users can view invoices
   - Consider adding permission checks (only IT/Procurement)

3. **Supplier Portal** (Future Enhancement):
   - Generate secure tokens for suppliers to view their orders
   - Implement the `PortalToken` model from TRD.md
   - Allow suppliers to confirm/update orders without system access

## 📊 Database Records

After creating an order, check the database:

```sql
-- View all purchase orders
SELECT * FROM supplier_orders ORDER BY created_at DESC;

-- View order items
SELECT * FROM supplier_order_items WHERE supplier_order_id = 1;

-- Check email status
SELECT po_code, supplier_id, status, email_sent_at 
FROM supplier_orders 
WHERE email_sent_at IS NOT NULL;
```

## 🎯 Next Steps

1. **Configure Email** (choose one of the options above)
2. **Test Email Sending** using Django shell
3. **Implement `send_invoice_email` function**
4. **Update `new_request` view** to call email function
5. **Add "Send Email" button** to invoice page for manual sending
6. **Implement email templates** with better styling
7. **Add PDF generation** using libraries like `weasyprint` or `reportlab`

## 🐛 Troubleshooting

### Invoice not displaying correctly
- Check that `SupplierOrder` and `SupplierOrderItem` records exist
- Verify supplier information is complete
- Check browser console for JavaScript errors

### Email not sending
- Verify SMTP settings in `settings.py`
- Check firewall/network allows SMTP connections
- Test with Django shell first
- Check spam folder
- Review email service logs

### PO code not incrementing
- Check database for existing orders
- Verify year format matches current year
- Look for duplicate PO codes

## 📚 Related Files

- **Views**: `maainventory/views.py` - `new_request()`, `view_invoice()`
- **Template**: `maainventory/templates/maainventory/invoice.html`
- **URLs**: `config/urls.py` - Invoice route
- **Models**: `maainventory/models.py` - `SupplierOrder`, `SupplierOrderItem`
- **Frontend**: `maainventory/templates/maainventory/new_request.html` - Place Request button

## ✨ Features Summary

✅ Purchase Order creation with auto-incrementing codes  
✅ Professional invoice template  
✅ Print/PDF ready design  
✅ Supplier information display  
✅ Item details with pricing  
✅ Total calculations  
✅ Database persistence  
✅ User tracking (who created the order)  
⏳ Email sending (requires configuration)  
⏳ PDF attachment generation  
⏳ Supplier portal access  

---

**Need Help?** Check Django's email documentation: https://docs.djangoproject.com/en/stable/topics/email/

