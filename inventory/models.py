from django.db import models
from django.forms import ModelForm

from django.core.files.storage import FileSystemStorage

store = FileSystemStorage()

class Vendor(models.Model):
  name = models.CharField('Name',unique=True,max_length=100)
  site = models.URLField()

  def __unicode__(self):
    return self.name

class Part(models.Model):
  oem = models.ForeignKey(Vendor, related_name='made_set')
  partnum = models.CharField('Vendor part num',max_length=100)
  count = models.PositiveIntegerField('number held',default=0)

  desc = models.TextField('Description')

  suppliers = models.ManyToManyField(Vendor, through='Supply')

  class Meta:
    unique_together = [('oem','partnum')]

  def __unicode__(self):
    return u'%s: %s'%(self.oem.name, self.partnum)

class Supply(models.Model):
  seller = models.ForeignKey(Vendor)
  part = models.ForeignKey(Part)

  partnum = models.CharField('Vendor part num',max_length=100)

  url = models.URLField()

class Info(models.Model):
  part = models.ForeignKey(Part)
  url = models.URLField()
  file = models.FileField(upload_to='sheets', storage=store, max_length=100)


# Forms

class VendorForm(ModelForm):
  class Meta:
    model = Vendor

class PartForm(ModelForm):
  class Meta:
    model = Part
    exclude = ('suppliers',)

class SupplyForm(ModelForm):
  class Meta:
    model = Supply
    exclude = ('part',)

class InfoForm(ModelForm):
  class Meta:
    model = Supply
    exclude = ('part',)