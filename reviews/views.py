from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

from cycles.models import ReviewCycle
from .models import SelfAssessment, Review
from .forms import SelfAssessmentForm, ManagerReviewForm


# ---------------------------------------------------------------------------
# Self-Assessment
# ---------------------------------------------------------------------------

@login_required
def self_assessment_submit(request, cycle_pk):
    """
    Employee submits or updates their self-assessment for a given cycle.
    - Cycle must be Under Review.
    - One per employee per cycle (upsert).
    - Locked once manager review is finalized.
    """
    cycle = get_object_or_404(ReviewCycle, pk=cycle_pk)

    # Only employees submit self-assessments
    if request.user.role == 'MANAGER':
        messages.error(request, 'Managers do not submit self-assessments.')
        return redirect('cycle_list')

    # Cycle must be Under Review
    if cycle.status != 'UNDER_REVIEW':
        messages.error(
            request,
            f'Self-assessments can only be submitted while a cycle is Under Review. '
            f'"{cycle.title}" is currently {cycle.get_status_display()}.'
        )
        return redirect('cycle_list')

    # Check if a finalized manager review already exists — lock editing
    existing_review = Review.objects.filter(
        employee=request.user,
        review_cycle=cycle,
        status='FINALIZED'
    ).first()

    if existing_review:
        messages.error(
            request,
            'Your manager has already finalized your review. '
            'Your self-assessment can no longer be edited.'
        )
        return redirect('self_assessment_detail', cycle_pk=cycle.pk)

    # Upsert: get or create
    assessment, _ = SelfAssessment.objects.get_or_create(
        employee=request.user,
        review_cycle=cycle,
        defaults={'text': ''}
    )

    if request.method == 'POST':
        form = SelfAssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Self-assessment saved.')
            return redirect('self_assessment_detail', cycle_pk=cycle.pk)
    else:
        form = SelfAssessmentForm(instance=assessment)

    return render(request, 'reviews/self_assessment_form.html', {
        'form': form,
        'cycle': cycle,
        'assessment': assessment,
    })


@login_required
def self_assessment_detail(request, cycle_pk):
    """
    View own self-assessment for a cycle.
    Managers can also view their direct reports' assessments.
    """
    cycle = get_object_or_404(ReviewCycle, pk=cycle_pk)
    user = request.user

    if user.role == 'MANAGER':
        # Manager sees all their direct reports' assessments for this cycle
        assessments = SelfAssessment.objects.filter(
            review_cycle=cycle,
            employee__manager=user
        ).select_related('employee')
        return render(request, 'reviews/manager_assessments_list.html', {
            'cycle': cycle,
            'assessments': assessments,
        })
    else:
        # Employee sees only their own
        assessment = SelfAssessment.objects.filter(
            employee=user,
            review_cycle=cycle
        ).first()

        # Check if finalized review exists to show lock state
        finalized_review = Review.objects.filter(
            employee=user,
            review_cycle=cycle,
            status='FINALIZED'
        ).first()

        return render(request, 'reviews/self_assessment_detail.html', {
            'cycle': cycle,
            'assessment': assessment,
            'finalized_review': finalized_review,
        })


# ---------------------------------------------------------------------------
# Manager Review — with filters / sorting / pagination
# ---------------------------------------------------------------------------

@login_required
def manager_review_list(request):
    """
    Manager sees all direct reports and their review status.
    Supports filtering by cycle and review status, plus sorting and pagination.
    """
    if request.user.role != 'MANAGER':
        messages.error(request, 'Only managers can access the review list.')
        return redirect('goal_list')

    direct_reports = request.user.team_members.all()
    cycles = ReviewCycle.objects.order_by('-start_date')

    # --- Filters ---
    cycle_filter    = request.GET.get('cycle', '')
    status_filter   = request.GET.get('status', '')   # review status: PENDING / FINALIZED / ''
    sa_filter       = request.GET.get('sa', '')        # self-assessment: yes / no / ''
    employee_filter = request.GET.get('employee', '')

    # Build review data
    review_data = []
    filtered_cycles = ReviewCycle.objects.filter(status='UNDER_REVIEW').order_by('-created_at')
    if cycle_filter:
        filtered_cycles = filtered_cycles.filter(pk=cycle_filter)

    filtered_reports = direct_reports
    if employee_filter:
        filtered_reports = filtered_reports.filter(pk=employee_filter)

    for report in filtered_reports:
        for cycle in filtered_cycles:
            review = Review.objects.filter(
                employee=report,
                review_cycle=cycle,
                manager=request.user
            ).first()

            has_self_assessment = SelfAssessment.objects.filter(
                employee=report,
                review_cycle=cycle
            ).exists()

            # Apply filters
            if status_filter:
                if status_filter == 'PENDING' and (not review or review.status != 'PENDING'):
                    continue
                if status_filter == 'FINALIZED' and (not review or review.status != 'FINALIZED'):
                    continue
                if status_filter == 'NOT_STARTED' and review:
                    continue

            if sa_filter == 'yes' and not has_self_assessment:
                continue
            if sa_filter == 'no' and has_self_assessment:
                continue

            review_data.append({
                'employee': report,
                'cycle': cycle,
                'review': review,
                'has_self_assessment': has_self_assessment,
            })

    # --- Sorting ---
    sort = request.GET.get('sort', 'employee')
    sort_map = {
        'employee': lambda x: x['employee'].username,
        '-employee': lambda x: x['employee'].username,
        'cycle': lambda x: x['cycle'].title,
        '-cycle': lambda x: x['cycle'].title,
        'status': lambda x: (x['review'].status if x['review'] else 'ZZZ'),
        '-status': lambda x: (x['review'].status if x['review'] else 'ZZZ'),
    }
    sort_fn = sort_map.get(sort, sort_map['employee'])
    reverse = sort.startswith('-')
    review_data.sort(key=sort_fn, reverse=reverse)

    # --- Pagination ---
    paginator = Paginator(review_data, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'reviews/manager_review_list.html', {
        'page_obj':        page_obj,
        'review_data':     page_obj.object_list,
        'direct_reports':  direct_reports,
        'cycles':          cycles,
        # active filters
        'cycle_filter':    cycle_filter,
        'status_filter':   status_filter,
        'sa_filter':       sa_filter,
        'employee_filter': employee_filter,
        'sort':            sort,
    })


