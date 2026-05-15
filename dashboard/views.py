from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from cycles.models import ReviewCycle
from goals.models import Goal
from reviews.models import SelfAssessment, Review


@login_required
def home(request):
    user = request.user
    context = {'user': user}

    if user.role == 'EMPLOYEE':
        # Active cycles this employee can interact with
        active_cycles = ReviewCycle.objects.filter(
            status__in=['OPEN', 'UNDER_REVIEW']
        ).order_by('-start_date')

        # Goal stats
        my_goals = Goal.objects.filter(employee=user)
        goal_counts = {
            'total':       my_goals.count(),
            'not_started': my_goals.filter(status='NOT_STARTED').count(),
            'in_progress': my_goals.filter(status='IN_PROGRESS').count(),
            'completed':   my_goals.filter(status='COMPLETED').count(),
        }

        # Self-assessments: which cycles still need one
        submitted_cycles = SelfAssessment.objects.filter(
            employee=user
        ).values_list('review_cycle_id', flat=True)

        pending_sa_cycles = ReviewCycle.objects.filter(
            status='UNDER_REVIEW'
        ).exclude(id__in=submitted_cycles)

        # Finalized reviews — what feedback is waiting
        finalized_reviews = Review.objects.filter(
            employee=user,
            status='FINALIZED'
        ).select_related('review_cycle', 'manager').order_by('-finalized_at')[:5]

        # Pending reviews (not yet finalized)
        pending_reviews_count = Review.objects.filter(
            employee=user,
            status='PENDING'
        ).count()

        context.update({
            'active_cycles':       active_cycles,
            'goal_counts':         goal_counts,
            'pending_sa_cycles':   pending_sa_cycles,
            'finalized_reviews':   finalized_reviews,
            'pending_reviews_count': pending_reviews_count,
        })

    elif user.role == 'MANAGER':
        # Cycles
        active_cycles = ReviewCycle.objects.filter(
            status__in=['OPEN', 'UNDER_REVIEW']
        ).order_by('-start_date')

        direct_reports = user.team_members.all()
        team_size = direct_reports.count()

        # Review progress across all under-review cycles
        under_review_cycles = ReviewCycle.objects.filter(status='UNDER_REVIEW')
        total_reviews_needed = team_size * under_review_cycles.count()

        finalized_count = Review.objects.filter(
            manager=user,
            status='FINALIZED',
            review_cycle__in=under_review_cycles
        ).count()

        pending_count = total_reviews_needed - finalized_count

        # Self-assessments submitted by team
        sa_submitted = SelfAssessment.objects.filter(
            employee__manager=user,
            review_cycle__in=under_review_cycles
        ).count()

        # Recent finalized reviews
        recent_reviews = Review.objects.filter(
            manager=user,
            status='FINALIZED'
        ).select_related('employee', 'review_cycle').order_by('-finalized_at')[:5]

        # Average rating
        rated_reviews = Review.objects.filter(
            manager=user,
            status='FINALIZED',
            rating__isnull=False
        )
        avg_rating = None
        if rated_reviews.exists():
            total = sum(r.rating for r in rated_reviews)
            avg_rating = round(total / rated_reviews.count(), 1)

        context.update({
            'active_cycles':       active_cycles,
            'direct_reports':      direct_reports,
            'team_size':           team_size,
            'total_reviews_needed': total_reviews_needed,
            'finalized_count':     finalized_count,
            'pending_count':       pending_count,
            'sa_submitted':        sa_submitted,
            'recent_reviews':      recent_reviews,
            'avg_rating':          avg_rating,
        })

    return render(request, 'home.html', context)