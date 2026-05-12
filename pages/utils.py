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


def get_volunteer_message_stats(volunteer):
    """
    Get message statistics for a volunteer (sender).
    
    Args:
        volunteer: The volunteer User object
        
    Returns:
        dict: Contains message statistics including sent count and unread receipt count
        
    Example:
        stats = get_volunteer_message_stats(request.user)
        # stats = {'total_sent': 5, 'unread_by_recipients': 2}
    """
    total_sent = Message.objects.filter(sender=volunteer).count()
    unread_by_recipients = Message.get_unread_sent_count(volunteer)
    
    return {
        'total_sent': total_sent,
        'unread_by_recipients': unread_by_recipients,
        'read_by_recipients': total_sent - unread_by_recipients,
    }


def get_sent_message_details(message):
    """
    Get detailed information about a sent message including read receipt.
    
    Args:
        message: The Message object
        
    Returns:
        dict: Contains message details with read receipt information
    """
    return {
        'message': message,
        'is_read': message.is_read,
        'is_unread': message.is_unread,
        'read_status': message.get_read_status(),
        'read_at': message.read_at,
        'sent_at': message.sent_at,
        'recipient_name': message.recipient.display_name,
    }


def get_message_conversations(organization):
    """
    Get all unique conversation threads for an organization.
    
    Args:
        organization: The organization User object
        
    Returns:
        list: List of original messages (not replies) with conversation info
    """
    # Get only original messages (where reply_to is None)
    original_messages = Message.objects.filter(
        recipient=organization,
        reply_to__isnull=True
    ).select_related('sender').order_by('-sent_at')
    
    conversations = []
    for msg in original_messages:
        reply_count = msg.replies.count()
        conversations.append({
            'original_message': msg,
            'reply_count': reply_count,
            'has_replies': reply_count > 0,
            'latest_reply': msg.replies.order_by('-sent_at').first(),
        })
    
    return conversations


def validate_reply_content(content):
    """
    Validate reply content for length and emptiness.
    
    Args:
        content: The reply text
        
    Returns:
        tuple: (is_valid, error_message)
    """
    max_length = 1000
    content = content.strip()
    
    if not content:
        return False, "Your reply cannot be blank. Please enter a message."
    
    if len(content) > max_length:
        overage = len(content) - max_length
        return (
            False,
            f"Your reply exceeds the {max_length} character limit by {overage} characters. "
            f"Please remove {overage} characters and try again."
        )
    
    return True, None