@login_required
def manager_review_submit(request, cycle_pk, employee_pk):
    """
    Manager writes assessment + rating and finalizes the review.
    - Only the direct manager of the employee may submit.
    - Cycle must be Under Review.
    - Once finalized, cannot be changed.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.user.role != 'MANAGER':
        messages.error(request, 'Only managers can submit reviews.')
        return redirect('goal_list')

    cycle = get_object_or_404(ReviewCycle, pk=cycle_pk)
    employee = get_object_or_404(User, pk=employee_pk)

    # Enforce: only the direct manager of this employee
    if employee.manager != request.user:
        messages.error(
            request,
            f'You are not the direct manager of {employee.username}.'
        )
        return redirect('manager_review_list')

    # Cycle must be Under Review
    if cycle.status != 'UNDER_REVIEW':
        messages.error(
            request,
            f'Reviews can only be submitted while a cycle is Under Review. '
            f'"{cycle.title}" is currently {cycle.get_status_display()}.'
        )
        return redirect('manager_review_list')

    # Get or create the review record
    review, _ = Review.objects.get_or_create(
        employee=employee,
        review_cycle=cycle,
        manager=request.user,
        defaults={'status': 'PENDING'}
    )

    # Once finalized, it's read-only
    if review.status == 'FINALIZED':
        messages.info(request, 'This review has already been finalized.')
        return redirect('manager_review_detail', cycle_pk=cycle.pk, employee_pk=employee.pk)

    # Attach self-assessment for reference (visible to manager)
    self_assessment = SelfAssessment.objects.filter(
        employee=employee,
        review_cycle=cycle
    ).first()

    # Fetch employee goals for reference
    from goals.models import Goal
    employee_goals = Goal.objects.filter(
        employee=employee,
        review_cycle=cycle
    )

    if request.method == 'POST':
        form = ManagerReviewForm(request.POST, instance=review)
        if form.is_valid():
            finalized_review = form.save(commit=False)
            finalized_review.status = 'FINALIZED'
            finalized_review.finalized_at = timezone.now()
            finalized_review.save()
            messages.success(
                request,
                f'Review for {employee.username} finalized successfully.'
            )
            return redirect('manager_review_list')
    else:
        form = ManagerReviewForm(instance=review)

    return render(request, 'reviews/manager_review_form.html', {
        'form': form,
        'cycle': cycle,
        'employee': employee,
        'self_assessment': self_assessment,
        'employee_goals': employee_goals,
        'review': review,
    })


@login_required
def manager_review_detail(request, cycle_pk, employee_pk):
    """
    View a finalized review.
    - Manager: always sees full details.
    - Employee: sees full details only after finalization (FR27).
      Before finalization, sees pending status only (FR26).
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    cycle = get_object_or_404(ReviewCycle, pk=cycle_pk)
    employee = get_object_or_404(User, pk=employee_pk)
    user = request.user

    # Access control: only the employee themselves or their direct manager
    if user != employee and user != employee.manager:
        messages.error(request, 'You do not have permission to view this review.')
        return redirect('goal_list')

    review = Review.objects.filter(
        employee=employee,
        review_cycle=cycle
    ).first()

    # Employees cannot see manager assessment/rating until finalized
    show_manager_feedback = (
        user.role == 'MANAGER' or
        (review and review.status == 'FINALIZED')
    )

    return render(request, 'reviews/review_detail.html', {
        'cycle': cycle,
        'employee': employee,
        'review': review,
        'show_manager_feedback': show_manager_feedback,
    })