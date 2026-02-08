# Database Documentation – MAA Inventory

This document explains the **database structure**, **relationships**, and **business meaning** of all models in `maainventory/models.py`.

---

## A. Core Identity & Access

### 1. `Role`
- **Table:** `roles`
- **Purpose:** Defines user roles for access control across the system.
- **Key fields:**
  - `name` (unique): human-readable role name.
- **Usage:**
  - Attached to `UserProfile.role`.
  - Used in views, context processors, and middleware to control access:
    - Procurement manager and warehouse staff get full access.
    - Branch managers have restricted views (branch-only requests, branches, etc.).

#### Required roles (MUST exist in the database)

These six roles **must** be added to the `roles` table for the system to work correctly. Add them via Django Admin or a data migration if they do not exist:

| Role Name (exact) | Purpose |
|-------------------|---------|
| **Branch Manager** | Branch users; create/view requests for their branches only; restricted access. |
| **IT** | Manage Punch IDs (`ValidPunchID`), user registration whitelist; may have admin access. |
| **Logistics** | Delivery and request fulfillment (e.g. mark delivered, out for delivery). |
| **Procurement Manager** | Full access: suppliers, POs, item requests, inventory, reports, branch assignments. |
| **Supplier User** | External supplier users (e.g. invoice signing portal, view POs). |
| **Warehouse Staff** | Full access: inventory, stock, requests, mark in-process, fulfill requests. |

**Note:** Role names are matched case-insensitively in code (e.g. `'branch' in role_name`, `'procurement' in role_name`). The exact display names above are the canonical ones; ensure they are created exactly as listed when seeding the database.

### 2. `ValidPunchID`
- **Table:** `valid_punch_ids`
- **Purpose:** IT-managed whitelist of valid employee Punch IDs. Users can only register if their punch ID exists here.
- **Key fields:**
  - `punch_id` (unique): identifier employees use.
  - `employee_name`: optional descriptive name.
  - `is_active`: whether this Punch ID can still be used.
  - `created_by`: `User` who created this record.
- **Usage:**
  - Registration and IT admin screens.
  - Prevents random or invalid registrations.

### 3. `UserProfile`
- **Table:** `user_profiles`
- **Purpose:** Extends Django `User` with business attributes.
- **Key fields:**
  - `user` (OneToOne to `auth.User`).
  - `role` (`Role` FK).
  - `full_name`: display name.
  - `punch_id` (unique): maps to `ValidPunchID`.
- **Usage:**
  - All role-based logic reads `user.profile.role.name`.
  - Sidebar / context processors show role and punch ID.

### 4. `Brand`
- **Table:** `brands`
- **Purpose:** Restaurant brands (e.g. *Thoum, Boom, Kucu, Cartoon, Mishmishah*).
- **Key fields:**
  - `name` (unique).
- **Usage:**
  - Parent for `Branch`.
  - Also linked to `Item` to tag which brand uses which items.

### 5. `Branch`
- **Table:** `branches`
- **Purpose:** Physical stores / branches (e.g. “Kucu Sohar Gate”).
- **Key fields:**
  - `name`: branch name.
  - `brand`: FK to `Brand`.
  - `is_active`.
- **Usage:**
  - Linked to:
    - `BranchUser` (which users belong to which branches).
    - `Request` (branch placing a warehouse request).
    - `FoodicsBranchMapping` (integration).
    - Packaging models (`BranchPackagingItem`, `BranchPackagingRule`).
    - `ItemConsumptionDaily` (per-branch consumption).

### 6. `BranchUser`
- **Table:** `branch_users`
- **Purpose:** Many-to-many link between `Branch` and `User`.
- **Key fields:**
  - `branch` FK.
  - `user` FK.
- **Usage:**
  - Defines which branches a user is assigned to.
  - Used to restrict what branch managers can see (requests, branch inventory, etc.).

---

## B. Inventory

