from django.shortcuts import render_to_response
from django.http import Http404

from django.contrib import messages

from models import *

def show_parts(request):
  parts = Part.objects.all()
  return render_to_response('parts_list.html', {'object_list':parts})

def edit_vendor(request, name=''):
  if request.method == 'POST':
    if name:
      # update existing
      mod = Vendor.objects.get(name=name)
      newv = VendorForm(request.POST, instance=mod)
    else:
      # create new
      newv = VendorForm(request.POST)

    if newv.is_valid():
      newv.save()
      messages.add_message(request, messages.INFO, 'Vendor updated')
    else:
      messages.add_message(request, messages.ERROR, 'Could not update Vendor')
  else:
    try:
      mod = Vendor.objects.get(name=name)
      newv = VendorForm(model_to_dict(mod), instance=mod )
    except Vendor.DoesNotExist:
      newv = VendorForm()

  return render_to_response('edit_vendor.html', {'formset':newv,'name':name})

def del_vendor(request, name):
  M = Vendor.objects.get(name=name)
  conf = request.GET.get('confirm', '0')
  done = conf=='yes'
  if done:
    M.delete()

  return render_to_response('delete_vendor.html', {'object':M, 'done':done})
