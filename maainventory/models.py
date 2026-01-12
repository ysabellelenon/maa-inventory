from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid


# ============================================================================
# A. Core Identity
# ============================================================================

class Role(models.Model):
    """User roles: ProcurementManager, BranchManager, WarehouseStaff, Logistics, SupplierUser"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ValidPunchID(models.Model):
    """Valid Punch IDs that IT can manage - users can only register with approved Punch IDs"""
    punch_id = models.CharField(max_length=100, unique=True, help_text='Employee Punch ID')
    employee_name = models.CharField(max_length=255, null=True, blank=True, help_text='Employee name (optional)')
    is_active = models.BooleanField(default=True, help_text='Whether this Punch ID is active and can be used for registration')
    notes = models.TextField(null=True, blank=True, help_text='Additional notes about this Punch ID')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_punch_ids')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'valid_punch_ids'
        ordering = ['punch_id']
        verbose_name = 'Valid Punch ID'
        verbose_name_plural = 'Valid Punch IDs'
    
    def __str__(self):
        return f"{self.punch_id} - {self.employee_name or 'Unnamed'}"


class UserProfile(models.Model):
    """Extends Django's built-in User model with role, full_name, and punch_id"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    full_name = models.CharField(max_length=255)
    punch_id = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text='Employee Punch ID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.full_name} ({self.user.username})"


class Brand(models.Model):
    """Restaurant brands: Thoum, Boom, Kucu, Cartoon, Mishmishah"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'brands'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Branch(models.Model):
    """Branches associated with brands (e.g., Kucu Sohar Gate)"""
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='branches')
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'branches'
        ordering = ['brand', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.brand.name})"


class BranchUser(models.Model):
    """Many-to-many relationship: Users can belong to multiple branches"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='branch_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'branch_users'
        unique_together = ['branch', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.branch.name}"


# ============================================================================
# B. Inventory
# ============================================================================

class BaseUnit(models.Model):
    """Base units for items (e.g., pcs, kg, box, liter, etc.)"""
    name = models.CharField(max_length=50, unique=True, help_text='Unit name (e.g., pcs, kg, box)')
    abbreviation = models.CharField(max_length=10, unique=True, help_text='Abbreviation (e.g., pcs, kg, bx)')
    description = models.TextField(null=True, blank=True, help_text='Optional description of the unit')
    is_active = models.BooleanField(default=True, help_text='Is this unit active?')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'base_units'
        ordering = ['name']
        verbose_name = 'Base Unit'
        verbose_name_plural = 'Base Units'
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Item(models.Model):
    """Inventory items with base unit, min order qty, and stock thresholds"""
    item_code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='items')
    base_unit = models.CharField(max_length=50)  # pcs, kg, box, etc.
    min_order_qty = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    min_stock_qty = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Price per unit for this item')
    photo_url = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    branches = models.ManyToManyField('Branch', related_name='items', blank=True, help_text='Branches that use this item')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'items'
        ordering = ['item_code']
    
    def __str__(self):
        return f"{self.item_code} - {self.name}"


class ItemPhoto(models.Model):
    """Multiple photos for an item (maximum 5 per item)"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='item_photos/', help_text='Photo for this item')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0, help_text='Display order for photos')
    
    class Meta:
        db_table = 'item_photos'
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Photo for {self.item.name}"


class ItemVariation(models.Model):
    """Item variations (e.g., Yellow, Blue, 5 Seasons)"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='variations')
    variation_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'item_variations'
        unique_together = ['item', 'variation_name']
    
    def __str__(self):
        return f"{self.item.item_code} - {self.variation_name}"


class InventoryLocation(models.Model):
    """Warehouse vs Supplier Hold locations"""
    class LocationType(models.TextChoices):
        WAREHOUSE = 'WAREHOUSE', 'Warehouse'
        SUPPLIER_HOLD = 'SUPPLIER_HOLD', 'Supplier Hold'
    
    type = models.CharField(max_length=20, choices=LocationType.choices)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, null=True, blank=True, related_name='hold_locations')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_locations'
    
    def __str__(self):
        return self.name


