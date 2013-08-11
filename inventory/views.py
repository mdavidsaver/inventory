from django.template.response import TemplateResponse
from django.http import Http404, HttpResponseRedirect
from django.forms.models import model_to_dict

from django.contrib import messages

from models import *

def show_parts(request):
  vlist = filter(len, request.GET.get('vendor','').split(','))
  if vlist:
    parts = Part.objects.filter(oem__name__in=vlist)
  else:
    parts = Part.objects.all()
  return TemplateResponse(request, 'parts_list.html', {'object_list':parts})

def add_info(request, vname, pnum):
  part = Part.objects.get(oem__name=vname, partnum=pnum)
  C={'part':part}

  if request.method=='POST':
    form = InfoForm(request.POST, request.FILES)

    if form.is_valid():
      form.instance.part = part
      form.save()
      return HttpResponseRedirect(part.get_absolute_url())

  else:
    form = InfoForm()

  C['formset'] = form
  return TemplateResponse(request, 'add_info.html', C)

def del_info(request, pk):
  info = Info.objects.get(pk=pk)
  C={'object':info}
  C['confirm'] = request.GET.get('confirm','')=='yes'
  if C['confirm']:
    if info.file:
      info.file.delete(save=False)
    info.delete()

  return TemplateResponse(request, 'delete.html', C)
  

def add_supply(request, vname, pnum, sname=None):
  part = Part.objects.get(oem__name=vname, partnum=pnum)
  C={'part':part}

  if request.method=='POST':
    if sname:
      # edit existing
      seller = Vendor.objects.get(name=sname)
      sup = Supply.objects.get(part=part, seller=seller)
      form = SupplyForm(request.POST, instance=sup)
      C['object'] = sup

    else:
      # create new
#      sup = Supply.objects.create(part=part)
      form = SupplyForm(request.POST)
      form.instance.part=part     

    if form.is_valid():
      form.save()
      messages.add_message(request, messages.INFO, 'updated')
      return HttpResponseRedirect(form.instance.part.get_absolute_url())

  else:
    if sname is None:
      # new supplier
      form = SupplyForm()
    else:
      seller = Vendor.objects.get(name=sname)
      sup = Supply.objects.get(part=part, seller=seller)
      form = SupplyForm(model_to_dict(sup), instance=sup)
      C['object'] = sup

  C['formset'] = form
  return TemplateResponse(request, 'edit_supply.html', C)