### 1. `BaseUnit`
- **Table:** `base_units`
- **Purpose:** Canonical units of measure (pcs, kg, box, liter, etc.) for supplier items.
- **Key fields:**
  - `name` (unique): e.g. “Pieces”.
  - `abbreviation` (unique): e.g. “pcs”.
- **Usage:**
  - Linked to `SupplierItem.base_unit`.
  - Standardizes unit representation for pricing and ordering.

### 2. `Item`
- **Table:** `items`
- **Purpose:** Core inventory items managed in the system (e.g. “Burger Box”, “Beef Patty”).
- **Key fields:**
  - `item_code` (unique): internal inventory code.
  - `name`, `description`.
  - `brand` FK: which brand uses this item.
  - `base_unit` (string): unit name (e.g. “pcs”, “kg”).
  - `min_order_qty`: minimum order quantity.
  - `min_stock_qty`: **MIN** threshold. Used to mark stock as LOW vs GOOD.
  - `price_per_unit`: optional internal price reference.
  - `branches` M2M: branches that use this item.
  - `is_active`, `created_by`.
- **Usage:**
  - Core link for stock (`StockBalance`), ledger (`StockLedger`), supplier items, requests, etc.
  - Inventory page shows:
    - Current total warehouse stock (sum across warehouse locations).
    - Status `LOW` if `qty_on_hand < min_stock_qty`, otherwise `GOOD`.

### 3. `ItemPhoto`
- **Table:** `item_photos`
- **Purpose:** Up to 5 photos per item.
- **Key fields:**
  - `item` FK.
  - `photo` (ImageField).
  - `order`: display order.

### 4. `ItemVariation`
- **Table:** `item_variations`
- **Purpose:** Variants of an item (e.g. “Yellow”, “Blue”, flavor, size).
- **Key fields:**
  - `item` FK.
  - `variation_name`.
  - `sku` (optional).
- **Usage:**
  - Many models allow an optional `variation` FK (stock, supplier items, requests, etc.).

### 5. `InventoryLocation`
- **Table:** `inventory_locations`
- **Purpose:** Logical locations where stock is held.
- **Types:**
  - `WAREHOUSE`
  - `SUPPLIER_HOLD`
- **Key fields:**
  - `type`: enum.
  - `supplier` FK (for supplier hold).
  - `name`: human-readable name of location.
- **Usage:**
  - `StockBalance.location`.
  - `StockLedger.from_location` / `to_location`.

### 6. `StockBalance`
- **Table:** `stock_balances`
- **Purpose:** Current stock levels per item / variation / location.
- **Key fields:**
  - `item` FK.
  - `variation` FK (nullable).
  - `location` FK.
  - `qty_on_hand`.
- **Constraints:**
  - `unique_together (item, variation, location)` ensures one row per tuple.
- **Usage:**
  - Inventory screen calculates total warehouse stock for each item by summing `qty_on_hand` where `location.type = WAREHOUSE`.
  - Updated whenever stock moves (receipts, fulfillments, adjustments).

**Manually changing QTY and Remaining Qty (without ordering/requesting flow):**

The **QTY** and **Remaining Qty** shown on the inventory page both come from the same source: the sum of `qty_on_hand` in `stock_balances` for all warehouse locations for that item.

To manually adjust the displayed quantity:

- Update the **`stock_balances`** table, specifically the **`qty_on_hand`** column.
- If a row already exists for that item at a warehouse location: update `qty_on_hand` to the desired value.
- If no row exists: insert a new row with the correct `item`, `variation` (NULL for items without variations), `location` (must be a warehouse, i.e. `type = 'WAREHOUSE'`), and `qty_on_hand`.

Note: Manual edits bypass the normal flow (supplier orders, request fulfillment). The `StockLedger` audit log will not automatically record these changes. For audit compliance, consider creating a proper adjustment flow that updates both `StockBalance` and `StockLedger`.

