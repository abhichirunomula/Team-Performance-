from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from cycles.models import ReviewCycle
from .forms import GoalForm
from .models import Goal


@login_required
def goal_list(request):
    """
    Employee: view own goals with filter/sort/pagination.
    Manager: can see all their direct reports' goals via ?employee= param.
    """
    user = request.user

    # --- Base queryset ---
    if user.role == 'MANAGER':
        # Manager can optionally scope to a specific employee
        employee_pk = request.GET.get('employee')
        if employee_pk:
            qs = Goal.objects.filter(employee__pk=employee_pk, employee__manager=user)
        else:
            qs = Goal.objects.filter(employee__manager=user)
    else:
        qs = Goal.objects.filter(employee=user)

    qs = qs.select_related('review_cycle', 'employee')

    # --- Filters ---
    status_filter = request.GET.get('status', '')
    cycle_filter  = request.GET.get('cycle', '')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if cycle_filter:
        qs = qs.filter(review_cycle__pk=cycle_filter)

    # --- Sorting ---
    sort = request.GET.get('sort', '-created_at')
    allowed_sorts = {
        'title': 'title',
        '-title': '-title',
        'status': 'status',
        '-status': '-status',
        'created_at': 'created_at',
        '-created_at': '-created_at',
        'cycle': 'review_cycle__title',
        '-cycle': '-review_cycle__title',
    }
    order_field = allowed_sorts.get(sort, '-created_at')
    qs = qs.order_by(order_field)

    # --- Pagination ---
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # For filter dropdowns
    cycles = ReviewCycle.objects.order_by('-start_date')
    if user.role == 'MANAGER':
        direct_reports = user.team_members.all()
    else:
        direct_reports = []

    context = {
        'page_obj':       page_obj,
        'goals':          page_obj.object_list,   # kept for template compat
        'cycles':         cycles,
        'direct_reports': direct_reports,
        # active filter values (for sticky form)
        'status_filter':  status_filter,
        'cycle_filter':   cycle_filter,
        'sort':           sort,
        'status_choices': Goal.STATUS_CHOICES,
    }

    return render(request, 'goals/goal_list.html', context)


@login_required
def create_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.employee = request.user
            goal.save()
            return redirect('goal_list')
    else:
        form = GoalForm()

    return render(request, 'goals/create_goal.html', {'form': form})


@login_required
def edit_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk)

    # Only the owning employee may edit
    if goal.employee != request.user:
        from django.contrib import messages
        messages.error(request, 'You can only edit your own goals.')
        return redirect('goal_list')

    # Guard: cycle must be OPEN
    if goal.review_cycle.status != 'OPEN':
        from django.contrib import messages
        messages.error(
            request,
            f'Goals cannot be edited once their cycle is '
            f'"{goal.review_cycle.get_status_display()}".'
        )
        return redirect('goal_list')

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('goal_list')
    else:
        form = GoalForm(instance=goal)

    return render(request, 'goals/edit_goal.html', {'form': form, 'goal': goal})


@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk)

    if goal.employee != request.user:
        from django.contrib import messages
        messages.error(request, 'You can only delete your own goals.')
        return redirect('goal_list')

    if goal.review_cycle.status != 'OPEN':
        from django.contrib import messages
        messages.error(
            request,
            f'Goals cannot be deleted once their cycle is '
            f'"{goal.review_cycle.get_status_display()}".'
        )
        return redirect('goal_list')

    if request.method == 'POST':
        goal.delete()
        from django.contrib import messages
        messages.success(request, 'Goal deleted.')
        return redirect('goal_list')

    return render(request, 'goals/delete_goal_confirm.html', {'goal': goal})