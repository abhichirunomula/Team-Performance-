from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from cycles.models import ReviewCycle
from .forms import GoalForm, ManagerGoalForm, GoalStatusForm
from .models import Goal


@login_required
def goal_list(request):
    """
    Employee: view own goals with filter/sort/pagination.
    Manager: view all their direct reports' goals.
    """
    user = request.user

    if user.role == 'MANAGER':
        employee_pk = request.GET.get('employee')
        if employee_pk:
            qs = Goal.objects.filter(employee__pk=employee_pk, employee__manager=user)
        else:
            qs = Goal.objects.filter(employee__manager=user)
    else:
        qs = Goal.objects.filter(employee=user)

    qs = qs.select_related('review_cycle', 'employee')

    # Filters
    status_filter = request.GET.get('status', '')
    cycle_filter  = request.GET.get('cycle', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if cycle_filter:
        qs = qs.filter(review_cycle__pk=cycle_filter)

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    allowed_sorts = {
        'title': 'title', '-title': '-title',
        'status': 'status', '-status': '-status',
        'created_at': 'created_at', '-created_at': '-created_at',
        'cycle': 'review_cycle__title', '-cycle': '-review_cycle__title',
    }
    qs = qs.order_by(allowed_sorts.get(sort, '-created_at'))

    # Pagination
    paginator  = Paginator(qs, 10)
    page_obj   = paginator.get_page(request.GET.get('page', 1))

    cycles        = ReviewCycle.objects.order_by('-start_date')
    direct_reports = user.team_members.all() if user.role == 'MANAGER' else []

    return render(request, 'goals/goal_list.html', {
        'page_obj':       page_obj,
        'cycles':         cycles,
        'direct_reports': direct_reports,
        'status_filter':  status_filter,
        'cycle_filter':   cycle_filter,
        'sort':           sort,
        'status_choices': Goal.STATUS_CHOICES,
    })


@login_required
def create_goal(request):
    """Employee creates their own goal."""
    if request.user.role == 'MANAGER':
        return redirect('assign_task')

    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.employee = request.user
            goal.save()
            messages.success(request, 'Goal created.')
            return redirect('goal_list')
    else:
        form = GoalForm()

    return render(request, 'goals/create_goal.html', {'form': form})


@login_required
def assign_task(request):
    """Manager assigns a task/goal to one of their direct reports."""
    if request.user.role != 'MANAGER':
        messages.error(request, 'Only managers can assign tasks.')
        return redirect('goal_list')

    if request.method == 'POST':
        form = ManagerGoalForm(request.POST, manager=request.user)
        if form.is_valid():
            goal = form.save(commit=False)
            # Safety check: employee must belong to this manager
            if goal.employee.manager != request.user:
                messages.error(request, 'You can only assign tasks to your own team members.')
                return redirect('goal_list')
            goal.save()
            messages.success(request, f'Task assigned to {goal.employee.username}.')
            return redirect('goal_list')
    else:
        form = ManagerGoalForm(manager=request.user)

    return render(request, 'goals/assign_task.html', {'form': form})


@login_required
def update_goal_status(request, pk):
    """Employee updates only the status of their own goal."""
    goal = get_object_or_404(Goal, pk=pk)

    if goal.employee != request.user:
        messages.error(request, 'You can only update your own goals.')
        return redirect('goal_list')

    if request.method == 'POST':
        form = GoalStatusForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Status updated to "{goal.get_status_display()}".')
            return redirect('goal_list')
    else:
        form = GoalStatusForm(instance=goal)

    return render(request, 'goals/update_status.html', {
        'form':           form,
        'goal':           goal,
        'status_choices': Goal.STATUS_CHOICES,
    })


@login_required
def edit_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk)

    if goal.employee != request.user:
        messages.error(request, 'You can only edit your own goals.')
        return redirect('goal_list')

    if goal.review_cycle.status != 'OPEN':
        messages.error(request, f'Goals cannot be edited once their cycle is "{goal.review_cycle.get_status_display()}".')
        return redirect('goal_list')

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated.')
            return redirect('goal_list')
    else:
        form = GoalForm(instance=goal)

    return render(request, 'goals/edit_goal.html', {'form': form, 'goal': goal})


@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk)

    if goal.employee != request.user and request.user.role != 'MANAGER':
        messages.error(request, 'You can only delete your own goals.')
        return redirect('goal_list')

    if goal.review_cycle.status != 'OPEN':
        messages.error(request, f'Goals cannot be deleted once their cycle is "{goal.review_cycle.get_status_display()}".')
        return redirect('goal_list')

    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted.')
        return redirect('goal_list')

    return render(request, 'goals/delete_goal_confirm.html', {'goal': goal})