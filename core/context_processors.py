from .models import Notification


def global_context(request):
    """Make unread notification count available to all templates."""
    context = {}
    if request.user.is_authenticated:
        context['unread_count'] = Notification.objects.filter(user=request.user, read=False).count()
    return context
