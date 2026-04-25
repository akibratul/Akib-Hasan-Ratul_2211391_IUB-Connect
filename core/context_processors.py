from .models import Notification, Message


def global_context(request):
    """Make unread notification count and unread message count available to all templates."""
    context = {}
    if request.user.is_authenticated:
        context['unread_count'] = Notification.objects.filter(user=request.user, read=False).count()
        context['unread_messages_count'] = Message.objects.filter(receiver=request.user, read=False).count()
    return context
