from django import forms
from webfile.models.foldermodels import Folder

class FolderForm(forms.ModelForm):
    class Meta:
        model  = Folder
        fields = '__all__'

