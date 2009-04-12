from django import forms
from pooled.models import *
from django.utils.translation import ugettext_lazy as _


class PickForm(forms.Form):
    position = forms.ModelChoiceField(queryset=PickType.objects.all())
    team = forms.CharField(max_length=30)
    team_id = forms.CharField(widget=forms.HiddenInput)
    player = forms.CharField(max_length=30)
    player_id = forms.CharField(widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        super(PickForm, self).__init__(*args, **kwargs)
        self.fields['team'].widget.attrs['disabled']=True 
        self.fields['player'].widget.attrs['disabled']=True

class PooledRegForm(forms.ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        error_message=_("Must contain only letters, numbers and underscores."))
    email = forms.EmailField(label=_("Email"))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    favourite_team = forms.ModelChoiceField(queryset=Team.objects.all(),
        help_text=_("They don't have to be in the playoffs"))

    class Meta:
        model = User
        fields = ("username","email",)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("A user with that email already exists."))
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(PooledRegForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
