from django.contrib import admin
from .models import (
    # Core Identity
    Role, UserProfile, ValidPunchID, Brand, Branch, BranchUser,
    # Inventory
    BaseUnit, Item, ItemPhoto, ItemVariation, InventoryLocation, StockBalance, StockLedger,
    # Suppliers & Pricing
    Supplier, SupplierCategory, SupplierItem,
    # Requests
    Request, RequestItem, RequestStatusHistory,
    # Supplier Orders
    SupplierOrder, SupplierOrderItem, PortalToken, SupplierInvoiceSignature,
    # Item Requests
    ItemRequest, ItemRequestItem, SupplierStock,
    # Logistics & Delivery
    Delivery, DeliveryDocument, DeliverySignature,
    # Foodics Integration
    IntegrationFoodics, FoodicsBranchMapping, ItemConsumptionDaily, SupplierSpendMonthly,
    # Excel Import
    ImportJob, ImportJobRow,
    # System Settings
    SystemSettings,
)


# ============================================================================
# A. Core Identity
# ============================================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'full_name', 'user__email']
    raw_id_fields = ['user', 'role']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'is_active', 'created_at']
    list_filter = ['brand', 'is_active', 'created_at']
    search_fields = ['name', 'address']
    raw_id_fields = ['brand']


@admin.register(BranchUser)
class BranchUserAdmin(admin.ModelAdmin):
    list_display = ['branch', 'user', 'created_at']
    list_filter = ['branch', 'created_at']
    search_fields = ['branch__name', 'user__username']
    raw_id_fields = ['branch', 'user']


# ============================================================================
# B. Inventory
# ============================================================================

@admin.register(BaseUnit)
class BaseUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'abbreviation', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'name', 'brand', 'base_unit', 'min_stock_qty', 'is_active', 'created_at']
    list_filter = ['brand', 'is_active', 'base_unit', 'created_at']
    search_fields = ['item_code', 'name', 'description']
    raw_id_fields = ['brand', 'created_by']


@admin.register(ItemPhoto)
class ItemPhotoAdmin(admin.ModelAdmin):
    list_display = ['item', 'photo', 'order', 'uploaded_at']
    list_filter = ['uploaded_at', 'item__brand']
    search_fields = ['item__item_code', 'item__name']
    raw_id_fields = ['item']
    readonly_fields = ['uploaded_at']
    ordering = ['item', 'order', 'uploaded_at']


@admin.register(ItemVariation)
class ItemVariationAdmin(admin.ModelAdmin):
    list_display = ['item', 'variation_name', 'sku', 'is_active']
    list_filter = ['is_active', 'item__brand']
    search_fields = ['variation_name', 'sku', 'item__item_code', 'item__name']
    raw_id_fields = ['item']


@admin.register(InventoryLocation)
class InventoryLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'supplier', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name']
    raw_id_fields = ['supplier']


@admin.register(StockBalance)
class StockBalanceAdmin(admin.ModelAdmin):
    list_display = ['item', 'variation', 'location', 'qty_on_hand', 'updated_at']
    list_filter = ['location', 'updated_at']
    search_fields = ['item__item_code', 'item__name', 'variation__variation_name']
    raw_id_fields = ['item', 'variation', 'location']


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ['item', 'variation', 'qty_change', 'reason', 'reference_type', 'created_at']
    list_filter = ['reason', 'reference_type', 'created_at']
    search_fields = ['item__item_code', 'item__name', 'reference_id', 'notes']
    raw_id_fields = ['item', 'variation', 'from_location', 'to_location', 'created_by']
    readonly_fields = ['created_at']


# ============================================================================
# C. Suppliers & Pricing
# ============================================================================

@admin.register(SupplierCategory)
class SupplierCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'category', 'delivery_days', 'order_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'email', 'phone', 'address']
    raw_id_fields = ['created_by', 'category']


@admin.register(SupplierItem)
class SupplierItemAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'item', 'variation', 'base_unit', 'price_per_unit', 'min_order_qty', 'is_active']
    list_filter = ['is_active', 'supplier', 'base_unit']
    search_fields = ['supplier__name', 'item__item_code', 'item__name']
    raw_id_fields = ['supplier', 'item', 'variation', 'base_unit']


# ============================================================================
# D. Requests
# ============================================================================

