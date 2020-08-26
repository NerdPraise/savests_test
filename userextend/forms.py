from django import forms
from .models import Email


class SendMailForm(forms.ModelForm):
    subject = forms.CharField(max_length=30)
    body = forms.Textarea()

    # TODO: save mail to db
    class Meta:
        model = Email
        fields = "__all__"
