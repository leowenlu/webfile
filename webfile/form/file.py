from django import forms
from django.conf import settings
from webfile.models.filemodels import File



class FileChangeFrom(forms.ModelForm):
    class Meta:
        model = File
        fields = '__all__'


class FileFieldForm(forms.ModelForm):
    file_name = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'test'}))
    class Meta:
        model = File
        fields = ('file_name',)
