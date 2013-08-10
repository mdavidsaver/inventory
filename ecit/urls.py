from django.conf.urls import patterns, include, url
from django.views.generic import ListView

from inventory.models import *
from inventory.editor import EditorView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ecit.views.home', name='home'),
    # url(r'^ecit/', include('ecit.foo.urls')),

    url(r'^$', 'inventory.views.show_parts', name='home'),

    url(r'^vendor/?$', ListView.as_view(queryset=Vendor.objects.all()),
        name='vendors'),

    url(r'^vendor/edit/?$',
      EditorView.as_view(model=Vendor, form=VendorForm, idkey='name', template='vendor.html'),
      name='edit_vendor'),
    url(r'^vendor/edit/(?P<name>\w+)/?$',
      EditorView.as_view(model=Vendor, form=VendorForm, idkey='name', template='vendor.html'),
      name='edit_vendor'),

#    url(r'^vendor/edit/?$', 'inventory.views.edit_vendor', name='edit_vendor'),
#    url(r'^vendor/edit/(?P<name>\w+)/?$', 'inventory.views.edit_vendor', name='edit_vendor'),

    url(r'^vendor/delete/(?P<name>\w+)/?$', 'inventory.views.del_vendor', name='del_vendor'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
