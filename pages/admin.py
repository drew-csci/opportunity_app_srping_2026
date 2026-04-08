from django.contrib import admin
from .models import Opportunity

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'opportunity_type', 'cause', 'location', 'duration', 'is_active', 'created_at')
    list_filter = ('opportunity_type', 'is_active', 'cause')
    search_fields = ('title', 'description', 'location', 'skills_required')