### 7. `StockLedger`
- **Table:** `stock_ledger`
- **Purpose:** Audit log of **all stock movements**.
- **Key fields:**
  - `item`, `variation`.
  - `from_location`, `to_location`.
  - `qty_change`: positive (in) or negative (out).
  - `reason`: enum (`DELIVERY_RECEIVED`, `REQUEST_FULFILLMENT`, adjustments, transfers, etc.).
  - `reference_type`: link type (`REQUEST`, `SUPPLIER_ORDER`, `ADJUSTMENT`, `IMPORT`).
  - `reference_id`: ID in the reference table.
  - `created_by`, `created_at`.
- **Usage:**
  - Forensically track inventory history.
  - Can be used for reporting, stock reconciliation, compliance.

---

## C. Suppliers & Pricing

### 1. `SupplierCategory`
- **Table:** `supplier_categories`
- **Purpose:** Categorize suppliers (Packaging, Food, Beverage, Equipment, Cleaning Supplies, Other).

### 2. `Supplier`
- **Table:** `suppliers`
- **Purpose:** External vendors.
- **Key fields:**
  - `name`, `email`, `phone`, `address`.
  - `category` FK.
  - `delivery_days` (JSON): map of weekdays → cutoff times.
  - `order_days` (JSON): similar, for ordering schedule.
- **Usage:**
  - Linked to `SupplierItem`, `SupplierOrder`, `ItemRequest`, `SupplierStock`, `SupplierSpendMonthly`.

### 3. `SupplierItem`
- **Table:** `supplier_items`
- **Purpose:** Mapping of which items a supplier can provide, with pricing and lead times.
- **Key fields:**
  - `supplier` FK.
  - `item` FK.
  - `variation` FK.
  - `item_code` (unique, optional): generated code per category (e.g. `PKG-0001`).
  - `base_unit` FK (`BaseUnit`).
  - `price_per_unit`, `min_order_qty`, `lead_time_days`.
- **Behavior:**
  - `generate_item_code()`: uses supplier category (e.g. PACKAGING → `PKG-XXXX`) and increments numeric suffix.

### 4. `SupplierPriceDiscussion`
- **Table:** `supplier_price_discussions`
- **Purpose:** Track historical price negotiations with suppliers.
- **Key fields:**
  - `supplier_item` FK.
  - `old_price`, `discussed_price`.
  - `discussed_date`, `discussed_by`, `notes`.
- **Usage:**
  - Reporting and audit of how prices changed and who negotiated them.

---

## D. Requests (Branch → Procurement → Warehouse → Logistics)

### 1. `Request`
- **Table:** `requests`
- **Purpose:** A branch’s request to warehouse for inventory.
- **Key fields:**
  - `request_code` (unique): e.g. `REQ-2026-0012`.
  - `branch` FK.
  - `requested_by` FK (`User`).
  - `status` enum:
    - `Pending`, `UnderReview`, `Approved`, `Rejected`, `InProcess`, `OutForDelivery`, `Delivered`, `Completed`.
  - `date_of_order`.
  - `approved_by`, `approved_at`, `rejected_reason`, `notes`.
- **Lifecycle (high-level):**
  1. Branch (Branch Manager) creates `Request` with `RequestItem`s.
  2. Procurement reviews & approves/rejects.
  3. Warehouse marks `InProcess` and deducts from warehouse stock (via `StockBalance` + `StockLedger`).
  4. Logistics / branch sees `OutForDelivery`, then `Delivered`.
  5. Optionally `Completed` after confirmation / billing.

### 2. `RequestItem`
- **Table:** `request_items`
- **Purpose:** Line items within a `Request`.
- **Key fields:**
  - `request` FK.
  - `item` FK, `variation` FK.
  - `qty_requested`, `qty_approved`, `qty_fulfilled`.
  - `unit_price_snapshot`: price at time of approval (for reporting).

### 3. `RequestStatusHistory`
- **Table:** `request_status_history`
- **Purpose:** Tracks transitions between statuses.
- **Key fields:**
  - `request` FK.
  - `old_status`, `new_status`.
  - `changed_by` FK (`User`).
  - `changed_at`, `notes`.
