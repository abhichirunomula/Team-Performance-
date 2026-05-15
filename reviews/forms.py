from django import forms
from .models import SelfAssessment, Review


class SelfAssessmentForm(forms.ModelForm):
    class Meta:
        model = SelfAssessment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Reflect on your accomplishments and progress on your goals this cycle...'
            }),
        }
        labels = {
            'text': 'Your Self-Assessment',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if not text.strip():
            raise forms.ValidationError(
                'Self-assessment text must not be empty or whitespace.'
            )
        return text


class ManagerReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['manager_assessment', 'rating']
        widgets = {
            'manager_assessment': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write your assessment for this employee...'
            }),
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'placeholder': '1–5',
            }),
        }
        labels = {
            'manager_assessment': 'Manager Assessment',
            'rating': 'Overall Rating (1–5)',
        }

    def clean_manager_assessment(self):
        text = self.cleaned_data.get('manager_assessment', '')
        if not text.strip():
            raise forms.ValidationError(
                'Manager assessment must not be empty or whitespace.'
            )
        return text

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError('Rating is required.')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating