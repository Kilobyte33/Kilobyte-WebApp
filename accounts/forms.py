from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

ZIMBABWE_ALIASES = {
    'zimbabwe',
    'zw',
    'zim',
}


def is_zimbabwe_location(value):
    normalized = (value or '').strip().lower()
    return normalized in ZIMBABWE_ALIASES


class CustomUserCreationForm(UserCreationForm):
    val_email = forms.EmailField(required=True, label='Email')
    location = forms.CharField(
        required=True,
        label='Country',
        help_text='Accounts are currently limited to users in Zimbabwe.',
    )

    class Meta:
        model = User
        fields = ("username", "val_email", "location")

    def clean_location(self):
        location = self.cleaned_data["location"]
        if not is_zimbabwe_location(location):
            raise forms.ValidationError('Kilobyte currently allows sign up only for users in Zimbabwe.')
        return 'Zimbabwe'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["val_email"]
        if commit:
            user.save()
            user.profile.location = self.cleaned_data["location"]
            user.profile.save(update_fields=["location"])
        return user


class ZimbabweAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        location = getattr(getattr(user, 'profile', None), 'location', '')
        if not is_zimbabwe_location(location):
            raise forms.ValidationError(
                'Kilobyte sign in is currently available only to users in Zimbabwe.',
                code='zimbabwe_only',
            )


class ProfileForm(forms.ModelForm):
    def clean_location(self):
        location = self.cleaned_data["location"]
        if location and not is_zimbabwe_location(location):
            raise forms.ValidationError('Kilobyte currently supports profiles only for users in Zimbabwe.')
        return 'Zimbabwe' if location else location

    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar', 'phone', 'location')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
