"""
Utility functions for managing student opportunities and dashboards.

This module provides helper functions for:
- Creating opportunities
- Marking opportunities as completed
- Retrieving student's opportunities by status
- Bulk operations on opportunities
"""

from django.utils import timezone
from datetime import timedelta
from .models import Opportunity, StudentOpportunity, Student


def create_opportunity(title, description, organization, status='open'):
    """
    Create a new opportunity posted by an organization.
    
    Args:
        title (str): The opportunity title
        description (str): Detailed description of the opportunity
        organization (User): The organization posting the opportunity (user_type must be 'organization')
        status (str): 'open' or 'closed' (default: 'open')
    
    Returns:
        Opportunity: The created opportunity instance
    """
    if organization.user_type != 'organization':
        raise ValueError("Organization must be a user with user_type='organization'")
    
    opportunity = Opportunity.objects.create(
        title=title,
        description=description,
        organization=organization,
        status=status
    )
    return opportunity


def add_student_to_opportunity(student, opportunity, status='not_started'):
    """
    Add a student to an opportunity.
    
    Args:
        student (User): The student user (user_type must be 'student')
        opportunity (Opportunity): The opportunity instance
        status (str): Initial status ('not_started', 'in_progress', 'completed')
    
    Returns:
        StudentOpportunity: The created StudentOpportunity instance
    
    Raises:
        ValueError: If student is not a student user type
    """
    if student.user_type != 'student':
        raise ValueError("User must be a student (user_type='student')")
    
    student_opp, created = StudentOpportunity.objects.get_or_create(
        student=student,
        opportunity=opportunity,
        defaults={'status': status}
    )
    
    if not created and status != 'not_started':
        student_opp.status = status
        student_opp.save()
    
    return student_opp


def mark_opportunity_completed(student, opportunity):
    """
    Mark an opportunity as completed by a student.
    
    Args:
        student (User): The student user
        opportunity (Opportunity): The opportunity instance
    
    Returns:
        StudentOpportunity: Updated StudentOpportunity instance
    """
    student_opp = StudentOpportunity.objects.get(
        student=student,
        opportunity=opportunity
    )
    student_opp.status = 'completed'
    student_opp.date_completed = timezone.now()
    student_opp.save()
    return student_opp


def mark_opportunity_pending(student, opportunity):
    """
    Mark an in-progress opportunity as pending completion.
    This is the first step before it's officially marked as completed.
    
    Args:
        student (User): The student user
        opportunity (Opportunity): The opportunity instance
    
    Returns:
        StudentOpportunity: Updated StudentOpportunity instance
    
    Raises:
        ValueError: If opportunity is not currently in_progress
    """
    student_opp = StudentOpportunity.objects.get(
        student=student,
        opportunity=opportunity
    )
    
    if student_opp.status != 'in_progress':
        raise ValueError(f"Opportunity must be 'in_progress' to mark as pending, current status: {student_opp.status}")
    
    student_opp.status = 'pending'
    student_opp.date_pending = timezone.now()
    student_opp.save()
    return student_opp


def get_student_completed_opportunities(student):
    """
    Get all completed opportunities for a student.
    
    Args:
        student (User): The student user
    
    Returns:
        QuerySet: StudentOpportunity objects with status='completed'
    """
    return StudentOpportunity.objects.filter(
        student=student,
        status='completed'
    ).select_related('opportunity', 'opportunity__organization').order_by('-date_completed')


def get_student_in_progress_opportunities(student):
    """
    Get all in-progress opportunities for a student.
    
    Args:
        student (User): The student user
    
    Returns:
        QuerySet: StudentOpportunity objects with status='in_progress'
    """
    return StudentOpportunity.objects.filter(
        student=student,
        status='in_progress'
    ).select_related('opportunity', 'opportunity__organization').order_by('-date_joined')


def get_student_pending_opportunities(student):
    """
    Get all pending opportunities for a student.
    These are opportunities marked for completion but awaiting approval.
    
    Args:
        student (User): The student user
    
    Returns:
        QuerySet: StudentOpportunity objects with status='pending'
    """
    return StudentOpportunity.objects.filter(
        student=student,
        status='pending'
    ).select_related('opportunity', 'opportunity__organization').order_by('-date_pending')


def get_student_not_started_opportunities(student):
    """
    Get opportunities a student hasn't started yet.
    
    Args:
        student (User): The student user
    
    Returns:
        QuerySet: StudentOpportunity objects with status='not_started'
    """
    return StudentOpportunity.objects.filter(
        student=student,
        status='not_started'
    ).select_related('opportunity', 'opportunity__organization')


def get_student_all_opportunities(student):
    """
    Get all opportunities for a student, regardless of status.
    
    Args:
        student (User): The student user
    
    Returns:
        QuerySet: All StudentOpportunity objects for the student
    """
    return StudentOpportunity.objects.filter(
        student=student
    ).select_related('opportunity', 'opportunity__organization').order_by('-date_joined')


def get_open_opportunities():
    """
    Get all open opportunities available to students.
    
    Returns:
        QuerySet: Opportunity objects with status='open'
    """
    return Opportunity.objects.filter(status='open').select_related('organization').order_by('-date_posted')


def close_opportunity(opportunity):
    """
    Close an opportunity so students can't join.
    
    Args:
        opportunity (Opportunity): The opportunity to close
    
    Returns:
        Opportunity: Updated opportunity instance
    """
    opportunity.status = 'closed'
    opportunity.save()
    return opportunity


def get_student_dashboard_data(student):
    """
    Get comprehensive dashboard data for a student.
    
    Args:
        student (User): The student user
    
    Returns:
        dict: Dashboard data including completed, in-progress, and statistics
    """
    completed = get_student_completed_opportunities(student)
    in_progress = get_student_in_progress_opportunities(student)
    all_opps = get_student_all_opportunities(student)
    
    return {
        'completed_opportunities': completed,
        'in_progress_opportunities': in_progress,
        'all_opportunities': all_opps,
        'completed_count': completed.count(),
        'in_progress_count': in_progress.count(),
        'total_opportunities_count': all_opps.count(),
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
"""
# In your views or management commands, you can use these utilities:

from pages.opportunity_utils import *
from accounts.models import User

# Create an opportunity
org_user = User.objects.get(email='organization@example.com')
opportunity = create_opportunity(
    title='Summer Volunteer Program',
    description='Help us make a difference this summer!',
    organization=org_user,
    status='open'
)

# Add a student to an opportunity
student = User.objects.get(email='student@example.com')
student_opp = add_student_to_opportunity(student, opportunity, status='in_progress')

# Mark it as completed
completed_opp = mark_opportunity_completed(student, opportunity)

# Get student's completed opportunities
completed = get_student_completed_opportunities(student)
for opp in completed:
    print(f"Completed: {opp.opportunity.title} on {opp.date_completed}")

# Get dashboard data
dashboard_data = get_student_dashboard_data(student)
print(f"Completed: {dashboard_data['completed_count']}")
print(f"In Progress: {dashboard_data['in_progress_count']}")
"""
