from django.contrib import admin
from .models import Achievement, Opportunity, StudentOpportunity

# Register your models here.

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'date_completed')
    list_filter = ('date_completed', 'student')
    search_fields = ('title', 'student__email', 'student__first_name', 'student__last_name')
    readonly_fields = ('id',)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'status', 'date_posted')
    list_filter = ('status', 'date_posted', 'organization')
    search_fields = ('title', 'description', 'organization__email')
    readonly_fields = ('date_posted', 'date_updated', 'id')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'organization')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('date_posted', 'date_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentOpportunity)
class StudentOpportunityAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'date_joined', 'date_completed')
    list_filter = ('status', 'date_joined', 'date_completed')
    search_fields = ('student__email', 'opportunity__title')
    readonly_fields = ('date_joined', 'id')
    fieldsets = (
        ('Student & Opportunity', {
            'fields': ('student', 'opportunity')
        }),
        ('Status', {
            'fields': ('status', 'date_completed')
        }),
        ('Dates', {
            'fields': ('date_joined',),
            'classes': ('collapse',)
        }),
    )
