"""
Copyright (C) 2013 Michael Davidsaver
Licensed under AGPL 3+
See file "LICENSE" for full terms
"""

from django.db import models
from django.forms import ModelForm, ValidationError
from django.core.validators import RegexValidator

from django.core.files.storage import FileSystemStorage

store = FileSystemStorage()


class Vendor(models.Model):
    name = models.CharField('Name',unique=True,max_length=100,
                            validators=[RegexValidator('^\S+$')])
    site = models.URLField()

    class Meta:
        ordering = ['name']

    @models.permalink
    def get_absolute_url(self):
        return ('vendors',)

    def __unicode__(self):
        return self.name

class Part(models.Model):
    oem = models.ForeignKey(Vendor, related_name='made_set', verbose_name='OEM')
    partnum = models.CharField('OEM P/N',max_length=100,
                               validators=[RegexValidator('^\S+$')])
    count = models.PositiveIntegerField('number held',default=0)

    desc = models.TextField('Description')

    suppliers = models.ManyToManyField(Vendor, through='Supply')

    class Meta:
        unique_together = [('oem','partnum')]
        ordering = ['partnum']

    @models.permalink
    def get_absolute_url(self):
        return ('part', [self.oem.name, self.partnum])

    @models.permalink
    def get_edit_url(self):
        return ('edit_part', [self.oem.name, self.partnum])

    def __unicode__(self):
        return u'%s: %s'%(self.oem.name, self.partnum)

class Supply(models.Model):
    seller = models.ForeignKey(Vendor)
    part = models.ForeignKey(Part)

    partnum = models.CharField('Vendor part num',max_length=100,
                               validators=[RegexValidator('^\S+$')])

    url = models.URLField()

    class Meta:
        unique_together = [('seller','part')]
        ordering = ['partnum']

    @models.permalink
    def get_absolute_url(self):
        return ('edit_supply', [self.part.oem.name, self.part.partnum, self.seller.name])

    @models.permalink
    def get_del_url(self):
        return ('del_supply', [self.part.oem.name, self.part.partnum, self.seller.name])

    def __unicode__(self):
        return u'%s: from %s as %s'%(self.part, self.seller.name, self.partnum)

class Info(models.Model):
    part = models.ForeignKey(Part)
    desc = models.CharField('Label', max_length=30, null=True, blank=True)
    url = models.URLField(null=True,blank=True)
    file = models.FileField(null=True,blank=True,upload_to='sheets', storage=store, max_length=100)


# Forms

class VendorForm(ModelForm):
    class Meta:
        model = Vendor
        exclude = ()

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
        model = Info
        exclude = ('part',)

    def clean(self):
        cleaned = super(InfoForm, self).clean()
        url = cleaned.get('url', '')
        file = cleaned.get('file', None)
        if not url and not file:
            raise ValidationError("Must specify a file and or URL")
        return cleaned
