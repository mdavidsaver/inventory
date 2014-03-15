"""
Copyright (C) 2013 Michael Davidsaver
Licensed under AGPL 3+
See file "LICENSE" for full terms
"""

from django import template
from django.forms.models import model_to_dict

import inventory.models as db

register = template.Library()

@register.assignment_tag
def new_model_form(form, **kws):
  form = getattr(db, form)
  return form(initial=kws)
