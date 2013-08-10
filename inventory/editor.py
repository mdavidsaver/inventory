from django.template.response import TemplateResponse
from django.views.generic import View
from django.forms.models import model_to_dict

from django.contrib import messages

class EditorView(View):
  """Generic form editor.

  Allows creation or update
  """
  model = None
  form = None
  idkey = None
  template = None

  def get(self, request, **kws):
    id = {}
    for k in self.idkey:
       try:
         id[k] = kws[k]
       except KeyError:
         pass
    C = {'idkey':id}
    try:
      # find an existing object to edit?
      mod = self.model.objects.get(**id)
    except self.model.DoesNotExist:
      # return an empty form
      C['formset'] = self.form()
    else:
      # edit existing
      C['formset'] = self.form(model_to_dict(mod), instance=mod)
      C['object'] = mod
    return TemplateResponse(request, self.template, C)

  def post(self, request, **kws):
    id = {}
    for k in self.idkey:
       try:
         id[k] = kws[k]
       except KeyError:
         pass
    C = {'idkey':id}
    if id:
      # updste existing
      mod = self.model.objects.get(**id)
      form = self.form(request.POST, instance=mod)
    else:
      # Create new
      form = self.form(request.POST)

    if form.is_valid():
      form.save()
      messages.add_message(request, messages.INFO, 'updated')
    C['formset']=form
    C['object']=form.instance

    return TemplateResponse(request, self.template, C)