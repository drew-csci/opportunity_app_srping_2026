from django.contrib import admin

from .models import Achievement, Opportunity, Application


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'is_active', 'created_at')
    list_filter = ('is_active', 'organization', 'opportunity_type')
    search_fields = ('title', 'description', 'cause', 'location', 'skills_required')


@admin.register(Application) # Register the Application model with the admin site using a custom admin class to display relevant fields and allow filtering and searching of applications based on status, opportunity, and student email.
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'student', 'status', 'applied_date', 'responded_date')
    list_filter = ('status', 'opportunity')
    search_fields = ('student__email', 'opportunity__title', 'message')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'date_completed')
    list_filter = ('date_completed',)
    search_fields = ('title', 'description', 'student__email')