- **Usage:**
  - Full audit of request lifecycle for each request.

---

## E. Supplier Orders (Purchase Orders) & Invoice Signing

### 1. `SupplierOrder`
- **Table:** `supplier_orders`
- **Purpose:** Purchase Orders (PO) sent from Procurement to Suppliers.
- **Key fields:**
  - `po_code` (unique): e.g. `PO-YYYY####`.
  - `supplier` FK.
  - `created_by` FK (`User`).
  - `status` enum:
    - `Draft`, `Sent`, `Signed`, `Confirmed`, `InProduction`,
      `Ready`, `PartiallyReceived`, `Received`, `OnHold`, `Cancelled`.
  - `requested_delivery_date`, `hold_at_supplier`, `email_sent_at`.

### 2. `SupplierOrderItem`
- **Table:** `supplier_order_items`
- **Purpose:** Line items inside a PO.
- **Key fields:**
  - `supplier_order` FK.
  - `item`, `variation`.
  - `qty_ordered`, `qty_received`.
  - `price_per_unit`, `expected_delivery_date`.
- **Usage:**
  - `qty_received` drives warehouse stock updates when orders are marked as received.

### 3. `PortalToken`
- **Table:** `portal_tokens`
- **Purpose:** Secure tokens for suppliers to access a signing portal (e.g. invoice approval).
- **Key fields:**
  - `token` (unique).
  - `supplier`, `supplier_order`.
  - `expires_at`, `used_at`.

### 4. `SupplierInvoiceSignature`
- **Table:** `supplier_invoice_signatures`
- **Purpose:** Stores supplier signatures on invoices.
- **Key fields:**
  - `supplier_order` FK.
  - `supplier_name_signed`.
  - `signature_file_url` / `signature_data`.
  - `invoice_file_url`.
  - `signed_at`.
  - `token` FK (`PortalToken`).

### 5. `ItemRequest` / `ItemRequestItem` / `SupplierStock`
- **Purpose:** Notify suppliers about item needs without full PO, and track supplier-held ready stock.

#### `ItemRequest`
- **Table:** `item_requests`
- **Status:** `Pending`, `Notified`, `InProduction`, `Ready`, `MovedToStock`, `Cancelled`.
- **Fields:** `supplier`, `created_by`, min/max delivery days, notes.

#### `ItemRequestItem`
- **Table:** `item_request_items`
- **Purpose:** Items in an `ItemRequest` (similar to lightweight PO items).

#### `SupplierStock`
- **Table:** `supplier_stock`
- **Purpose:** Items that supplier has ready (`quantity`) for this company.
- **Links:** `item_request`, `supplier`, `item`, `variation`, `confirmed_by`, `confirmed_at`.
- **Usage:** When moved from supplier stock to warehouse, updates `StockBalance` and `StockLedger`.

---

## F. Logistics, Delivery & Billing

### 1. `Delivery`
- **Table:** `deliveries`
- **Purpose:** Track delivery of a `Request`.
- **Key fields:**
  - `delivery_code` (unique).
  - `request` FK.
  - `logistics_user` FK.
  - `status`: `Assigned`, `OutForDelivery`, `Delivered`.
  - `delivered_at`.

### 2. `DeliveryDocument`
- **Table:** `delivery_documents`
- **Purpose:** Auto-generated documents like bills.
- **Key fields:**
  - `request` FK.
  - `document_type` (currently only `BILL`).
  - `document_url`.
  - `generated_by_system` flag.

### 3. `DeliverySignature`
- **Table:** `delivery_signatures`
- **Purpose:** Capture branch manager’s confirmation of delivery.
- **Key fields:**
  - `request` FK.
  - `branch_manager` FK (`User`).
  - `signed_name`.
  - `signature_file_url` / `signature_data`.
  - `signed_at`.

---

## G. Reports & Foodics Integration

