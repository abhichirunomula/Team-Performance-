from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ReviewCycle
from .forms import ReviewCycleForm


def manager_required(view_func):
    """Decorator: only users with role MANAGER can access this view."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'MANAGER':
            messages.error(request, 'Only managers can perform this action.')
            return redirect('cycle_list')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def cycle_list(request):
    cycles = ReviewCycle.objects.all().order_by('-created_at')
    return render(request, 'cycles/cycle_list.html', {'cycles': cycles})


@manager_required
def cycle_create(request):
    if request.method == 'POST':
        form = ReviewCycleForm(request.POST)
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.created_by = request.user
            cycle.status = 'OPEN'
            cycle.save()
            messages.success(request, f'Cycle "{cycle.title}" created successfully.')
            return redirect('cycle_list')
    else:
        form = ReviewCycleForm()

    return render(request, 'cycles/cycle_create.html', {'form': form})


@login_required
def cycle_detail(request, pk):
    cycle = get_object_or_404(ReviewCycle, pk=pk)
    return render(request, 'cycles/cycle_detail.html', {'cycle': cycle})


@manager_required
def cycle_transition(request, pk):
    """
    Open → Under Review → Closed.
    Only the manager who created the cycle can transition it.
    """
    cycle = get_object_or_404(ReviewCycle, pk=pk)

    if cycle.created_by != request.user:
        messages.error(
            request,
            'Only the manager who created this cycle can change its status.'
        )
        return redirect('cycle_detail', pk=pk)

    TRANSITIONS = {
        'OPEN': 'UNDER_REVIEW',
        'UNDER_REVIEW': 'CLOSED',
    }

    next_status = TRANSITIONS.get(cycle.status)
    if not next_status:
        messages.error(request, 'This cycle is already closed and cannot be transitioned.')
        return redirect('cycle_detail', pk=pk)

    if request.method == 'POST':
        cycle.status = next_status
        cycle.save()
        status_label = dict(ReviewCycle.STATUS_CHOICES).get(next_status, next_status)
        messages.success(
            request,
            f'Cycle "{cycle.title}" moved to {status_label}.'
        )
        return redirect('cycle_detail', pk=pk)

    # GET — confirmation page
    next_label = dict(ReviewCycle.STATUS_CHOICES).get(next_status, next_status)
    return render(request, 'cycles/cycle_transition_confirm.html', {
        'cycle': cycle,
        'next_status': next_status,
        'next_label': next_label,
    })
