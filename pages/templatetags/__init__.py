"""Template tags for pages app."""
from django import template
from pages.models import Message

register = template.Library()


@register.simple_tag
def unread_message_count(user):
    """
    Get the count of unread messages for a user (if organization).
    
    Usage in template: {% unread_message_count request.user %}
    """
    if hasattr(user, 'user_type') and user.user_type == 'organization':
        return Message.get_unread_count(user)
    return 0


@register.simple_tag
def unread_sent_message_count(user):
    """
    Get the count of sent messages not yet read by recipient (if volunteer).
    
    Usage in template: {% unread_sent_message_count request.user %}
    """
    if hasattr(user, 'user_type') and user.user_type == 'student':
        return Message.get_unread_sent_count(user)
    return 0


@register.simple_tag
def message_read_status(message):
    """
    Get human-readable read status of a message.
    
    Usage in template: {% message_read_status message %}
    """
    return message.get_read_status()


@register.inclusion_tag('components/message_badge.html')
def message_badge(user):
    """
    Render a badge showing unread message count.
    
    Usage in template: {% message_badge request.user %}
    """
    count = 0
    if hasattr(user, 'user_type') and user.user_type == 'organization':
        count = Message.get_unread_count(user)
    
    return {
        'count': count,
        'has_unread': count > 0,
    }


@register.inclusion_tag('components/inbox_link.html')
def inbox_link(user, link_text='Inbox'):
    """
    Render an inbox link with unread message badge.
    
    Usage in template: {% inbox_link request.user %} or {% inbox_link request.user "View Messages" %}
    """
    count = 0
    if hasattr(user, 'user_type') and user.user_type == 'organization':
        count = Message.get_unread_count(user)
    
    return {
        'count': count,
        'has_unread': count > 0,
        'link_text': link_text,
    }


@register.inclusion_tag('components/sent_messages_badge.html')
def sent_messages_badge(user):
    """
    Render a badge showing unread sent messages (waiting for recipient to read).
    
    Usage in template: {% sent_messages_badge request.user %}
    """
    unread_count = 0
    total_sent = 0
    
    if hasattr(user, 'user_type') and user.user_type == 'student':
        unread_count = Message.get_unread_sent_count(user)
        total_sent = Message.objects.filter(sender=user).count()
    
    return {
        'unread_count': unread_count,
        'total_sent': total_sent,
        'has_unread': unread_count > 0,
    }


@register.filter
def read_status_badge_class(message):
    """
    Return CSS class for read status badge.
    
    Usage in template: <span class="badge {{ message|read_status_badge_class }}">
    """
    if message.is_read:
        return 'badge-success'
    else:
        return 'badge-warning'


@register.filter
def read_status_icon(message):
    """
    Return icon indicator for read status.
    
    Usage in template: {{ message|read_status_icon }}
    """
    if message.is_read:
        return '✓ Read'
    else:
        return '✗ Unread'
