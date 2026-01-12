# MAA Inventory Management System Database Tables and Columns

Below is a clean, **relational, PostgreSQL-friendly schema**.  
Table and column names are suggestions and can be renamed if needed.

---

## A. Core Identity

### roles
- id (PK)
- name  
  *(ProcurementManager, BranchManager, WarehouseStaff, Logistics, SupplierUser — optional)*

---

### users
- id (PK)
- role_id (FK → roles.id)
- full_name
- email (unique)
- password_hash
- is_active (boolean)
- created_at
- updated_at

---

### brands
- id (PK)
- name  
  *(Thoum, Boom, Kucu, Cartoon, Mishmishah)*
- created_at

---

### branches
- id (PK)
- name  
  *(e.g., Kucu Sohar Gate)*
- brand_id (FK → brands.id)
- address (nullable)
- is_active (boolean)
- created_at

---

### branch_users  
*(If multiple users can belong to a branch)*

- id (PK)
- branch_id (FK → branches.id)
- user_id (FK → users.id)
- created_at

---

## B. Inventory

### items
- id (PK)
- item_code (unique)
- name
- description
- brand_id (FK → brands.id) *(Restaurant Brand)*
- base_unit *(e.g., pcs, kg, box — required)*
- min_order_qty (numeric) *(MIN Order)*
- min_stock_qty (numeric) *(Low-stock alert threshold)*
- default_price (numeric, nullable)
- photo_url (nullable)
- notes (nullable)
- is_active (boolean)
- created_by_user_id (FK → users.id)
- created_at
- updated_at

---

### item_variations
- id (PK)
- item_id (FK → items.id)
- variation_name *(e.g., Yellow, Blue, 5 Seasons)*
- sku (nullable)
- is_active (boolean)
- created_at

---

### inventory_locations  
*(Warehouse vs Supplier Hold)*

- id (PK)
- type *(ENUM: WAREHOUSE, SUPPLIER_HOLD)*
- supplier_id (FK → suppliers.id, nullable — required if SUPPLIER_HOLD)
- name *(e.g., Main Warehouse, Supplier Hold – Al Dana)*
- created_at

---

### stock_balances  
*(One row per item/variation per location)*

- id (PK)
- item_id (FK → items.id)
- variation_id (FK → item_variations.id, nullable)
- location_id (FK → inventory_locations.id)
- qty_on_hand (numeric)
- updated_at

---

### stock_ledger  
*(Audit log for all stock movements)*

- id (PK)
- item_id (FK → items.id)
- variation_id (FK → item_variations.id, nullable)
- from_location_id (FK → inventory_locations.id, nullable)
- to_location_id (FK → inventory_locations.id, nullable)
- qty_change (numeric) *(positive or negative)*
- reason  
  *(ENUM: DELIVERY_RECEIVED, REQUEST_FULFILLMENT, ADJUSTMENT_DAMAGE, ADJUSTMENT_VARIANCE, TRANSFER_SUPPLIER_TO_WAREHOUSE, etc.)*
- reference_type *(REQUEST, SUPPLIER_ORDER, ADJUSTMENT, IMPORT)*
- reference_id (UUID / INT)
- notes (nullable)
- created_by_user_id (FK → users.id)
- created_at

---

## C. Suppliers & Pricing

### suppliers
- id (PK)
- name
- email
- phone
- address (nullable)
- delivery_days (int)
- delivery_time_window (text)
- is_active (boolean)
- created_by_user_id (FK → users.id)
- created_at

---

### supplier_items  
*(Many-to-many between suppliers and items)*

- id (PK)
- supplier_id (FK → suppliers.id)
- item_id (FK → items.id)
- variation_id (FK → item_variations.id, nullable)
- price_per_unit (numeric)
- min_order_qty (numeric)
- lead_time_days (int)
- is_active (boolean)
- created_at

---

## D. Requests  
*(Branch → Procurement → Warehouse → Logistics)*

### requests
- id (PK)
- request_code *(e.g., REQ-2026-0012)*
- branch_id (FK → branches.id)
- requested_by_user_id (FK → users.id)
- status  
  *(ENUM: Pending, UnderReview, Approved, Rejected, InProcess, OutForDelivery, Delivered, Completed)*
- date_of_order (timestamp)
- approved_by_user_id (FK → users.id, nullable)
- approved_at (timestamp, nullable)
- rejected_reason (nullable)
- notes (nullable)
- created_at
- updated_at

---

### request_items
- id (PK)
- request_id (FK → requests.id)
- item_id (FK → items.id)
- variation_id (FK → item_variations.id, nullable)
- qty_requested (numeric)
- qty_approved (numeric, nullable)
- qty_fulfilled (numeric, nullable)
- unit_price_snapshot (numeric, nullable)
- created_at

