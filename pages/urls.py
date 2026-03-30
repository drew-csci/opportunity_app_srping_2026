from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('screen1/', views.screen1, name='screen1'),
    path('screen2/', views.screen2, name='screen2'),
    path('screen3/', views.screen3, name='screen3'),
    path('achievements/', views.student_achievements, name='student_achievements'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-notifications/', views.student_notifications, name='student_notifications'),
    path('mark-pending/<int:student_opportunity_id>/', views.mark_opportunity_pending, name='mark_opportunity_pending'),
    path('organization-dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('approve-opportunity/<int:student_opportunity_id>/', views.approve_opportunity_completion, name='approve_opportunity_completion'),
    path('deny-opportunity/<int:student_opportunity_id>/', views.deny_opportunity_completion, name='deny_opportunity_completion'),
    path('faq/', views.faq, name='faq'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