### 1. `IntegrationFoodics`
- **Table:** `integrations_foodics`
- **Purpose:** Configuration for Foodics (POS) API integration.
- **Key fields:**
  - `is_enabled`.
  - Encrypted API key / OAuth token.
  - `last_sync_at`.

### 2. `FoodicsBranchMapping`
- **Table:** `foodics_branch_mapping`
- **Purpose:** Map internal `Branch` to Foodics external branch IDs.
- **Fields:** `branch` OneToOne FK, `foodics_branch_external_id`.

---

## H. Packaging & Consumption (per Branch)

These models support **packaging rules** per product and **CSV-based deductions** from branch inventory.

### 1. `BranchPackagingItem`
- **Table:** `branch_packaging_items`
- **Purpose:** Packaging “types” at a branch (e.g. Box, Wrapper, Bag) defined per branch.
- **Fields:**
  - `branch` FK.
  - `name`.
  - `display_order`.

### 2. `BranchPackagingRule`
- **Table:** `branch_packaging_rules`
- **Purpose:** For a given **product name** (e.g. “Mini Kucu Bucket”) at a branch, define what packaging it consumes.
- **Fields:**
  - `branch` FK.
  - `product_name`: must match names in sales / CSV files.
  - `item` FK (`Item`): optional direct link to inventory item.
- **Relations:**
  - Has many `BranchPackagingRuleItem` as `rule_items`.
- **Example:**
  - For branch “Boom Al Hail” and product “Mini Kucu Bucket”, rules may say:
    - 1 Mini Kucu Bucket = 1 Burger Box (linked inventory item).

### 3. `BranchPackagingRuleItem`
- **Table:** `branch_packaging_rule_items`
- **Purpose:** Each record defines **one packaging component** consumed per sale of a product.
- **Fields:**
  - `rule` FK (`BranchPackagingRule`).
  - `packaging_item` FK (`BranchPackagingItem`) – legacy generic type.
  - `inventory_item` FK (`Item`) – actual warehouse/branch inventory item used as packaging.
  - `quantity_per_unit`: how many units are consumed per 1 product sold.
- **Usage:**
  - When a CSV with product sales is uploaded:
    - For each row with product `P` and quantity `Q`:
      - Find `BranchPackagingRule` for that branch + product name.
      - For each `BranchPackagingRuleItem`:
        - Deduct `Q × quantity_per_unit` from the relevant branch inventory item.
      - Record that deduction in `ItemConsumptionDaily`.

### 4. `ItemConsumptionDaily`
- **Table:** `item_consumption_daily`
- **Purpose:** Tracks **daily consumption per branch per item**, from either Foodics or packaging CSV.
- **Key fields:**
  - `date`.
  - `branch` FK.
  - `item`, `variation`.
  - `qty_consumed`.
  - `source`: `FOODICS` or `PACKAGING_CSV`.
- **Uniqueness:**
  - One row per `(date, branch, item, variation, source)`.
- **Usage:**
  - Reporting, usage analytics, reordering decisions.

### 5. `SupplierSpendMonthly`
- **Table:** `supplier_spend_monthly`
- **Purpose:** Aggregated monthly spend per supplier (could be managed as a materialized view / summary table).
- **Fields:**
  - `month` (YYYY-MM).
  - `supplier` FK.
  - `total_spent`.

---

## I. Excel Import

### 1. `ImportJob`
- **Table:** `import_jobs`
- **Purpose:** Track high-level Excel/CSV import operations.
- **Fields:**
  - `uploaded_by` FK (`User`).
  - `file_url`.
  - `status`: `Pending`, `Processing`, `Completed`, `Failed`.
  - `error_log`.

### 2. `ImportJobRow`
- **Table:** `import_job_rows`
- **Purpose:** Per-row processing status within an `ImportJob`.
- **Fields:**
  - `import_job` FK.
  - `row_number`.
  - `raw_data_json`.
  - `status`, `error_message`.

---

## J. System Settings

