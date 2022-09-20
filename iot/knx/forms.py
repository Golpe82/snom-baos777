from email.policy import default
from ipaddress import ip_address
from django import forms

from knx.models import AlsStatus

class AmbientlightSensor(forms.ModelForm):
    ip_address = forms.CharField(disabled=True)
    value = forms.CharField(disabled=True)

    class Meta:
        model = AlsStatus
        fields = ["ip_address", "value"]

AlsFormSet = forms.modelformset_factory(AlsStatus,form=AmbientlightSensor)
