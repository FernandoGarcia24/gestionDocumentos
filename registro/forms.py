from django import forms
from django.contrib.auth.models import User
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'pdf', 'approver']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'approver': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['approver'].queryset = User.objects.exclude(id=user.id)