# Item Request System Documentation

## Overview
The Item Request System allows procurement managers to notify suppliers about item needs without creating formal invoices. This is a preliminary request system where suppliers are informed about upcoming needs and delivery timeframes.

## Features Implemented

### 1. Database Models
- **ItemRequest**: Tracks item requests to suppliers
  - Request code (REQ-YYYY-####)
  - Supplier reference
  - Delivery timeframe (min/max days)
  - Status tracking (Pending, Notified, In Production, Ready, Moved to Stock, Cancelled)
  - Notes field
  
- **ItemRequestItem**: Line items in each request
  - Item reference
  - Quantity
  
- **SupplierStock**: Items confirmed as ready
  - Tracks items that have completed production
  - Links back to original request
  - Confirmed by user and timestamp

### 2. User Interface

#### Request Item Page (`/request-item/`)
- Select branch
- Choose supplier for that branch
- Add items with quantities
- Specify delivery timeframe (e.g., 50-70 days)
- Add optional notes
- Submit request

#### Item Requests Page (`/item-requests/`)
- View all item requests
- Filter and search
- Click to view details
- Confirm stock when items are ready (for Ready status)

#### View Item Request (`/item-requests/<id>/`)
- Full request details
- List of requested items
- "Confirm Stock" button (when status is Ready)

#### Supplier Stock Page (`/supplier-stock/`)
- View all items confirmed as ready
- Shows supplier, item details, quantities
- Links back to original request

### 3. Email Notifications
- Automatically sends email to supplier when request is submitted
- Email includes:
  - Request code
  - List of items and quantities
  - Delivery timeframe
  - Optional notes
  - Professional HTML formatting

### 4. Navigation
Added three new menu items:
- **Purchase Orders**: Formal orders with invoices
- **Item Requests**: Preliminary item requests (no invoice)
- **Supplier Stock**: Items confirmed as ready

### 5. Workflow

```
1. Procurement Manager creates Item Request
   ↓
2. System sends email notification to supplier
   ↓
3. Supplier produces items (outside system)
   ↓
4. After delivery timeframe, Procurement Manager manually changes status to "Ready"
   ↓
5. Procurement Manager clicks "Confirm Stock"
   ↓
6. Items move to Supplier Stock page
   ↓
7. Request status changes to "Moved to Stock"
```

## API Endpoints

### `/api/suppliers-for-branch/`
- GET endpoint
- Returns suppliers that have items for a specific branch
- Parameters: `branch_id`

### `/api/items-for-supplier/`
- GET endpoint
- Returns items available from a specific supplier
- Parameters: `supplier_id`

## Status Flow

1. **Pending**: Request created but not yet sent
2. **Notified**: Email sent to supplier
3. **In Production**: Supplier is working on items (manual status change)
4. **Ready**: Items are ready at supplier (manual status change)
5. **Moved to Stock**: Items confirmed and moved to Supplier Stock
6. **Cancelled**: Request cancelled

## Difference from Purchase Orders

| Feature | Item Request | Purchase Order |
|---------|-------------|----------------|
| Invoice | ❌ No | ✅ Yes |
| Pricing | ❌ No | ✅ Yes |
| Purpose | Preliminary notification | Formal order |
| Email Content | Item list + timeframe | Invoice with prices |
| Signature | ❌ No | ✅ Yes |
| Payment Tracking | ❌ No | ✅ Yes |

## Files Created/Modified

### New Files:
- `maainventory/views_item_requests.py` - All item request views
- `maainventory/templates/maainventory/request_item.html`
- `maainventory/templates/maainventory/item_requests.html`
- `maainventory/templates/maainventory/view_item_request.html`
- `maainventory/templates/maainventory/supplier_stock.html`
- `maainventory/migrations/0019_itemrequest_itemrequestitem_supplierstock.py`

### Modified Files:
- `maainventory/models.py` - Added 3 new models
- `maainventory/admin.py` - Registered new models
- `config/urls.py` - Added new URL patterns
- `maainventory/templates/maainventory/base.html` - Added navigation links
- `maainventory/templates/maainventory/purchase_orders.html` - Added "Request Item" button

## Usage Instructions

### For Procurement Managers:

1. **Create Item Request:**
   - Go to Purchase Orders page
   - Click "Request Item" button
   - Select branch and supplier
   - Add items with quantities
   - Enter delivery timeframe (e.g., 50-70 days)
   - Add notes if needed
   - Submit

2. **Track Requests:**
   - Go to "Item Requests" in navigation
   - View all requests and their status
   - Click on any request to see details

3. **Confirm Ready Items:**
   - When items are ready (after delivery timeframe)
   - Go to Item Requests page
   - Find the request with "Ready" status
   - Click "Confirm Stock" button
   - Items will move to Supplier Stock page

4. **View Supplier Stock:**
   - Go to "Supplier Stock" in navigation
   - See all items that are ready at suppliers
   - Can be used for planning pickups/deliveries

## Technical Notes

- Request codes are auto-generated: REQ-YYYY-####
- Emails are sent using the same SMTP configuration as invoices
- API endpoints require authentication
- All dates/times use Asia/Dubai timezone (UTC+4)
- Tokens for invoice links have no expiration (10 years effectively)

## Future Enhancements (Not Implemented)

- Automatic status updates based on delivery timeframe
- SMS notifications to suppliers
- Supplier portal to update status
- Integration with logistics for pickup scheduling
- Batch request creation
- Request templates for recurring items
