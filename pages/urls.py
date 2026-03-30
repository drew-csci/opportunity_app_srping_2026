from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('screen1/', views.screen1, name='screen1'),
    path('screen2/', views.screen2, name='screen2'),
    path('screen3/', views.screen3, name='screen3'),
    path('achievements/', views.student_achievements, name='student_achievements'),
    path('send-message/', views.send_message, name='send_message'),
    path('inbox/', views.organization_inbox, name='organization_inbox'),
    path('message/<int:pk>/', views.message_detail, name='message_detail'),
    path('faq/', views.faq, name='faq'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
