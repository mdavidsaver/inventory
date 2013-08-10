from django.template.response import TemplateResponse
from django.http import Http404

from django.contrib import messages

from models import *

def show_parts(request):
  parts = Part.objects.all()
  return TemplateResponse(request, 'parts_list.html', {'object_list':parts})

def del_vendor(request, name):
  M = Vendor.objects.get(name=name)
  conf = request.GET.get('confirm', '0')
  done = conf=='yes'
  if done:
    M.delete()

  return TemplateResponse(request, 'delete_vendor.html', {'object':M, 'done':done})

