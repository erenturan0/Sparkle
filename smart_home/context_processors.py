from .models import DeviceShareRequest


def pending_requests(request):
    """Navbar'daki bildirim badge'i için bekleyen istek sayısını sağlar."""
    if request.user.is_authenticated:
        count = DeviceShareRequest.objects.filter(
            owner=request.user,
            status=DeviceShareRequest.Status.PENDING,
        ).count()
        return {"pending_request_count": count}
    return {"pending_request_count": 0}
