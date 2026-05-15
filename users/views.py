from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, AddEmployeeForm, CreateManagerForm, AssignManagerForm
from .models import User


# ── Helper decorators ────────────────────────────────────────────────────────

def admin_required(view_func):
    """Only Django superusers (admins) may access this view."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access the Admin Panel.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'MANAGER':
            messages.error(request, 'Only managers can access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ── Public ───────────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# ── Admin Panel ──────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_dashboard(request):
    """Admin: overview of all managers and employees."""
    managers  = User.objects.filter(role='MANAGER').order_by('username').prefetch_related('team_members')
    employees = User.objects.filter(role='EMPLOYEE').order_by('username').select_related('manager')
    unassigned = employees.filter(manager__isnull=True)

    return render(request, 'users/admin_dashboard.html', {
        'managers':   managers,
        'employees':  employees,
        'unassigned': unassigned,
    })


@login_required
@admin_required
def admin_create_manager(request):
    """Admin: create a new Manager account."""
    if request.method == 'POST':
        form = CreateManagerForm(request.POST)
        if form.is_valid():
            manager = form.save()
            messages.success(request, f'Manager "{manager.username}" created successfully.')
            return redirect('admin_dashboard')
    else:
        form = CreateManagerForm()

    return render(request, 'users/admin_create_manager.html', {'form': form})


@login_required
@admin_required
def admin_delete_manager(request, pk):
    """Admin: delete a manager (their employees become unassigned)."""
    manager = get_object_or_404(User, pk=pk, role='MANAGER')

    if request.method == 'POST':
        username = manager.username
        # Unassign all employees first
        manager.team_members.update(manager=None)
        manager.delete()
        messages.success(request, f'Manager "{username}" has been deleted. Their employees are now unassigned.')
        return redirect('admin_dashboard')

    return render(request, 'users/admin_delete_manager.html', {'manager': manager})


@login_required
@admin_required
def admin_manager_detail(request, pk):
    """Admin: view a manager's team and reassign employees."""
    manager   = get_object_or_404(User, pk=pk, role='MANAGER')
    team      = manager.team_members.order_by('username')
    unassigned = User.objects.filter(role='EMPLOYEE', manager__isnull=True).order_by('username')

    return render(request, 'users/admin_manager_detail.html', {
        'manager':   manager,
        'team':      team,
        'unassigned': unassigned,
    })


@login_required
@admin_required
def admin_assign_manager(request, employee_pk):
    """Admin: change or set the manager for a specific employee."""
    employee = get_object_or_404(User, pk=employee_pk, role='EMPLOYEE')

    if request.method == 'POST':
        form = AssignManagerForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            new_manager = form.cleaned_data.get('manager')
            if new_manager:
                messages.success(request, f'{employee.username} assigned to manager {new_manager.username}.')
            else:
                messages.success(request, f'{employee.username} is now unassigned.')
            return redirect('admin_dashboard')
    else:
        form = AssignManagerForm(instance=employee)

    return render(request, 'users/admin_assign_manager.html', {
        'employee': employee,
        'form':     form,
    })


@login_required
@admin_required
def admin_delete_employee(request, pk):
    """Admin: delete an employee account."""
    employee = get_object_or_404(User, pk=pk, role='EMPLOYEE')

    if request.method == 'POST':
        username = employee.username
        employee.delete()
        messages.success(request, f'Employee "{username}" has been deleted.')
        return redirect('admin_dashboard')

    return render(request, 'users/admin_delete_employee.html', {'employee': employee})


# ── Manager Team Views ───────────────────────────────────────────────────────

@login_required
@manager_required
def team_list(request):
    team = request.user.team_members.order_by('username')
    return render(request, 'users/team_list.html', {'team': team})


@login_required
@manager_required
def add_employee(request):
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            form.save(manager=request.user)
            messages.success(request, f'Employee "{form.cleaned_data["username"]}" added to your team.')
            return redirect('team_list')
    else:
        form = AddEmployeeForm()

    return render(request, 'users/add_employee.html', {'form': form})


@login_required
@manager_required
def remove_employee(request, pk):
    employee = User.objects.filter(pk=pk, manager=request.user).first()
    if not employee:
        messages.error(request, 'Employee not found in your team.')
        return redirect('team_list')

    if request.method == 'POST':
        employee.manager = None
        employee.save()
        messages.success(request, f'{employee.username} removed from your team.')
        return redirect('team_list')

    return render(request, 'users/remove_employee_confirm.html', {'employee': employee})