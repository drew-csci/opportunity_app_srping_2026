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
    path('volunteer/profile/', views.volunteer_profile, name='volunteer_profile'),
    path('volunteer/profile/edit/', views.volunteer_profile_edit, name='volunteer_profile_edit'),
    path('volunteer/profile/experience/add/', views.experience_add, name='experience_add'),
    path('volunteer/profile/experience/<int:pk>/edit/', views.experience_edit, name='experience_edit'),
    path('volunteer/profile/experience/<int:pk>/delete/', views.experience_delete, name='experience_delete'),


    path('organization/<int:org_id>/', views.organization_profile, name='organization_profile'),
    path('organization/<int:org_id>/follow/', views.follow_organization, name='follow_organization'),
    path('organization/<int:org_id>/unfollow/', views.unfollow_organization, name='unfollow_organization'),
    path('following/', views.followed_organizations, name='followed_organizations'),
]

