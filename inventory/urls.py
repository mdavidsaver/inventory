from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import ListView

from inventory.models import *
from inventory.editor import EditorView
from inventory.detail import DetailView
from inventory.delete import DeleteView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ecit.views.home', name='home'),
    # url(r'^ecit/', include('ecit.foo.urls')),

    url(r'^$', 'inventory.views.show_parts', name='home'),

    url(r'^part/edit/$',
      EditorView.as_view(model=Part, form=PartForm, idkey=['oem__name','partnum'], template='edit_part.html'),
      name='edit_part'),
    url(r'^part/edit/(?P<oem__name>\S+)/(?P<partnum>\S+)/$',
      EditorView.as_view(model=Part, form=PartForm, idkey=['oem__name','partnum'], template='edit_part.html'),
      name='edit_part'),

    url(r'^part/delete/(?P<oem__name>\S+)/(?P<partnum>\S+)/$',
      DeleteView.as_view(model=Part, idkey=['oem__name','partnum']),
      name='del_part'),

    url(r'^part/supply/delete/(?P<part__oem__name>\S+)/(?P<part__partnum>\S+)/(?P<seller__name>\S+)/$',
      DeleteView.as_view(model=Supply, idkey=['part__oem__name','part__partnum','seller__name']),
      name='del_supply'),

    url(r'^part/supply/(?P<vname>\S+)/(?P<pnum>\S+)/$',
      'inventory.views.add_supply', name='edit_supply'),

    url(r'^part/supply/(?P<vname>\S+)/(?P<pnum>\S+)/(?P<sname>\S+)/$',
      'inventory.views.add_supply', name='edit_supply'),

    url(r'^part/addinfo/(?P<vname>\S+)/(?P<pnum>\S+)/$',
      'inventory.views.add_info', name='add_info'),

    url(r'^part/delinfo/(?P<pk>\d+)/$',
       'inventory.views.del_info',
      name='del_info'),

    url(r'^part/(?P<oem__name>\S+)/(?P<partnum>\S+)/$',
      DetailView.as_view(model=Part, idkey=['oem__name','partnum'], template='part.html'),
      name='part'),

    url(r'^vendor/$', ListView.as_view(queryset=Vendor.objects.all()),
        name='vendors'),

    url(r'^vendor/edit/$',
      EditorView.as_view(model=Vendor, form=VendorForm, idkey=['name'], template='edit_vendor.html'),
      name='edit_vendor'),
    url(r'^vendor/edit/(?P<name>\S+)/$',
      EditorView.as_view(model=Vendor, form=VendorForm, idkey=['name'], template='edit_vendor.html'),
      name='edit_vendor'),

    url(r'^vendor/delete/(?P<name>\S+)/$',
      DeleteView.as_view(model=Vendor, idkey=['name']),
      name='del_vendor'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
