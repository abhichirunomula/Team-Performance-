from django import forms
from .models import Goal
from users.models import User
from cycles.models import ReviewCycle


class GoalForm(forms.ModelForm):
    """Used by employees to create their own goals."""
    class Meta:
        model = Goal
        fields = ['review_cycle', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ManagerGoalForm(forms.ModelForm):
    """Used by managers to assign a task/goal to a specific employee."""

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        if manager:
            self.fields['employee'].queryset = User.objects.filter(
                manager=manager, role='EMPLOYEE'
            ).order_by('username')
        self.fields['employee'].empty_label = '— Select employee —'

    class Meta:
        model = Goal
        fields = ['employee', 'review_cycle', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class GoalStatusForm(forms.ModelForm):
    """Employees use this to update only the status of their goal."""
    class Meta:
        model = Goal
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'status-select'}),
        }