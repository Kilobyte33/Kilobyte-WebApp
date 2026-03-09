from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    val_email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ("username", "val_email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["val_email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar', 'phone', 'location')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }