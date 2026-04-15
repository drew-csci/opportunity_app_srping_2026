"""Utility functions for pages app."""
from .models import Message


def get_unread_message_badge_data(organization):
    """
    Get badge data for displaying unread message count.
    
    Args:
        organization: The organization User object
        
    Returns:
        dict: Contains 'count' and 'has_unread' for template rendering
        
    Example:
        badge_data = get_unread_message_badge_data(request.user)
        if badge_data['has_unread']:
            # Display badge with badge_data['count']
    """
    unread_count = Message.get_unread_count(organization)
    return {
        'count': unread_count,
        'has_unread': unread_count > 0,
    }


def get_inbox_link_with_badge(organization, url_name='organization_inbox'):
    """
    Generate inbox link data with unread badge information.
    
    Args:
        organization: The organization User object
        url_name: The URL name for the inbox (default: 'organization_inbox')
        
    Returns:
        dict: Contains badge_data and url_name for rendering inbox link
    """
    badge_data = get_unread_message_badge_data(organization)
    return {
        'badge_data': badge_data,
        'url_name': url_name,
    }
