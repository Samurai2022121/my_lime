from rest_framework.permissions import BasePermission


def deny__all(perm, request, view):
    return False


def allow_all(perm, request, view):
    return True


def allow_authenticated(perm, request, view):
    return request.user.is_authenticated


def allow_admin(perm, request, view):
    return request.user.is_superuser


def allow_staff(perm, request, view):
    return request.user.is_staff or request.user.is_superuser


class ActionPermission(BasePermission):
    """
    Allows combining custom functions with explicit actions. Actions could be
    ‘list’, ‘retrieve’, ‘create’, ‘update’, ‘partial_update’, ‘destroy’,
    extra (custom), or ‘default’.
    """

    def __init__(self, **kwargs):
        # bind functions passed in kwargs to the object
        for name, func in kwargs.items():
            setattr(self, f"perm_{name}", func.__get__(self, self.__class__))

    def __call__(self):
        """
        So the object could be used in `permission_classes` iterable
        instead of a class.
        """
        return self

    def perm_default(self, request, view):
        """Denies access by default. May be overridden on init."""
        return False

    def has_permission(self, request, view):
        action = getattr(view, "action", "default")
        if action is None:  # for browsable API
            return True
        return getattr(self, f"perm_{action}", self.perm_default)(request, view)


class ReadWritePermission(ActionPermission):
    """Shortcut for read/write permissions."""

    def __init__(self, read=None, write=None, **kwargs):
        if read:
            kwargs.setdefault("list", read)
            kwargs.setdefault("retrieve", read)
        if write:
            kwargs.setdefault("create", write)
            kwargs.setdefault("destroy", write)
            kwargs.setdefault("update", write)
            kwargs.setdefault("partial_update", write)
        super().__init__(**kwargs)
