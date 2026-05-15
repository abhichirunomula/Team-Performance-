from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='EMPLOYEE',
        widget=forms.Select()
    )
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role='MANAGER'),
        required=False,
        empty_label='— Select your manager (required for employees) —',
        help_text='Employees must select a direct manager.'
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'role',
            'manager',
            'password1',
            'password2',
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        manager = cleaned_data.get('manager')

        if role == 'EMPLOYEE' and not manager:
            self.add_error(
                'manager',
                'Employees must select a direct manager.'
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        # Managers do not have a manager themselves
        if user.role == 'MANAGER':
            user.manager = None
        else:
            user.manager = self.cleaned_data.get('manager')
        if commit:
            user.save()
        return user