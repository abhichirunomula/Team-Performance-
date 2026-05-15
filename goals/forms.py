from django import forms

from .models import Goal


class GoalForm(forms.ModelForm):

    class Meta:

        model = Goal

        fields = [
            'review_cycle',
            'title',
            'description',
        ]