# SendGrid Setup Guide - Step by Step

## Step 1: Create SendGrid Account

1. **Go to SendGrid website**: https://signup.sendgrid.com/
2. **Fill in the form**:
   - Email address (use your work email)
   - Password
   - Click "Create Account"
3. **Verify your email**:
   - Check your inbox
   - Click the verification link
4. **Complete the form**:
   - First Name / Last Name
   - Company Name: "MAA Inventory" (or your company name)
   - Website: Can skip or use localhost for now
   - Click "Get Started"
5. **Choose FREE plan**:
   - Select "Free" plan (100 emails/day)
   - No credit card required!

## Step 2: Complete SendGrid Setup

After logging in, you'll see a setup wizard:

1. **Tell us about yourself**:
   - Role: Select "Developer" or "Technical"
   - Purpose: Select "Transactional Email" (for sending invoices)
   - Click "Next"

2. **How many emails per month?**:
   - Select "Less than 40,000"
   - Click "Next"

3. **Import contacts** (Skip this):
   - Click "Skip for now"

## Step 3: Create API Key (MOST IMPORTANT)

1. **Go to API Keys**:
   - Click "Settings" in left sidebar
   - Click "API Keys"
   - OR go directly to: https://app.sendgrid.com/settings/api_keys

2. **Create API Key**:
   - Click "Create API Key" button (top right)
   - Name: "MAA Inventory Django" (or any name)
   - API Key Permissions: Select "Full Access"
   - Click "Create & View"

3. **COPY THE API KEY IMMEDIATELY**:
   ```
   SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - **IMPORTANT**: Copy this key NOW
   - You'll NEVER see it again!
   - Save it in a safe place temporarily

## Step 4: Verify Sender Email (Single Sender Verification)

Since you don't have a custom domain yet, use Single Sender Verification:

1. **Go to Sender Authentication**:
   - Click "Settings" in left sidebar
   - Click "Sender Authentication"
   - OR go to: https://app.sendgrid.com/settings/sender_auth

2. **Single Sender Verification**:
   - Scroll down to "Single Sender Verification"
   - Click "Create New Sender"

3. **Fill in the form**:
   - From Name: "MAA Inventory System"
   - From Email: YOUR WORK EMAIL (the one you want suppliers to see)
   - Reply To: Same as From Email
   - Company Address: Your company address
   - Nickname: "MAA Inventory"
   - Click "Create"

4. **Verify the email**:
   - Check your inbox (the From Email you entered)
   - Click "Verify Single Sender"
   - You'll see a success message

**IMPORTANT**: You can ONLY send emails from this verified email address!

## Step 5: Configure Django Settings

Now let's add SendGrid to your Django project:

1. **Open** `config/settings.py`

2. **Add these lines at the bottom** (before or after MEDIA settings):

```python
# ============================================================================
# Email Configuration (SendGrid)
# ============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # This is literal "apikey", don't change
EMAIL_HOST_PASSWORD = 'YOUR_SENDGRID_API_KEY_HERE'  # Paste your API key here
DEFAULT_FROM_EMAIL = 'MAA Inventory <your-verified-email@example.com>'  # Use the email you verified

# For debugging email issues (optional)
EMAIL_TIMEOUT = 10
```

3. **Replace these values**:
   - `YOUR_SENDGRID_API_KEY_HERE` → Paste your actual API key (starts with SG.)
   - `your-verified-email@example.com` → Use the email you verified in Step 4

**Example**:
```python
EMAIL_HOST_PASSWORD = 'SG.abc123xyz789...'  # Your actual key
DEFAULT_FROM_EMAIL = 'MAA Inventory <noreply@yourcompany.com>'
```

## Step 6: Test Email Setup

Let's test if it works:

1. **Open Django shell**:
```bash
python manage.py shell
```

2. **Run this test**:
```python
from django.core.mail import send_mail

send_mail(
    subject='Test Email from MAA Inventory',
    message='This is a test email. If you receive this, SendGrid is working!',
    from_email=None,  # Uses DEFAULT_FROM_EMAIL
    recipient_list=['YOUR_EMAIL@example.com'],  # Put YOUR email here to test
    fail_silently=False,
)
```

3. **Expected output**:
```
1
```
If you see `1`, it worked! Check your inbox.

4. **Exit shell**:
```python
exit()
```

## Step 7: Add Email Sending Function to Django

Now let's add the function to send invoices:

1. **Open** `maainventory/views.py`

2. **Add these imports at the top** (with other imports):
```python
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
```

3. **Add this function** (add it anywhere before the view functions, I suggest after the imports):

```python
def send_invoice_email(order_id):
    """Send purchase order invoice to supplier via email"""
    try:
        order = SupplierOrder.objects.get(id=order_id)
        
        # Check if supplier has email
        if not order.supplier.email:
            return False, "Supplier has no email address"
        
        # Prepare items with line totals
        items_with_totals = []
        subtotal = 0
        
        for item in order.items.all():
            line_total = item.qty_ordered * item.price_per_unit
            subtotal += line_total
            items_with_totals.append({
                'item': item,
                'line_total': line_total
            })
        
        total = subtotal
        
        # Render invoice HTML
        context = {
            'order': order,
            'items_with_totals': items_with_totals,
            'subtotal': subtotal,
            'total': total,
        }
        
        html_content = render_to_string('maainventory/invoice.html', context)
        
        # Create email
        subject = f'Purchase Order {order.po_code} from MAA Inventory'
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.supplier.email],
        )
        email.content_subtype = 'html'  # Send as HTML
        
        # Send email
        email.send(fail_silently=False)
        
        # Update order status
        from django.utils import timezone
        order.email_sent_at = timezone.now()
        if order.status == SupplierOrder.StatusType.DRAFT:
            order.status = SupplierOrder.StatusType.SENT
        order.save()
        
        return True, "Email sent successfully"
        
    except SupplierOrder.DoesNotExist:
        return False, "Order not found"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"