### 1. `SystemSettings`
- **Table:** `system_settings`
- **Purpose:** Global system-wide configuration.
- **Fields:**
  - `request_cutoff_day`: enum Mon–Sun.
  - `request_cutoff_time`: time.
  - `urgent_days`: JSON list (weekdays/date ranges).
  - `timezone`: e.g. `Asia/Dubai`.
- **Usage:**
  - Controls business rules like when branches are allowed to create requests.

---

## High-Level Data Flow Summary

1. **Identity & Access**
   - `User` ↔ `UserProfile` ↔ `Role` define permissions.
   - `BranchUser` links users to branches.

2. **Branch Requests → Warehouse**
   - Branch Manager creates `Request` + `RequestItem`s.
   - Procurement approves (`Request.status = Approved`).
   - Warehouse marks `InProcess`, deducts stock from `StockBalance` and writes `StockLedger` entries (`REQUEST_FULFILLMENT`).

3. **Procurement → Suppliers**
   - Procurement creates `SupplierOrder` + `SupplierOrderItem`s based on needs.
   - Order is sent to supplier; statuses track the lifecycle until `Received`.
   - When marking `Received`, the system increases `StockBalance` at warehouse locations and logs in `StockLedger` (`DELIVERY_RECEIVED`).

4. **Supplier Ready Stock (Item Requests)**
   - `ItemRequest` + `ItemRequestItem` used for lighter notifications / reservations with suppliers.
   - `SupplierStock` records what’s ready at supplier side.

5. **Logistics & Delivery**
   - `Delivery` ties requests to delivery operations.
   - `DeliveryDocument` generates bills.
   - `DeliverySignature` confirms final receipt by branch managers.

6. **Packaging & CSV Consumption**
   - Procurement Manager configures `BranchPackagingItem` & `BranchPackagingRule`/`BranchPackagingRuleItem` per branch and per product (e.g. “Mini Kucu Bucket” = 1 Burger Box).
   - Branch Manager uploads CSV / Excel with `Product` and `Quantity`.
   - System:
     - Matches product name to `BranchPackagingRule`.
     - For each `BranchPackagingRuleItem`, deducts `quantity_per_unit × Quantity` from **branch inventory** (not warehouse).
     - Records per-day usage in `ItemConsumptionDaily` with `source = PACKAGING_CSV`.

7. **Reporting**
   - `StockBalance` + `StockLedger` give inventory snapshots and history.
   - `ItemConsumptionDaily` & `SupplierSpendMonthly` support demand and spend analytics.
   - `IntegrationFoodics` + `FoodicsBranchMapping` allow external sales data to drive consumption records.

This document reflects the current structure in `maainventory/models.py`. Any future model changes should be mirrored here to keep the documentation accurate.

---

## Handover & Developer Guide

This section is for **future developers** taking over the MAA Inventory system. It summarizes architecture, configuration, access control, and important considerations so you can onboard and maintain the system safely.

---

### 1. Mandatory database setup: Roles

The `roles` table **must** contain these six roles (see table in **A. Core Identity & Access → Role** above):

- **Branch Manager**
- **IT**
- **Logistics**
- **Procurement Manager**
- **Supplier User**
- **Warehouse Staff**

**How to add:** Via Django Admin (`/admin/`) → Roles, or a data migration. Without these roles, registration (role dropdown), access control, and sidebar logic may break or behave incorrectly.

---

### 2. Project structure (high level)

