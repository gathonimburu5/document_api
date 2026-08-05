from apps.audits.models import AuditLog

class AuditService:
    @staticmethod
    def log(*, user=None, request=None, action, description, status=True, metadata=None):
        """ Logs an action performed by a user. """
        if metadata is None:
            metadata = {}
        AuditLog.objects.create(
            user=user,
            action=action,
            description=description,
            method=request.method if request else "",
            endpoint=request.path if request else "",
            ip_address=AuditService.get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
            status=status,
            metadata=metadata or {}
        )

    @staticmethod
    def get_client_ip(request):
        """ Retrieves the client's IP address from the request. """
        if not request:
            return None
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].split()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip