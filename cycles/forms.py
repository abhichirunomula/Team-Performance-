from django import forms
from .models import ReviewCycle


class ReviewCycleForm(forms.ModelForm):
    class Meta:
        model = ReviewCycle
        fields = ['title', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            self.add_error(
                'end_date',
                'End date must be on or after the start date.'
            )

        title = cleaned_data.get('title', '')
        if not title.strip():
            self.add_error('title', 'Title must not be empty or whitespace.')

        return cleaned_data