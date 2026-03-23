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
    
    # Messaging URLs
    path('inbox/', views.organization_inbox, name='organization_inbox'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('send-message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('message-sent-success/', views.message_sent_success, name='message_sent_success'),
    path('message/<int:message_id>/mark-read/', views.mark_message_read, name='mark_message_read'),
    path('api/unread-count/', views.get_unread_count, name='get_unread_count'),
]
