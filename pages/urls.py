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

    # Organization Dashboard Routes
    path('org/dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('org/applicant/<int:applicant_id>/', views.applicant_profile, name='applicant_profile'),
    path('org/application/<int:application_id>/accept/', views.accept_application, name='accept_application'),
    path('org/application/<int:application_id>/decline/', views.decline_application, name='decline_application'),
    path('org/profile/', views.organization_profile, name='organization_profile'),
    path('org/messages/', views.organization_messages, name='organization_messages'),
    path('org/opportunities/', views.organization_opportunities, name='organization_opportunities'),
]
