"""
Context processors for template context.
"""


def get_branch_user_info(user):
    """
    Return (is_branch_user, user_branch_ids) for a user.
    Branch users (restricted view): role contains "Branch" (e.g. BranchManager) OR has BranchUser assignments.
    Procurement Manager and Warehouse Staff always get full access - see all branches and all requests.
    """
    is_branch_user = False
    user_branch_ids = []

    if user and user.is_authenticated:
        profile = getattr(user, 'profile', None)
        role_name = (profile.role.name if profile and profile.role else '').lower()
        has_procurement_role = 'procurement' in role_name
        has_warehouse_role = 'warehouse' in role_name
        has_branch_role = 'branch' in role_name
        branch_assignments = getattr(user, 'branch_assignments', None)
        has_assignments = branch_assignments.exists() if branch_assignments else False

        # Procurement Manager and Warehouse Staff see everything - never restrict
        if has_procurement_role or has_warehouse_role:
            return False, []

        if has_branch_role or has_assignments:
            is_branch_user = True
            if branch_assignments:
                user_branch_ids = list(
                    branch_assignments.values_list('branch_id', flat=True)
                )

    return is_branch_user, user_branch_ids


def branch_user_context(request):
    """
    Add is_branch_user, user_branch_ids, is_procurement_user, is_warehouse_staff to template context.
    Branch users (restricted): role contains "Branch" (e.g. BranchManager) OR has BranchUser assignments.
    Procurement Manager and Warehouse Staff get appropriate full access.
    """
    is_branch_user, user_branch_ids = get_branch_user_info(request.user)
    is_procurement_user = False
    is_it_user = False
    is_warehouse_staff = False
    is_branch_manager = False
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        role_name = (profile.role.name if profile and profile.role else '').lower()
        is_procurement_user = 'procurement' in role_name
        is_it_user = 'it' in role_name or role_name == 'it'
        is_warehouse_staff = 'warehouse' in role_name
        is_branch_manager = 'branch' in role_name and not is_procurement_user and not is_warehouse_staff
    return {
        'is_branch_user': is_branch_user,
        'user_branch_ids': user_branch_ids,
        'is_procurement_user': is_procurement_user,
        'is_it_user': is_it_user,
        'is_warehouse_staff': is_warehouse_staff,
        'is_branch_manager': is_branch_manager,
    }
