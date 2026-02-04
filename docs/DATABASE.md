# Database Documentation – MAA Inventory

This document explains the **database structure**, **relationships**, and **business meaning** of all models in `maainventory/models.py`.

---

## A. Core Identity & Access

### 1. `Role`
- **Table:** `roles`
- **Purpose:** Defines user roles, e.g. `ProcurementManager`, `BranchManager`, `WarehouseStaff`, `Logistics`, `SupplierUser`, `IT`, etc.
- **Key fields:**
  - `name` (unique): human-readable role name.
- **Usage:**
  - Attached to `UserProfile.role`.
  - Used in views, context processors, and middleware to control access:
    - Procurement manager and warehouse staff get full access.
    - Branch managers have restricted views (branch-only requests, branches, etc.).

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

