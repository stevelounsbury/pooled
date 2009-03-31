from django import forms
from pooled.models import *

class PickForm(forms.Form):
    position = forms.ModelChoiceField(queryset=PickType.objects.all())
    team = forms.CharField(max_length=30, required=False)
    team_id = forms.CharField(widget=forms.HiddenInput)
    player = forms.CharField(max_length=30, required=False)
    player_id = forms.CharField(widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        super(PickForm, self).__init__(*args, **kwargs)
        self.fields['team'].widget.attrs['disabled']=True 
        self.fields['player'].widget.attrs['disabled']=True
        
    def as_nolabel(self):
        "Returns this form rendered as plain widgets with no wrapper or labels."
        return self._html_output(u'%(field)s%(help_text)s', u'%s', '', u' %s', True)

    
    