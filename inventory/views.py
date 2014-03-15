from django.template.response import TemplateResponse
from django import forms

from django.contrib import messages

from models import Part

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
