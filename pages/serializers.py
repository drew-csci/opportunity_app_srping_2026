from rest_framework import serializers
from .models import Message, Conversation, FAQSuggestion
from accounts.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for display"""
    class Meta:
        model = User
        fields = ['id', 'email', 'display_name', 'user_type']


class FAQSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for FAQ suggestions"""
    class Meta:
        model = FAQSuggestion
        fields = ['id', 'faq_content', 'relevance_score', 'was_accepted', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for individual messages"""
    sender = UserBasicSerializer(read_only=True)
    faq_suggestions = FAQSuggestionSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp', 'is_read', 'faq_suggestions']
        read_only_fields = ['id', 'timestamp', 'faq_suggestions']


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer for conversation list"""
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_user', 'created_at', 'last_message_at', 'last_message']
        read_only_fields = ['id', 'created_at', 'last_message_at']

    def get_other_user(self, obj):
        """Get the other user in the conversation (not the current user)"""
        request = self.context.get('request')
        # For testing purposes, return organization if available
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            if obj.volunteer == request.user:
                return UserBasicSerializer(obj.organization).data
            else:
                return UserBasicSerializer(obj.volunteer).data
        # If no authenticated user, return organization as default
        return UserBasicSerializer(obj.organization).data

    def get_last_message(self, obj):
        """Get the content of the last message"""
        last_msg = obj.messages.last()
        return last_msg.content if last_msg else None


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for conversation with full message history"""
    volunteer = UserBasicSerializer(read_only=True)
    organization = UserBasicSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'volunteer', 'organization', 'messages', 'created_at', 'last_message_at']
        read_only_fields = ['id', 'created_at', 'last_message_at']
