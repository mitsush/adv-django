from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'email', 'profile_picture', 'phone', 'summary', 'degree', 'school', 'university',
                  'previous_work', 'skills', 'employed']