class StockBalance(models.Model):
    """One row per item/variation per location"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stock_balances')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_balances')
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE, related_name='stock_balances')
    qty_on_hand = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_balances'
        unique_together = ['item', 'variation', 'location']
    
    def __str__(self):
        var_str = f" - {self.variation.variation_name}" if self.variation else ""
        return f"{self.item.item_code}{var_str} @ {self.location.name}: {self.qty_on_hand}"


class StockLedger(models.Model):
    """Audit log for all stock movements"""
    class ReasonType(models.TextChoices):
        DELIVERY_RECEIVED = 'DELIVERY_RECEIVED', 'Delivery Received'
        REQUEST_FULFILLMENT = 'REQUEST_FULFILLMENT', 'Request Fulfillment'
        ADJUSTMENT_DAMAGE = 'ADJUSTMENT_DAMAGE', 'Adjustment - Damage'
        ADJUSTMENT_VARIANCE = 'ADJUSTMENT_VARIANCE', 'Adjustment - Variance'
        TRANSFER_SUPPLIER_TO_WAREHOUSE = 'TRANSFER_SUPPLIER_TO_WAREHOUSE', 'Transfer Supplier to Warehouse'
        OTHER = 'OTHER', 'Other'
    
    class ReferenceType(models.TextChoices):
        REQUEST = 'REQUEST', 'Request'
        SUPPLIER_ORDER = 'SUPPLIER_ORDER', 'Supplier Order'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'
        IMPORT = 'IMPORT', 'Import'
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ledger_entries')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='ledger_entries')
    from_location = models.ForeignKey(InventoryLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_ledger_entries')
    to_location = models.ForeignKey(InventoryLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_ledger_entries')
    qty_change = models.DecimalField(max_digits=10, decimal_places=2)  # positive or negative
    reason = models.CharField(max_length=50, choices=ReasonType.choices)
    reference_type = models.CharField(max_length=20, choices=ReferenceType.choices, null=True, blank=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True)  # UUID or INT
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ledger_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_ledger'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.item.item_code} - {self.qty_change} ({self.reason})"


# ============================================================================
# C. Suppliers & Pricing
# ============================================================================

class SupplierCategory(models.Model):
    """Supplier category"""
    name = models.CharField(max_length=100, unique=True, help_text='Category name (e.g., Packaging, Food, Beverage)')
    description = models.TextField(null=True, blank=True, help_text='Optional description of the category')
    is_active = models.BooleanField(default=True, help_text='Is this category active?')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'supplier_categories'
        ordering = ['name']
        verbose_name = 'Supplier Category'
        verbose_name_plural = 'Supplier Categories'
    
    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Supplier information"""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField(null=True, blank=True)
    category = models.ForeignKey(SupplierCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='suppliers', help_text='Supplier category')
    contact_person = models.CharField(max_length=255, null=True, blank=True, help_text='Primary contact person name')
    delivery_days = models.JSONField(default=dict, help_text='JSON object with delivery days as keys and cutoff times as values (e.g., {"Monday": "14:00", "Tuesday": "15:00"})')
    order_days = models.JSONField(default=dict, help_text='JSON object with order days as keys and cutoff times as values (e.g., {"Monday": "17:00", "Wednesday": "18:00"})')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_suppliers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SupplierItem(models.Model):
    """Many-to-many: Suppliers can supply items with pricing"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='supplier_items')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='supplier_items')
    item_code = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text='Auto-generated item code based on category')
    base_unit = models.ForeignKey('BaseUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='supplier_items', help_text='Base unit for this supplier item')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    min_order_qty = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    lead_time_days = models.IntegerField(null=True, blank=True, default=0, help_text='Lead time in days for orders from this supplier')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_item_code(self):
        """Generate item code based on supplier category"""
        if not self.supplier or not self.supplier.category:
            return None
        
        category_name = self.supplier.category.name.upper()
        
        # Map category to prefix
        category_prefixes = {
            'PACKAGING': 'PKG',
            'FOOD': 'FOOD',
            'BEVERAGE': 'BEV',
            'EQUIPMENT': 'EQP',
            'CLEANING SUPPLIES': 'CLN',
            'OTHER': 'OTH',
        }
        
        # Get prefix (default to first 3 letters if not in mapping)
        prefix = category_prefixes.get(category_name, category_name[:3].upper())
        
        # Get the next number based on existing SupplierItems with same prefix
        # Check for existing item_codes and find the highest number
        existing_codes = SupplierItem.objects.filter(
            item_code__startswith=f'{prefix}-'
        ).exclude(item_code__isnull=True).exclude(item_code='').values_list('item_code', flat=True)
        
        max_number = 0
        for code in existing_codes:
            try:
                # Extract number from code (e.g., "PKG-0001" -> 1)
                number = int(code.split('-')[1])
                if number > max_number:
                    max_number = number
            except (ValueError, IndexError):
                continue
        
        next_number = max_number + 1
        
        # Format with leading zeros (4 digits)
        return f"{prefix}-{next_number:04d}"
    
    class Meta:
        db_table = 'supplier_items'
        unique_together = ['supplier', 'item', 'variation']
    
    def __str__(self):
        var_str = f" - {self.variation.variation_name}" if self.variation else ""
        return f"{self.supplier.name} - {self.item.item_code}{var_str}"


# ============================================================================
# D. Requests (Branch → Procurement → Warehouse → Logistics)
# ============================================================================

class Request(models.Model):
    """Branch requests for inventory"""
    class StatusType(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        UNDER_REVIEW = 'UnderReview', 'Under Review'
        APPROVED = 'Approved', 'Approved'
        REJECTED = 'Rejected', 'Rejected'
        IN_PROCESS = 'InProcess', 'In Process'
        OUT_FOR_DELIVERY = 'OutForDelivery', 'Out for Delivery'
        DELIVERED = 'Delivered', 'Delivered'
        COMPLETED = 'Completed', 'Completed'
    
    request_code = models.CharField(max_length=50, unique=True)  # e.g., REQ-2026-0012
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_orders')
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.PENDING)
    date_of_order = models.DateTimeField()
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_code} - {self.branch.name}"


class RequestItem(models.Model):
    """Items requested in a request"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='request_items')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='request_items')
    qty_requested = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    qty_approved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    qty_fulfilled = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'request_items'
    
    def __str__(self):
        return f"{self.request.request_code} - {self.item.item_code}"


