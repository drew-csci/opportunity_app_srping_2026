from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('screen1/', views.screen1, name='screen1'),
    path('screen2/', views.screen2, name='screen2'),
    path('screen3/', views.screen3, name='screen3'),
    path('achievements/', views.student_achievements, name='student_achievements'),
    path('faq/', views.faq, name='faq'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API Endpoints for Messaging
    path('api/conversations/', views.ConversationListView.as_view(), name='conversation_list'),
    path('api/conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('api/conversations/create/', views.CreateConversationView.as_view(), name='create_conversation'),
    path('api/messages/', views.MessageListView.as_view(), name='message_list'),
    path('api/messages/send/', views.SendMessageView.as_view(), name='send_message'),
    path('api/messages/<int:pk>/read/', views.MarkMessageAsReadView.as_view(), name='mark_message_read'),
    path('api/organizations/', views.GetOrganizationsView.as_view(), name='get_organizations'),
    path('api/faq-suggestions/', views.FAQSuggestionView.as_view(), name='faq_suggestions'),
]
