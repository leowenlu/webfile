from django.db import models
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from webfile.form.file import FileChangeFrom, FileFieldForm
# Create your views here.
from django.views import View
from webfile.models.filemodels import File
from django.views.generic.edit import CreateView, DeleteView, UpdateView


class ListFile(View):
    def post(self,request):
        form = FileFieldForm(request.POST, request.FILES)
        files = request.FILES.getlist('file_name')
        if form.is_valid():
            for f in files:
                file_instance = File(file_name=f)
                file_instance.save()
            #TODO: pagenation
            object_list = File.objects.all()
            context = {
                'form': form,
                'object_list': object_list
            }
            return render(request, 'webfile/file_list.html', context)  
    def get(self, request):
        form = FileFieldForm()
        object_list = File.objects.all()
        context = {
            'form': form,
            'object_list': object_list
        }
        return render(request, 'webfile/file_list.html', context)