class RequestStatusHistory(models.Model):
    """History of status changes for requests"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='status_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'request_status_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.request.request_code}: {self.old_status} → {self.new_status}"


# ============================================================================
# E. Supplier Orders (PO) & Invoice Signing
# ============================================================================

class SupplierOrder(models.Model):
    """Purchase orders to suppliers"""
    class StatusType(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        SENT = 'Sent', 'Sent'
        SIGNED = 'Signed', 'Signed'
        CONFIRMED = 'Confirmed', 'Confirmed'
        IN_PRODUCTION = 'InProduction', 'In Production'
        READY = 'Ready', 'Ready'
        PARTIALLY_RECEIVED = 'PartiallyReceived', 'Partially Received'
        RECEIVED = 'Received', 'Received'
        ON_HOLD = 'OnHold', 'On Hold'
        CANCELLED = 'Cancelled', 'Cancelled'
    
    po_code = models.CharField(max_length=50, unique=True)  # PO-YYYY-####
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_orders')
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.DRAFT)
    requested_delivery_date = models.DateField(null=True, blank=True)
    hold_at_supplier = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'supplier_orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.po_code} - {self.supplier.name}"


class SupplierOrderItem(models.Model):
    """Items in a supplier order"""
    supplier_order = models.ForeignKey(SupplierOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_items')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='order_items')
    qty_ordered = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    qty_received = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    expected_delivery_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'supplier_order_items'
    
    def __str__(self):
        return f"{self.supplier_order.po_code} - {self.item.item_code}"


class PortalToken(models.Model):
    """Secure supplier access links for invoice signing"""
    token = models.CharField(max_length=255, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='portal_tokens')
    supplier_order = models.ForeignKey(SupplierOrder, on_delete=models.CASCADE, related_name='portal_tokens')
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'portal_tokens'
    
    def __str__(self):
        return f"Token for {self.supplier_order.po_code}"


class SupplierInvoiceSignature(models.Model):
    """Supplier invoice signatures"""
    supplier_order = models.ForeignKey(SupplierOrder, on_delete=models.CASCADE, related_name='invoice_signatures')
    supplier_name_signed = models.CharField(max_length=255)
    signature_file_url = models.URLField(null=True, blank=True)
    signature_data = models.TextField(null=True, blank=True)  # Base64 encoded signature
    invoice_file_url = models.URLField(null=True, blank=True)
    signed_at = models.DateTimeField()
    token = models.ForeignKey(PortalToken, on_delete=models.SET_NULL, null=True, related_name='signatures')
    
    class Meta:
        db_table = 'supplier_invoice_signatures'
    
    def __str__(self):
        return f"Invoice signature for {self.supplier_order.po_code}"


class ItemRequest(models.Model):
    """Item requests to suppliers (no invoice, just notification)"""
    class StatusType(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        NOTIFIED = 'Notified', 'Notified'
        IN_PRODUCTION = 'InProduction', 'In Production'
        READY = 'Ready', 'Ready'
        MOVED_TO_STOCK = 'MovedToStock', 'Moved to Stock'
        CANCELLED = 'Cancelled', 'Cancelled'
    
    request_code = models.CharField(max_length=50, unique=True)  # REQ-YYYY-####
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='item_requests')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_item_requests')
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.PENDING)
    delivery_days_min = models.IntegerField(validators=[MinValueValidator(1)], help_text='Minimum delivery days (e.g., 50)')
    delivery_days_max = models.IntegerField(validators=[MinValueValidator(1)], help_text='Maximum delivery days (e.g., 70)')
    notes = models.TextField(null=True, blank=True, help_text='Additional notes for supplier')
    email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'item_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_code} - {self.supplier.name}"


class ItemRequestItem(models.Model):
    """Items in an item request"""
    item_request = models.ForeignKey(ItemRequest, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_request_items')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='item_request_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'item_request_items'
    
    def __str__(self):
        return f"{self.item_request.request_code} - {self.item.item_code}"


class SupplierStock(models.Model):
    """Items that are ready in supplier stock"""
    item_request = models.ForeignKey(ItemRequest, on_delete=models.CASCADE, related_name='stock_items', null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='stock_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='supplier_stock')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='supplier_stock')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='confirmed_stock')
    confirmed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'supplier_stock'
        ordering = ['-confirmed_at']
    
    def __str__(self):
        return f"{self.supplier.name} - {self.item.item_code} ({self.quantity})"


# ============================================================================
# F. Logistics, Delivery & Billing
# ============================================================================

class Delivery(models.Model):
    """Delivery tracking"""
    class StatusType(models.TextChoices):
        ASSIGNED = 'Assigned', 'Assigned'
        OUT_FOR_DELIVERY = 'OutForDelivery', 'Out for Delivery'
        DELIVERED = 'Delivered', 'Delivered'
    
    delivery_code = models.CharField(max_length=50, unique=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='deliveries')
    logistics_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.ASSIGNED)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'deliveries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.delivery_code} - {self.request.request_code}"


class DeliveryDocument(models.Model):
    """Auto-generated bills"""
    class DocumentType(models.TextChoices):
        BILL = 'BILL', 'Bill'
    
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=10, choices=DocumentType.choices)
    document_url = models.URLField()
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by_system = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'delivery_documents'
    
    def __str__(self):
        return f"{self.document_type} for {self.request.request_code}"


class DeliverySignature(models.Model):
    """Branch manager signatures for delivery confirmation"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='delivery_signatures')
    branch_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='delivery_signatures')
    signed_name = models.CharField(max_length=255)
    signature_file_url = models.URLField(null=True, blank=True)
    signature_data = models.TextField(null=True, blank=True)  # Base64 encoded signature
    signed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'delivery_signatures'
    
    def __str__(self):
        return f"Signature for {self.request.request_code} by {self.signed_name}"


