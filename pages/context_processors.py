"""Context processors for pages app."""
from .models import Message


def organization_unread_messages(request):
    """
    Context processor to add unread message count for organization and volunteer users.
    This makes unread_message_count and volunteer_sent_message_stats available in all templates.
    
    For organizations: unread_message_count (count of unread messages received)
    For volunteers: volunteer_unread_sent_count (count of sent messages not yet read)
    """
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'user_type'):
        if request.user.user_type == 'organization':
            # For organizations: show unread messages they have received
            context['unread_message_count'] = Message.get_unread_count(request.user)
        elif request.user.user_type == 'student':
            # For volunteers: show unread sent messages (messages they sent that haven't been read)
            context['volunteer_unread_sent_count'] = Message.get_unread_sent_count(request.user)
            context['volunteer_total_sent'] = Message.objects.filter(sender=request.user).count()
    
    return context
