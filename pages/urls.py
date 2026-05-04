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
    path('org/opportunities/', views.organization_opportunities, name='organization_opportunities'),
    path('org/opportunities/new/', views.organization_post_opportunity, name='organization_post_opportunity'),

    # Volunteer Profile Routes
    path('volunteer/profile/', views.volunteer_profile, name='volunteer_profile'),
    path('volunteer/profile/edit/', views.volunteer_profile_edit, name='volunteer_profile_edit'),
    path('volunteer/profile/experience/add/', views.experience_add, name='experience_add'),
    path('volunteer/profile/experience/<int:pk>/edit/', views.experience_edit, name='experience_edit'),
    path('volunteer/profile/experience/<int:pk>/delete/', views.experience_delete, name='experience_delete'),

    # Organization Profile & Follow Routes
    path('organization/<int:org_id>/', views.organization_profile, name='organization_profile'),
    path('organization/<int:org_id>/follow/', views.follow_organization, name='follow_organization'),
    path('organization/<int:org_id>/unfollow/', views.unfollow_organization, name='unfollow_organization'),
    path('following/', views.followed_organizations, name='followed_organizations'),

    # Messaging Routes
    path('organization/inbox/', views.organization_inbox, name='organization_inbox'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('volunteer/sent-messages/', views.volunteer_sent_messages, name='volunteer_sent_messages'),
    path('volunteer/sent-messages/<int:message_id>/', views.volunteer_sent_message_detail, name='volunteer_sent_message_detail'),

    # Student Routes
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/notifications/', views.student_notifications, name='student_notifications'),
]
