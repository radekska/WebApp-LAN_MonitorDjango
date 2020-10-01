from django import forms
from .models import ConfigParameters, SNMPConfigParameters


class ConfigParametersForm(forms.ModelForm):
    class Meta:
        model = ConfigParameters
        fields = [
            'login_username',
            'login_password',
            'secret',
            'network_ip',
            'subnet_cidr',
            'network_device_os',
            'discovery_protocol'
        ]
        widgets = {
            'login_password': forms.PasswordInput(),
            'secret': forms.PasswordInput(),

        }


class SNMPConfigParametersForm(forms.ModelForm):
    server_location = forms.CharField(required=False)
    contact_details = forms.CharField(required=False)
    enable_traps = forms.BooleanField(required=False)

    class Meta:
        model = SNMPConfigParameters
        fields = [
            'server_location',
            'contact_details',
            'enable_traps',
            'group_name',
            'snmp_user',
            'snmp_password',
            'snmp_encrypt_key',
            'snmp_host'
        ]
        widgets = {
            'snmp_password': forms.PasswordInput(),
            'snmp_encrypt_key': forms.PasswordInput(),
        }