| Path | Purpose |
|------|---------|
| `config/` | Django project: `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`. |
| `maainventory/` | Main app: models, views, forms, admin, middleware, context processors, templates. |
| `maainventory/models.py` | All database models (identity, inventory, suppliers, requests, POs, delivery, packaging, integrations). |
| `maainventory/views.py` | Main views (dashboard, login, register, inventory, requests, POs, suppliers, branches, packaging, invoice signing, reports). |
| `maainventory/views_item_requests.py` | Item Request system (request-item, item-requests, supplier-stock, confirm-stock, APIs). |
| `maainventory/forms.py` | RegistrationForm, LoginForm, SupplierForm, ItemForm, SupplierItemForm, PriceDiscussionForm, etc. |
| `maainventory/middleware.py` | `branch_user_access_middleware`: restricts Branch Manager (and branch-assigned users) to allowed URLs. |
| `maainventory/context_processors.py` | `branch_user_context`: exposes `is_branch_user`, `user_branch_ids`, `is_procurement_user`, `is_it_user`, `is_warehouse_staff` to templates. |
| `maainventory/templates/maainventory/` | All HTML templates (base, dashboard, inventory, requests, purchase_orders, branches, packaging, etc.). |
| `static/` | CSS, icons, images (project root). |
| `media/` | User uploads (item photos, signatures, etc.). |
| `docs/` | DATABASE.md, ITEM_REQUEST_SYSTEM.md, design-tokens.md, email/invoice setup docs, TRD.md. |

---

### 3. Environment and configuration

- **`.env`** (project root, do not commit): Used for `DB_*`, optional `USE_SQLITE`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `PORTAL_TOKEN_EXPIRATION_DAYS`. Loaded via `python-dotenv` in `config/settings.py`.
- **Database:** Production uses **PostgreSQL** (settings read `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`). Some setups may use SQLite via `USE_SQLITE`; if present in settings, ensure `DATABASES` is set accordingly.
- **Timezone:** `TIME_ZONE = 'Asia/Dubai'` (UTC+4). All date/time logic should respect this.
- **Email:** SMTP is configured in `config/settings.py` (Gmail or similar). Used for: purchase order/invoice emails to suppliers, item request notifications. **Security:** Move `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` to environment variables in production; do not commit credentials.
- **Secret key:** In production, set `SECRET_KEY` from environment (e.g. `os.getenv('DJANGO_SECRET_KEY')`); do not use the default insecure key from settings.
- **Static/Media:** `STATIC_URL`, `STATICFILES_DIRS`, `MEDIA_URL`, `MEDIA_ROOT` are set; in production use `collectstatic` and serve static/media via the web server.

---

### 4. Access control (roles and URLs)

- **Procurement Manager** and **Warehouse Staff:** Full access to all app URLs (inventory, POs, item requests, supplier stock, suppliers, reports, punch IDs, branches, packaging, etc.).
- **Branch Manager (and users with only branch assignments):** Restricted. They can access: `/`, `/requests/` (except `/requests/new/`), `/branches/`, `/branches/configure/`, `/branches/<id>/packaging/`, `/login/`, `/logout/`, `/register/`. All other paths (e.g. `/inventory/`, `/purchase-orders/`, `/item-requests/`, `/supplier-stock/`, `/suppliers/`, `/reports/`, `/requests/new/`, `/punch-ids/`, `/admin/`) redirect to `requests`.
- **IT:** Identified in context as `is_it_user`; used for Punch ID management visibility/permissions.
- **Logistics / Supplier User:** Role exists; any specific URL restrictions or features should be implemented consistently with the above pattern (middleware + context processor).

**Implementation:** `maainventory/middleware.branch_user_access_middleware` and `maainventory/context_processors.branch_user_context` + `get_branch_user_info()`. Role detection is by **substring** on `profile.role.name` (e.g. `'branch'`, `'procurement'`, `'warehouse'`, `'it'`).

---

### 5. Key URLs and flows (reference)

- **Auth:** `/login/`, `/logout/`, `/register/`.
- **Dashboard:** `/`.
- **Punch IDs (IT):** `/punch-ids/`, add/edit/delete.
- **Inventory:** `/inventory/`, add/edit/delete item, delete item photo.
- **Requests (branch → warehouse):** `/requests/`, `/requests/create/`, `/requests/new/`, `/requests/<id>/`, approve-reject, mark-in-process, mark-delivered.
- **Purchase orders:** `/purchase-orders/`, `/purchase-orders/<id>/`, mark-received, send-receiving-note.
- **Invoices (supplier signing):** `/invoice/<order_id>/`, `/invoice/<order_id>/sign/`, `/invoice/token/<token>/`, `/invoice/token/<token>/sign/`.
- **Item requests:** `/request-item/`, `/item-requests/`, `/item-requests/<id>/`, confirm-stock, `/supplier-stock/`; APIs: `/api/suppliers-for-branch/`, `/api/items-for-supplier/`.
- **Suppliers:** `/suppliers/`, add/edit/delete, update-category; `/api/add-price-discussion/`.
- **Branches:** `/branches/`, `/branches/configure/`, `/branch-assignments/`; per-branch packaging: `/branches/<id>/packaging/`, upload, add-item, save, cancel-draft, process-csv.
- **Reports:** `/reports/`.
- **Admin:** `/admin/`.