class RequestItemInline(admin.TabularInline):
    model = RequestItem
    extra = 1
    raw_id_fields = ['item', 'variation']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['request_code', 'branch', 'requested_by', 'status', 'date_of_order', 'created_at']
    list_filter = ['status', 'branch__brand', 'created_at']
    search_fields = ['request_code', 'branch__name', 'requested_by__username']
    raw_id_fields = ['branch', 'requested_by', 'approved_by']
    inlines = [RequestItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['request', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at']
    search_fields = ['request__request_code']
    raw_id_fields = ['request', 'changed_by']
    readonly_fields = ['changed_at']


# ============================================================================
# E. Supplier Orders
# ============================================================================

class SupplierOrderItemInline(admin.TabularInline):
    model = SupplierOrderItem
    extra = 1
    raw_id_fields = ['item', 'variation']


@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = ['po_code', 'supplier', 'status', 'requested_delivery_date', 'hold_at_supplier', 'created_at']
    list_filter = ['status', 'hold_at_supplier', 'created_at']
    search_fields = ['po_code', 'supplier__name']
    raw_id_fields = ['supplier', 'created_by']
    inlines = [SupplierOrderItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PortalToken)
class PortalTokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'supplier', 'supplier_order', 'expires_at', 'used_at', 'created_at']
    list_filter = ['used_at', 'expires_at', 'created_at']
    search_fields = ['token', 'supplier__name', 'supplier_order__po_code']
    raw_id_fields = ['supplier', 'supplier_order']
    readonly_fields = ['created_at']


@admin.register(SupplierInvoiceSignature)
class SupplierInvoiceSignatureAdmin(admin.ModelAdmin):
    list_display = ['supplier_order', 'supplier_name_signed', 'signed_at']
    list_filter = ['signed_at']
    search_fields = ['supplier_order__po_code', 'supplier_name_signed']
    raw_id_fields = ['supplier_order', 'token']
    readonly_fields = ['signed_at']


class ItemRequestItemInline(admin.TabularInline):
    model = ItemRequestItem
    extra = 1
    raw_id_fields = ['item', 'variation']


@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ['request_code', 'supplier', 'status', 'delivery_days_min', 'delivery_days_max', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['request_code', 'supplier__name']
    raw_id_fields = ['supplier', 'created_by']
    inlines = [ItemRequestItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SupplierStock)
class SupplierStockAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'item', 'quantity', 'confirmed_by', 'confirmed_at']
    list_filter = ['supplier', 'confirmed_at']
    search_fields = ['supplier__name', 'item__item_code', 'item__name']
    raw_id_fields = ['item_request', 'supplier', 'item', 'variation', 'confirmed_by']
    readonly_fields = ['confirmed_at']


# ============================================================================
# F. Logistics & Delivery
# ============================================================================

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['delivery_code', 'request', 'logistics_user', 'status', 'delivered_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['delivery_code', 'request__request_code']
    raw_id_fields = ['request', 'logistics_user']
    readonly_fields = ['created_at']


@admin.register(DeliveryDocument)
class DeliveryDocumentAdmin(admin.ModelAdmin):
    list_display = ['request', 'document_type', 'generated_at', 'generated_by_system']
    list_filter = ['document_type', 'generated_by_system', 'generated_at']
    search_fields = ['request__request_code']
    raw_id_fields = ['request']
    readonly_fields = ['generated_at']


@admin.register(DeliverySignature)
class DeliverySignatureAdmin(admin.ModelAdmin):
    list_display = ['request', 'branch_manager', 'signed_name', 'signed_at']
    list_filter = ['signed_at']
    search_fields = ['request__request_code', 'signed_name', 'branch_manager__username']
    raw_id_fields = ['request', 'branch_manager']
    readonly_fields = ['signed_at']


# ============================================================================
# G. Foodics Integration
# ============================================================================

@admin.register(IntegrationFoodics)
class IntegrationFoodicsAdmin(admin.ModelAdmin):
    list_display = ['is_enabled', 'last_sync_at', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    readonly_fields = ['created_at']


@admin.register(FoodicsBranchMapping)
class FoodicsBranchMappingAdmin(admin.ModelAdmin):
    list_display = ['branch', 'foodics_branch_external_id']
    search_fields = ['branch__name', 'foodics_branch_external_id']
    raw_id_fields = ['branch']


@admin.register(ItemConsumptionDaily)
class ItemConsumptionDailyAdmin(admin.ModelAdmin):
    list_display = ['date', 'branch', 'item', 'variation', 'qty_consumed', 'source', 'created_at']
    list_filter = ['date', 'source', 'created_at']
    search_fields = ['branch__name', 'item__item_code', 'item__name']
    raw_id_fields = ['branch', 'item', 'variation']
    readonly_fields = ['created_at']


@admin.register(SupplierSpendMonthly)
class SupplierSpendMonthlyAdmin(admin.ModelAdmin):
    list_display = ['month', 'supplier', 'total_spent']
    list_filter = ['month', 'supplier']
    search_fields = ['supplier__name']
    raw_id_fields = ['supplier']


# ============================================================================
# H. Excel Import
# ============================================================================

class ImportJobRowInline(admin.TabularInline):
    model = ImportJobRow
    extra = 0
    readonly_fields = ['row_number', 'status', 'error_message']


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_by', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['uploaded_by__username']
    raw_id_fields = ['uploaded_by']
    inlines = [ImportJobRowInline]
    readonly_fields = ['created_at']


# ============================================================================
# I. System Settings
# ============================================================================

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['request_cutoff_day', 'request_cutoff_time', 'timezone', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