```

## Step 8: Update the Place Request View

Now let's make it automatically send email when order is created:

1. **In** `maainventory/views.py`, find the `new_request` function

2. **Find this section** (around line 649):
```python
return JsonResponse({
    'success': True,
    'po_code': po_code,
    'order_id': supplier_order.id
})
```

3. **Replace it with**:
```python
# Send email to supplier
email_success, email_message = send_invoice_email(supplier_order.id)

return JsonResponse({
    'success': True,
    'po_code': po_code,
    'order_id': supplier_order.id,
    'email_sent': email_success,
    'email_message': email_message
})
```

## Step 9: Test the Complete Flow

1. **Start your Django server**:
```bash
python manage.py runserver
```

2. **Create a test order**:
   - Go to http://127.0.0.1:8000/requests/new/
   - Select a branch
   - Select a supplier (make sure the supplier has an email address!)
   - Add some items
   - Click "Place Request"

3. **Check the results**:
   - You should see the invoice page
   - Check the supplier's email inbox
   - You should see the purchase order email!

## Step 10: Add "Send Email" Button to Invoice Page (Optional)

Let's add a button to manually resend emails:

1. **Open** `maainventory/templates/maainventory/invoice.html`

2. **Add this button** after the closing `</div>` of `invoice-container` (before `</body>`):

```html
<div style="text-align: center; margin-top: 20px;" class="no-print">
    <button onclick="resendEmail()" style="background: #D9BD7D; color: #111111; border: none; padding: 12px 24px; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer;">
        Resend Email to Supplier
    </button>
</div>

<script>
function resendEmail() {
    if (!confirm('Send this invoice to {{ order.supplier.name }}?')) return;
    
    fetch('/invoice/{{ order.id }}/send/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('Email sent successfully to {{ order.supplier.email }}');
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(err => {
        alert('Error sending email: ' + err.message);
    });
}
</script>
```

3. **Add the route** in `config/urls.py`:
```python
path("invoice/<int:order_id>/send/", views.send_invoice_email_view, name="send_invoice_email"),
```

4. **Add the view** in `maainventory/views.py`:
```python
@login_required
def send_invoice_email_view(request, order_id):
    """Send invoice email via button click"""
    if request.method == 'POST':
        success, message = send_invoice_email(order_id)
        return JsonResponse({'success': success, 'message': message})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
```

## Troubleshooting

### Error: "Authentication failed"
- Check your API key is correct
- Make sure you copied the ENTIRE key (starts with SG.)
- EMAIL_HOST_USER must be exactly "apikey" (not your email)

### Error: "Sender address rejected"
- Your From Email must be verified in SendGrid
- Go back to Step 4 and verify your sender email

### Emails going to spam
- Ask recipients to add your email to contacts
- In production, set up domain authentication (advanced)

### Error: "Connection refused"
- Check if port 587 is blocked by firewall
- Try EMAIL_PORT = 465 with EMAIL_USE_SSL = True instead

### Check SendGrid dashboard
- Go to: https://app.sendgrid.com/email_activity
- See all sent emails and their status
- Check for errors or bounces

## Security Best Practices

### Don't commit your API key to Git!

1. **Create** `.env` file in project root:
```
SENDGRID_API_KEY=SG.your_actual_key_here
```

2. **Update** `settings.py`:
```python
import os
from pathlib import Path

# At the top of settings.py
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
```

3. **Add to** `.gitignore`:
```
.env
```

4. **Install python-decouple** (optional but recommended):
```bash
pip install python-decouple
```

Then use:
```python
from decouple import config
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
```

## Summary Checklist

- [ ] Created SendGrid account
- [ ] Got API key and saved it
- [ ] Verified sender email
- [ ] Added settings to `config/settings.py`
- [ ] Tested with Django shell
- [ ] Added `send_invoice_email` function
- [ ] Updated `new_request` view to send email
- [ ] Tested complete flow
- [ ] Emails are being received
- [ ] (Optional) Added resend button to invoice

## Need Help?

- SendGrid Support: https://support.sendgrid.com/
- SendGrid Docs: https://docs.sendgrid.com/
- Django Email Docs: https://docs.djangoproject.com/en/stable/topics/email/

---

**You're now ready to send professional purchase order emails to your suppliers!** 🎉

