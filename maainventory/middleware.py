"""
Middleware for access control.
"""

from django.shortcuts import redirect


# Path prefixes that branch users are NOT allowed to access (they only see Requests and Branches)
BRANCH_USER_FORBIDDEN_PREFIXES = (
    '/inventory/',
    '/purchase-orders/',
    '/item-requests/',
    '/supplier-stock/',
    '/suppliers/',
    '/reports/',
    '/requests/new/',
    '/punch-ids/',
    '/admin/',
)


def branch_user_access_middleware(get_response):
    """
    Block branch users from accessing pages other than Dashboard, Requests, and Branches.
    They can only access: /, /requests/, /requests/<id>/, /branches/, /branches/configure/,
    /branches/<id>/packaging/, /login/, /logout/, /register/.
    
    Procurement Managers and Warehouse Staff have full access to all pages.
    """
    def middleware(request):
        if not request.user.is_authenticated:
            return get_response(request)

        # Check if user is a branch user (restricted). Procurement Manager and Warehouse Staff always get full access.
        profile = getattr(request.user, 'profile', None)
        role_name = (profile.role.name if profile and profile.role else '').lower()
        has_procurement_role = 'procurement' in role_name
        has_warehouse_role = 'warehouse' in role_name
        has_branch_role = 'branch' in role_name
        branch_assignments = getattr(request.user, 'branch_assignments', None)
        has_assignments = branch_assignments.exists() if branch_assignments else False
        # Procurement Manager and Warehouse Staff see everything - never restrict
        is_branch_user = (has_branch_role or has_assignments) and not has_procurement_role and not has_warehouse_role

        if not is_branch_user:
            return get_response(request)

        path = request.path

        # Block forbidden paths first - redirect to requests
        for prefix in BRANCH_USER_FORBIDDEN_PREFIXES:
            if path.startswith(prefix):
                return redirect('requests')

        # Allow: /, /requests/ (except /requests/new/), /branches/, /login, /logout, /register, static, media
        if path == '/' or path.startswith('/branches/'):
            return get_response(request)
        if path.startswith('/requests/') and not path.startswith('/requests/new/'):
            return get_response(request)
        if path in ('/login/', '/logout/', '/register/'):
            return get_response(request)
        if path.startswith('/static/') or path.startswith('/media/'):
            return get_response(request)

        return get_response(request)

    return middleware