# ============================================================================
# G. Reports & Foodics Integration
# ============================================================================

class IntegrationFoodics(models.Model):
    """Foodics API integration settings"""
    is_enabled = models.BooleanField(default=False)
    api_key_encrypted = models.TextField(null=True, blank=True)
    oauth_token_encrypted = models.TextField(null=True, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'integrations_foodics'
        verbose_name_plural = 'Foodics Integrations'
    
    def __str__(self):
        return f"Foodics Integration ({'Enabled' if self.is_enabled else 'Disabled'})"


class FoodicsBranchMapping(models.Model):
    """Mapping between branches and Foodics external IDs"""
    branch = models.OneToOneField(Branch, on_delete=models.CASCADE, related_name='foodics_mapping')
    foodics_branch_external_id = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'foodics_branch_mapping'
    
    def __str__(self):
        return f"{self.branch.name} → Foodics ID: {self.foodics_branch_external_id}"


class ItemConsumptionDaily(models.Model):
    """Computed daily consumption from Foodics sales"""
    class SourceType(models.TextChoices):
        FOODICS = 'FOODICS', 'Foodics'
    
    date = models.DateField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='consumption_records')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='consumption_records')
    variation = models.ForeignKey(ItemVariation, on_delete=models.CASCADE, null=True, blank=True, related_name='consumption_records')
    qty_consumed = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    source = models.CharField(max_length=20, choices=SourceType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'item_consumption_daily'
        unique_together = ['date', 'branch', 'item', 'variation', 'source']
        ordering = ['-date', 'branch']
    
    def __str__(self):
        return f"{self.date} - {self.branch.name} - {self.item.item_code}: {self.qty_consumed}"


class SupplierSpendMonthly(models.Model):
    """Monthly supplier spending report (optional materialized table)"""
    month = models.CharField(max_length=7)  # YYYY-MM
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='monthly_spend')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'supplier_spend_monthly'
        unique_together = ['month', 'supplier']
        ordering = ['-month', 'supplier']
    
    def __str__(self):
        return f"{self.month} - {self.supplier.name}: {self.total_spent}"