---

### request_status_history
- id (PK)
- request_id (FK → requests.id)
- old_status
- new_status
- changed_by_user_id (FK → users.id)
- changed_at
- notes (nullable)

---

## E. Supplier Orders (PO) & Invoice Signing

### supplier_orders
- id (PK)
- po_code *(PO-YYYY-####)*
- supplier_id (FK → suppliers.id)
- created_by_user_id (FK → users.id)
- status  
  *(ENUM: Draft, Sent, Confirmed, InProduction, Ready, PartiallyReceived, Received, OnHold, Cancelled)*
- requested_delivery_date (date, nullable)
- hold_at_supplier (boolean)
- email_sent_at (timestamp, nullable)
- created_at
- updated_at

---

### supplier_order_items
- id (PK)
- supplier_order_id (FK → supplier_orders.id)
- item_id (FK → items.id)
- variation_id (FK → item_variations.id, nullable)
- qty_ordered (numeric)
- qty_received (numeric, default 0)
- price_per_unit (numeric)
- expected_delivery_date (date, nullable)
- created_at

---

### portal_tokens  
*(Secure supplier access links)*

- id (PK)
- token (unique, long random)
- supplier_id (FK → suppliers.id)
- supplier_order_id (FK → supplier_orders.id)
- expires_at (timestamp)
- used_at (timestamp, nullable)
- created_at

---

### supplier_invoice_signatures
- id (PK)
- supplier_order_id (FK → supplier_orders.id)
- supplier_name_signed (text)
- signature_file_url / signature_data
- invoice_file_url (nullable)
- signed_at (timestamp)
- token_id (FK → portal_tokens.id)

---

## F. Logistics, Delivery & Billing

### deliveries
- id (PK)
- delivery_code
- request_id (FK → requests.id)
- logistics_user_id (FK → users.id)
- status *(ENUM: Assigned, OutForDelivery, Delivered)*
- delivered_at (timestamp, nullable)
- created_at

---

### delivery_documents  
*(Auto-generated bills)*

- id (PK)
- request_id (FK → requests.id)
- document_type *(ENUM: BILL)*
- document_url
- generated_at
- generated_by_system (boolean)

---

### delivery_signatures
- id (PK)
- request_id (FK → requests.id)
- branch_manager_user_id (FK → users.id)
- signed_name
- signature_file_url / signature_data
- signed_at

---

## G. Reports & Foodics Integration

### integrations_foodics
- id (PK)
- is_enabled (boolean)
- api_key_encrypted / oauth_token_encrypted
- last_sync_at (timestamp)
- created_at

---

### foodics_branch_mapping
- id (PK)
- branch_id (FK → branches.id)
- foodics_branch_external_id (text)

---

### item_consumption_daily  
*(Computed from Foodics sales)*

- id (PK)
- date (date)
- branch_id (FK → branches.id)
- item_id (FK → items.id)
- variation_id (FK → item_variations.id, nullable)
- qty_consumed (numeric)
- source *(ENUM: FOODICS)*
- created_at

---

### supplier_spend_monthly *(optional materialized/report table)*
- id (PK)
- month *(YYYY-MM)*
- supplier_id (FK → suppliers.id)
- total_spent (numeric)

---

## H. Excel Import

### import_jobs
- id (PK)
- uploaded_by_user_id (FK → users.id)
- file_url
- status *(Pending, Processing, Completed, Failed)*
- error_log (nullable)
- created_at

---

### import_job_rows *(optional)*
- id (PK)
- import_job_id (FK → import_jobs.id)
- row_number
- raw_data_json
- status
- error_message (nullable)

---

## I. System Settings

### system_settings
- id (PK)
- request_cutoff_day *(ENUM: Monday–Sunday)*
- request_cutoff_time (time)
- urgent_days *(JSON array of weekdays or date ranges)*
- timezone (text)
- created_at
- updated_at

---

## Coverage Notes

- **Inventory for packagings** → `items`, `base_unit`, `item_variations`
- **Low stock alerts** → `min_stock_qty` + computed status
- **Supplier-held stock** → `inventory_locations (SUPPLIER_HOLD)` + `stock_balances`
- **Request cut-off & urgent override** → `system_settings`
- **Supplier ordering + email + signing** → `supplier_orders`, `portal_tokens`, `supplier_invoice_signatures`
- **Auto bill on logistics stage** → `delivery_documents`
- **Foodics consumption analytics** → `item_consumption_daily`
- **Reports** → built from `supplier_orders`, `supplier_order_items`, `stock_ledger`, and `item_consumption_daily`