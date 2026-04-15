"""Context processors for pages app."""
from .models import Message


def organization_unread_messages(request):
    """
    Context processor to add unread message count for organization users.
    This makes unread_message_count available in all templates for organizations.
    
    Usage in template: {{ unread_message_count }}
    """
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'user_type'):
        if request.user.user_type == 'organization':
            context['unread_message_count'] = Message.get_unread_count(request.user)
    
    return context
