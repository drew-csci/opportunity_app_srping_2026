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
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:opportunity_id>/apply/', views.apply_to_opportunity, name='apply_to_opportunity'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('organization/applications/', views.organization_applications, name='organization_applications'),
    path('organization/applications/<int:application_id>/review/', views.review_application, name='review_application'),
    path('faq/', views.faq, name='faq'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('volunteer/profile/', views.volunteer_profile, name='volunteer_profile'),
    path('volunteer/profile/edit/', views.volunteer_profile_edit, name='volunteer_profile_edit'),
    path('volunteer/profile/experience/add/', views.experience_add, name='experience_add'),
    path('volunteer/profile/experience/<int:pk>/edit/', views.experience_edit, name='experience_edit'),
    path('volunteer/profile/experience/<int:pk>/delete/', views.experience_delete, name='experience_delete'),


    path('organization/<int:org_id>/', views.organization_profile, name='organization_profile'),
    path('organization/<int:org_id>/follow/', views.follow_organization, name='follow_organization'),
    path('organization/<int:org_id>/unfollow/', views.unfollow_organization, name='unfollow_organization'),
    path('following/', views.followed_organizations, name='followed_organizations'),
    path('organization/inbox/', views.organization_inbox, name='organization_inbox'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('volunteer/sent-messages/', views.volunteer_sent_messages, name='volunteer_sent_messages'),
    path('volunteer/sent-messages/<int:message_id>/', views.volunteer_sent_message_detail, name='volunteer_sent_message_detail'),
    path('report/submit/', views.submit_report, name='submit_report'),
]

