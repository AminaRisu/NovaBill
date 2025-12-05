from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.core.exceptions import PermissionDenied

def group_required(group_names):
    if isinstance(group_names, str):
        group_names = [group_names]
    def in_groups(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
            if bool(u.groups.filter(name__in=group_names)):
                return True
        return False
    return user_passes_test(in_groups)
