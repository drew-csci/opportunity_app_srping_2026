from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('screen1/', views.screen1, name='screen1'),
    path('screen2/', views.screen2, name='screen2'),
    path('screen3/', views.screen3, name='screen3'),
    path('achievements/', views.student_achievements, name='student_achievements'),
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:opportunity_id>/apply/', views.apply_to_opportunity, name='apply_to_opportunity'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('organization/applications/', views.organization_applications, name='organization_applications'),
    path('organization/applications/<int:application_id>/review/', views.review_application, name='review_application'),
    path('faq/', views.faq, name='faq'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
