from django.template.response import TemplateResponse
from django.views.generic import View

class DetailView(View):
  """Generic detail selector
  """
  model = None
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

    # find object
    C['object'] = self.model.objects.get(**id)

    return TemplateResponse(request, self.template, C)