# ============================================================================
# H. Excel Import
# ============================================================================

class ImportJob(models.Model):
    """Excel import job tracking"""
    class StatusType(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        PROCESSING = 'Processing', 'Processing'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='import_jobs')
    file_url = models.URLField()
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.PENDING)
    error_log = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'import_jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Import Job #{self.id} - {self.status}"


class ImportJobRow(models.Model):
    """Individual row processing for import jobs"""
    import_job = models.ForeignKey(ImportJob, on_delete=models.CASCADE, related_name='rows')
    row_number = models.IntegerField()
    raw_data_json = models.JSONField()
    status = models.CharField(max_length=50)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'import_job_rows'
        unique_together = ['import_job', 'row_number']
    
    def __str__(self):
        return f"Import Job #{self.import_job.id} - Row {self.row_number}"


# ============================================================================
# I. System Settings
# ============================================================================

class SystemSettings(models.Model):
    """System-wide settings"""
    class CutoffDay(models.TextChoices):
        MONDAY = 'Monday', 'Monday'
        TUESDAY = 'Tuesday', 'Tuesday'
        WEDNESDAY = 'Wednesday', 'Wednesday'
        THURSDAY = 'Thursday', 'Thursday'
        FRIDAY = 'Friday', 'Friday'
        SATURDAY = 'Saturday', 'Saturday'
        SUNDAY = 'Sunday', 'Sunday'
    
    request_cutoff_day = models.CharField(max_length=10, choices=CutoffDay.choices)
    request_cutoff_time = models.TimeField()
    urgent_days = models.JSONField(default=list)  # Array of weekdays or date ranges
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"System Settings (Cutoff: {self.request_cutoff_day} at {self.request_cutoff_time})"
