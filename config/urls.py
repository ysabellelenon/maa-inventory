"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from maainventory import views
from maainventory import views_item_requests

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),
    path("punch-ids/", views.punch_id_management, name="punch_id_management"),
    path("punch-ids/add/", views.punch_id_add, name="punch_id_add"),
    path("punch-ids/<int:punch_id_id>/edit/", views.punch_id_edit, name="punch_id_edit"),
    path("punch-ids/<int:punch_id_id>/delete/", views.punch_id_delete, name="punch_id_delete"),
    path("inventory/", views.inventory, name="inventory"),
    path("inventory/add/", views.add_item, name="add_item"),
    path("inventory/edit/<str:code>/", views.edit_item, name="edit_item"),
    path("inventory/delete/<str:code>/", views.delete_item, name="delete_item"),
    path("inventory/photo/<int:photo_id>/delete/", views.delete_item_photo, name="delete_item_photo"),
    path("invoice/<int:order_id>/", views.view_invoice, name="view_invoice"),
    path("invoice/<int:order_id>/sign/", views.submit_invoice_signature, name="submit_invoice_signature"),
    path("invoice/token/<str:token>/", views.view_invoice_by_token, name="view_invoice_by_token"),
    path("invoice/token/<str:token>/sign/", lambda request, token: views.submit_invoice_signature(request, order_id=None, token=token), name="submit_invoice_signature_by_token"),
    path("requests/", views.requests, name="requests"),
    path("requests/create/", views.create_stock_request, name="create_stock_request"),
    path("requests/<int:request_id>/", views.view_request, name="view_request"),
    path("requests/<int:request_id>/approve-reject/", views.approve_reject_request, name="approve_reject_request"),
    path("requests/<int:request_id>/mark-in-process/", views.mark_request_in_process, name="mark_request_in_process"),
    path("requests/<int:request_id>/mark-delivered/", views.mark_request_delivered, name="mark_request_delivered"),
    path("requests/new/", views.new_request, name="new_request"),
    path("purchase-orders/", views.purchase_orders, name="purchase_orders"),
    path("purchase-orders/<int:order_id>/", views.view_purchase_order, name="view_purchase_order"),
    path("purchase-orders/<int:order_id>/mark-received/", views.mark_order_received, name="mark_order_received"),
    path("purchase-orders/<int:order_id>/send-receiving-note/", views.send_receiving_note, name="send_receiving_note"),
    path("api/suppliers-for-branch/", views_item_requests.api_suppliers_for_branch, name="api_suppliers_for_branch"),
    path("api/items-for-supplier/", views_item_requests.api_items_for_supplier, name="api_items_for_supplier"),
    path("request-item/", views_item_requests.request_item, name="request_item"),
    path("item-requests/", views_item_requests.item_requests, name="item_requests"),
    path("item-requests/<int:request_id>/", views_item_requests.view_item_request, name="view_item_request"),
    path("item-requests/<int:request_id>/confirm-stock/", views_item_requests.confirm_item_stock, name="confirm_item_stock"),
    path("supplier-stock/", views_item_requests.supplier_stock, name="supplier_stock"),
    path("suppliers/", views.suppliers, name="suppliers"),
    path("suppliers/add/", views.add_supplier, name="add_supplier"),
    path("suppliers/edit/<str:code>/", views.edit_supplier, name="edit_supplier"),
    path("suppliers/delete/<str:code>/", views.delete_supplier, name="delete_supplier"),
    path("suppliers/update-category/", views.update_supplier_category, name="update_supplier_category"),
    path("reports/", views.reports, name="reports"),
    path("branch-assignments/", views.manage_branch_assignments, name="manage_branch_assignments"),
    path("branches/", views.branches, name="branches"),
    path("branches/configure/", views.branches_configure, name="branches_configure"),
    path("branches/<int:branch_id>/packaging/", views.branch_packaging, name="branch_packaging"),
    path("branches/<int:branch_id>/packaging/upload/", views.branch_upload_packaging, name="branch_upload_packaging"),
    path("branches/<int:branch_id>/packaging/add-item/", views.branch_add_packaging_item, name="branch_add_packaging_item"),
    path("branches/<int:branch_id>/packaging/save/", views.branch_save_packaging_rules, name="branch_save_packaging_rules"),
    path("branches/<int:branch_id>/packaging/cancel-draft/", views.branch_cancel_packaging_draft, name="branch_cancel_packaging_draft"),
    path("branches/<int:branch_id>/packaging/process-csv/", views.branch_process_packaging_csv, name="branch_process_packaging_csv"),
    path("api/add-price-discussion/", views.add_price_discussion, name="add_price_discussion"),
    path('admin/', admin.site.urls),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
