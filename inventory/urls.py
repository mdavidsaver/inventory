from django.conf import settings
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView

import djapian
djapian.load_indexes()

from inventory.models import Vendor, Part, Supply, Info, VendorForm, PartForm, SupplyForm, InfoForm

class PartObjectMixin(object):
    model = Part
    form_class = PartForm
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(queryset,
                                 oem__name=self.kwargs['oem'],
                                 partnum=self.kwargs['partnum'])

class PartDeleteView(PartObjectMixin, DeleteView):
    template_name = 'delete.html'
    success_url = reverse_lazy('home')

class PartUpdateView(PartObjectMixin, UpdateView):
    template_name = 'edit_part.html'

class PartDetailView(PartObjectMixin, DetailView):
    template_name = 'part.html'


class SupplyObjectMixin(object):
    model = Supply
    form_class = SupplyForm
    def get_object(self, queryset=None):
        kws = self.kwargs
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(queryset,
                                 part__oem__name=kws['oem'],
                                 part__partnum=kws['partnum'],
                                 seller__name=kws['seller'])

    def get_success_url(self):
        if self.object:
            return self.object.part.get_absolute_url()
        return reverse_lazy('home')

class SupplyCreateView(SupplyObjectMixin, CreateView):
    template_name = 'edit_supply.html'

    def get_form(self, klass):
        F = super(SupplyCreateView, self).get_form(klass)
        kws = self.kwargs
        F.instance.part = get_object_or_404(Part.objects,
                                            oem__name=kws['oem'],
                                            partnum=kws['partnum'])
        return F

class SupplyDeleteView(SupplyObjectMixin, DeleteView):
    template_name = 'delete.html'

class SupplyUpdateView(SupplyObjectMixin, UpdateView):
    template_name = 'edit_supply.html'

class SupplyDetailView(SupplyObjectMixin, DetailView):
    pass

class InfoCreateView(CreateView):
    model = Info
    form_class = InfoForm
    def get_form(self, klass):
        F = super(InfoCreateView, self).get_form(klass)
        kws = self.kwargs
        F.instance.part = get_object_or_404(Part.objects,
                                            oem__name=kws['oem'],
                                            partnum=kws['partnum'])
        return F
    def get_success_url(self):
        return self.object.part.get_absolute_url()

class InfoDeleteView(DeleteView):
    model = Info
    form_class = InfoForm
    template_name = 'delete.html'
    def get_success_url(self):
        return self.object.part.get_absolute_url()    

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ecit.views.home', name='home'),
    # url(r'^ecit/', include('ecit.foo.urls')),

    url(r'^$', 'inventory.views.show_parts', name='home'),

    url(r'^part/edit/$',
      CreateView.as_view(form_class=PartForm, template_name='edit_part.html'),
      name='edit_part'),
    url(r'^part/edit/(?P<oem>\S+)/(?P<partnum>\S+)/$',
      PartUpdateView.as_view(), name='edit_part'),

    url(r'^part/delete/(?P<oem>\S+)/(?P<partnum>\S+)/$',
      PartDeleteView.as_view(), name='del_part'),

    url(r'^part/supply/delete/(?P<oem>\S+)/(?P<partnum>\S+)/(?P<seller>\S+)/$',
      SupplyDeleteView.as_view(), name='del_supply'),

    url(r'^part/supply/add/(?P<oem>\S+)/(?P<partnum>\S+)/$',
      SupplyCreateView.as_view(), name='edit_supply'),

    url(r'^part/supply/edit/(?P<oem>\S+)/(?P<partnum>\S+)/(?P<seller>\S+)/$',
      SupplyUpdateView.as_view(), name='edit_supply'),

    url(r'^part/addinfo/(?P<oem>\S+)/(?P<partnum>\S+)/$',
      InfoCreateView.as_view(), name='add_info'),

    url(r'^part/delinfo/(?P<pk>\d+)/$',
       InfoDeleteView.as_view(), name='del_info'),

    url(r'^part/(?P<oem>\S+)/(?P<partnum>\S+)/$',
      PartDetailView.as_view(), name='part'),

    url(r'^vendor/$', ListView.as_view(queryset=Vendor.objects.all(),
                                       template_name='vendor_list.html'),
        name='vendors'),

    url(r'^vendor/edit/$',
      CreateView.as_view(model=Vendor, form_class=VendorForm,
                         template_name='edit_vendor.html'),
      name='edit_vendor'),
    url(r'^vendor/edit/(?P<slug>\S+)/$',
      UpdateView.as_view(model=Vendor, form_class=VendorForm, slug_field='name',
                         template_name='edit_vendor.html'),
      name='edit_vendor'),

    url(r'^vendor/delete/(?P<slug>\S+)/$',
      DeleteView.as_view(model=Vendor, slug_field='name',
                         template_name='delete.html',
                         success_url=reverse_lazy('vendors')),
      name='del_vendor'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