---

### 6. Important business flows (short)

- **Branch request lifecycle:** Branch creates Request + RequestItems → Procurement approves/rejects → Warehouse marks In Process (stock deducted from `StockBalance`, `StockLedger` updated) → Logistics/Delivery: Out for Delivery → Delivered → optional Completed.
- **Purchase order lifecycle:** Procurement creates SupplierOrder + SupplierOrderItems → Sent to supplier (email with invoice link) → Supplier signs (PortalToken, SupplierInvoiceSignature) → Order marked Received → warehouse `StockBalance` and `StockLedger` updated.
- **Item request (no invoice):** Procurement creates ItemRequest + ItemRequestItems → Supplier notified by email → Status: Pending → Notified → In Production → Ready → Confirm Stock → items appear in Supplier Stock; status Moved to Stock.
- **Packaging/consumption:** Branch packaging rules (`BranchPackagingRule`, `BranchPackagingRuleItem`) define product → packaging item consumption. CSV upload triggers deductions and `ItemConsumptionDaily` (source PACKAGING_CSV). Foodics integration can also feed consumption (source FOODICS).

---

### 7. Related documentation (in `docs/`)

- **DATABASE.md** (this file): Database schema, relationships, mandatory roles, and handover.
- **ITEM_REQUEST_SYSTEM.md:** Item Request feature (workflow, APIs, statuses, difference from POs).
- **design-tokens.md:** UI/design tokens.
- **EMAIL_SETUP_COMPLETE.md**, **INVOICE_AND_EMAIL_SETUP.md**, **SENDGRID_SETUP_GUIDE.md:** Email and invoice setup.
- **TRD.md:** Likely technical/requirements documentation.

---

### 8. What future developers must consider

1. **Roles:** Always ensure the six required roles exist after migrations or fresh DB. Add a check or data migration if needed.
2. **Secrets:** Never commit `SECRET_KEY`, email passwords, or DB passwords. Use `.env` and environment variables in production.
3. **Migrations:** After changing `maainventory/models.py`, run `python manage.py makemigrations` and `python manage.py migrate`. Keep migrations in version control.
4. **Admin:** All main models are registered in `maainventory/admin.py`. Use Admin for initial data (roles, brands, base units) and debugging.
5. **Branch vs global data:** Branch managers only see data for their assigned branches (`BranchUser`). Views filter Requests, Branches, and packaging by `user_branch_ids` when `is_branch_user` is True.
6. **Stock integrity:** Any change to warehouse stock should update both `StockBalance` and `StockLedger` with the correct `reason` and `reference_type`/`reference_id`.
7. **Email and tokens:** Invoice links use `PortalToken`; token-based URLs allow suppliers to view/sign without logging in. Expiration is configurable (`PORTAL_TOKEN_EXPIRATION_DAYS`).
8. **New roles or permissions:** If you add a role or change who can see what, update both `middleware.py` and `context_processors.py` so that access and UI (e.g. sidebar) stay in sync.
9. **Time zone:** Keep `TIME_ZONE = 'Asia/Dubai'` and use timezone-aware datetimes in code for reporting and cutoffs.
10. **Testing:** Add or extend tests when changing access control, stock logic, or request/PO workflows; the codebase has `maainventory/tests.py`.

---

*End of Handover & Developer Guide.*

