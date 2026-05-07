from django.contrib import admin
from .models import Achievement, Opportunity, StudentOpportunity, Notification, Application

# Register your models here.

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'date_completed')
    list_filter = ('date_completed', 'student')
    search_fields = ('title', 'description', 'student__email', 'student__first_name', 'student__last_name')
    readonly_fields = ('id',)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'opportunity_type', 'is_active', 'posted_date')
    list_filter = ('is_active', 'opportunity_type', 'posted_date', 'organization')
    search_fields = ('title', 'description', 'organization__email')
    readonly_fields = ('posted_date', 'id')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'organization')
        }),
        ('Details', {
            'fields': ('category', 'location', 'duration', 'required_skills', 'opportunity_type')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('posted_date',),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentOpportunity)
class StudentOpportunityAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__email', 'opportunity__title')
    readonly_fields = ('created_at', 'date_pending', 'id')
    fieldsets = (
        ('Student & Opportunity', {
            'fields': ('student', 'opportunity')
        }),
        ('Status', {
            'fields': ('status', 'date_pending')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__email', 'message')
    readonly_fields = ('created_at', 'id')
    fieldsets = (
        ('Recipient', {
            'fields': ('recipient', 'is_read')
        }),
        ('Content', {
            'fields': ('message',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Application) # Register the Application model with the admin site using a custom admin class to display relevant fields and allow filtering and searching of applications based on status, opportunity, and student email.
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'student', 'status', 'applied_date', 'responded_date')
    list_filter = ('status', 'opportunity')
    search_fields = ('student__email', 'opportunity__title', 'message')


