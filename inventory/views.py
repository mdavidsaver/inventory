from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponseRedirect
from django.forms.models import model_to_dict
from django import forms

from django.contrib import messages

from models import *

class SearchForm(forms.Form):
  query = forms.CharField(required=True)

def show_parts(request):
  parts = Part.objects.all()
  conv = False

  if 'query' in request.GET:
    form = SearchForm(request.GET)
    if form.is_valid():
      query = form.cleaned_data['query']
      parts = Part.indexer.search(query).prefetch()
      conv = True

  # filter vendor list
  vlist = filter(len, request.GET.get('vendor','').split(','))
  if vlist:
    parts = parts.filter(oem__name__in=vlist)

  if conv:
    # Warning: this will fail for large query sets.
    # Paginate first?
    parts = [ p.instance for p in parts ]

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
