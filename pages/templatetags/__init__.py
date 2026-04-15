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
