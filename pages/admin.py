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
    list_display = ('title', 'organization', 'opportunity_type', 'is_active', 'created_at')
    list_filter = ('is_active', 'opportunity_type', 'created_at', 'organization')
    search_fields = ('title', 'description', 'organization__email')
    readonly_fields = ('created_at', 'id')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'organization')
        }),
        ('Details', {
            'fields': ('cause', 'location', 'duration', 'skills_required', 'opportunity_type')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentOpportunity)
class StudentOpportunityAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'date_joined', 'date_completed')
    list_filter = ('status', 'date_joined', 'date_completed')
    search_fields = ('student__email', 'opportunity__title')
    readonly_fields = ('date_joined', 'date_pending', 'id')
    fieldsets = (
        ('Student & Opportunity', {
            'fields': ('student', 'opportunity')
        }),
        ('Status', {
            'fields': ('status', 'date_completed', 'date_pending')
        }),
        ('Denial Information', {
            'fields': ('denial_reason',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_joined',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'message')
    readonly_fields = ('created_at', 'id')
    fieldsets = (
        ('Recipient & Type', {
            'fields': ('recipient', 'notification_type', 'is_read')
        }),
        ('Content', {
            'fields': ('message',)
        }),
        ('Related Opportunity', {
            'fields': ('student_opportunity',)
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


