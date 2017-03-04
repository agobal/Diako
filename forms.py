from django import forms
from Fara.models import UserProfile
from django.contrib.auth.models import User

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select the pdf file',
        initial = 'arash'
    )
    docfile1 = forms.FileField(
        label='Select the xml file',
        required = False,
        initial = 'arash'
    )

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'email', 'password')

class NonElecForm(forms.Form):
	COUNTY = forms.CharField(max_length=128, help_text="Please enter")
	CITY = forms.CharField(max_length=128, help_text="Please enter")
	ROUTE = forms.CharField(max_length=128, help_text="Please enter")
	SECONDARY_INFORMATION = forms.CharField(max_length=128, help_text="Please enter", initial=None)
	MILEPOST_INFORMATION = forms.CharField(max_length=128, help_text="Please enter", initial=None)
	LATITUDE = forms.CharField(max_length=128, help_text="Please enter", initial=None)
	LONGITUDE = forms.CharField(max_length=128, help_text="Please enter", initial=None)
