from django import forms
from pooled.models import *

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

    
    