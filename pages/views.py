from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q

from .models import Achievement, Message, Conversation, FAQSuggestion
from .forms import AchievementForm
from .serializers import (
    MessageSerializer, 
    ConversationListSerializer, 
    ConversationDetailSerializer,
    FAQSuggestionSerializer
)
from .faq_service import get_suggestions as get_faq_suggestions
from accounts.models import User

# ============ Traditional Views ============

def welcome(request):
    return render(request, 'pages/welcome.html')

@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen1.html', {'role': role})

@login_required
def screen2(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen2.html', {'role': role})

@login_required
def screen3(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen3.html', {'role': role})


@login_required
def student_achievements(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        # Redirect non-students
        return redirect('screen1')

    if request.method == 'POST':
        form = AchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.student = request.user
            achievement.save()
            return redirect('student_achievements')
    else:
        form = AchievementForm()

    achievements = Achievement.objects.filter(student=request.user).order_by('-date_completed')
    return render(request, 'pages/student_achievements.html', {
        'achievements': achievements,
        'form': form,
    })

def faq(request):
    return render(request, 'pages/faq.html')

def dashboard(request):
    return render(request, 'pages/dashboard.html')


# ============ API Views for Messaging ============

class ConversationListView(generics.ListAPIView):
    """
    List all conversations for the current user.
    - Volunteers see their conversations with organizations
    - Organizations see conversations with volunteers
    """
    serializer_class = ConversationListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # For testing/development: return all conversations
        # In production, this should filter by authenticated user
        return Conversation.objects.all().order_by('-last_message_at')


class ConversationDetailView(generics.RetrieveAPIView):
    """Retrieve a specific conversation with all its messages"""
    serializer_class = ConversationDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    def get_queryset(self):
        # For testing/development: return all conversations
        return Conversation.objects.all()


class CreateConversationView(generics.CreateAPIView):
    """
    Create a new conversation between a volunteer and an organization.
    Request body:
    {
        "organization_id": <user_id_of_organization>
    }
    """
    permission_classes = [AllowAny]
    serializer_class = ConversationListSerializer

    def perform_create(self, serializer):
        organization_id = self.request.data.get('organization_id')
        try:
            organization = User.objects.get(id=organization_id, user_type='organization')
        except User.DoesNotExist:
            raise serializers.ValidationError("Organization not found")

        conversation, created = Conversation.objects.get_or_create(
            volunteer=self.request.user,
            organization=organization
        )
        return conversation

    def create(self, request, *args, **kwargs):
        try:
            organization_id = request.data.get('organization_id')
            volunteer_id = request.data.get('volunteer_id')
            
            if not organization_id:
                return Response(
                    {'error': 'organization_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For testing: if no volunteer_id, use the first volunteer
            if not volunteer_id:
                volunteer = User.objects.filter(user_type='student').first()
                if not volunteer:
                    return Response(
                        {'error': 'No volunteers found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                volunteer = User.objects.get(id=volunteer_id)
            
            organization = User.objects.get(id=organization_id, user_type='organization')
            
            conversation, created = Conversation.objects.get_or_create(
                volunteer=volunteer,
                organization=organization
            )
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MessageListView(generics.ListAPIView):
    """Get all messages for a specific conversation"""
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Message.objects.all()
        
        # For testing: return messages for the specified conversation
        return Message.objects.filter(conversation_id=conversation_id)


class SendMessageView(generics.CreateAPIView):
    """
    Send a message in a conversation.
    Request body:
    {
        "conversation_id": <conversation_id>,
        "content": "<message_content>"
    }
    """
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('content')

        if not conversation_id or not content:
            return Response(
                {'error': 'conversation_id and content are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conversation = Conversation.objects.get(id=conversation_id)
            
            # For testing: if user is anonymous, use the first volunteer
            if request.user and request.user.is_authenticated:
                sender = request.user
            else:
                sender = User.objects.filter(user_type='student').first()
                if not sender:
                    return Response(
                        {'error': 'No sender found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkMessageAsReadView(generics.UpdateAPIView):
    """Mark a message as read"""
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(conversation__volunteer=user) | Q(conversation__organization=user)
        )

    def perform_update(self, serializer):
        message = self.get_object()
        message.is_read = True
        message.save()
        return message


class GetOrganizationsView(generics.ListAPIView):
    """Get list of all organizations for selection"""
    permission_classes = [AllowAny]
    serializer_class = None

    def get(self, request):
        organizations = User.objects.filter(user_type='organization')
        data = [
            {
                'id': org.id,
                'email': org.email,
                'display_name': org.display_name,
            }
            for org in organizations
        ]
        return Response(data)


class FAQSuggestionView(generics.CreateAPIView):
    """
    Generate FAQ suggestions for a message.
    Uses rule-based matching and optionally integrates with OpenAI GPT.
    
    Request body:
    {
        "message_content": "<user_message>"
    }
    """
    serializer_class = FAQSuggestionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        message_content = request.data.get('message_content')
        
        if not message_content:
            return Response(
                {'error': 'message_content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate FAQ suggestions using AI service
        try:
            suggestions = get_faq_suggestions(message_content, num_suggestions=3)
            return Response(suggestions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to generate suggestions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
