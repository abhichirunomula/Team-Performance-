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
        fields = ['username', 'email', 'role', 'manager', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        manager = cleaned_data.get('manager')
        if role == 'EMPLOYEE' and not manager:
            self.add_error('manager', 'Employees must select a direct manager.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if user.role == 'MANAGER':
            user.manager = None
        else:
            user.manager = self.cleaned_data.get('manager')
        if commit:
            user.save()
        return user


class AddEmployeeForm(UserCreationForm):
    """Form for managers to create an employee account pre-assigned to themselves."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name  = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True, manager=None):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        user.role       = 'EMPLOYEE'
        user.manager    = manager
        if commit:
            user.save()
        return user


# ── Admin-only forms ─────────────────────────────────────────────────────────

class CreateManagerForm(UserCreationForm):
    """Admin creates a new Manager account."""
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False, label='First Name')
    last_name  = forms.CharField(max_length=150, required=False, label='Last Name')

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        user.role       = 'MANAGER'
        user.manager    = None
        if commit:
            user.save()
        return user


class AssignManagerForm(forms.ModelForm):
    """Admin reassigns an employee's manager."""
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role='MANAGER'),
        empty_label='— Unassigned —',
        required=False,
        label='Manager',
    )

    class Meta:
        model  = User
        fields = ['manager']