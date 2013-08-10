
from django.utils import unittest
from django.test.client import Client

from models import *

class Vendors(unittest.TestCase):
  def setUp(self):
    self.client = Client()

  def test_create(self):
    R = self.client.get('/vendor/edit/')
    self.assertEqual(R.status_code, 200)

    Vendor.objects.filter(name='testa').delete()

    R = self.client.post('/vendor/edit/', {'name':'testa', 'site':'http://xyz.com/xyz'})
    self.assertEqual(R.status_code, 200)

    M = Vendor.objects.get(name='testa')
    self.assertEqual(M.site,'http://xyz.com/xyz')

  def test_edit(self):
    M = Vendor.objects.create(name='testb', site='http://mmm.abc/nnn')

    R = self.client.get('/vendor/edit/testb/')
    self.assertEqual(R.status_code, 200)

    F = R.context['formset']

    self.assertTrue(F.is_bound)
    self.assertTrue(F.is_valid())
    self.assertEqual(F.cleaned_data['name'], 'testb')
    self.assertEqual(F.cleaned_data['site'], 'http://mmm.abc/nnn')

    R = self.client.post('/vendor/edit/testb/', {'name':'testc', 'site':'http://abc.xyz/a'})
    self.assertEqual(R.status_code, 200)

    F = R.context['formset']

    self.assertTrue(F.is_bound)
    self.assertTrue(F.is_valid())

    self.assertRaises(Vendor.DoesNotExist, Vendor.objects.get, name='testb')
    M = Vendor.objects.get(name='testc')
    self.assertEqual(M.site, 'http://abc.xyz/a')

class PartView(unittest.TestCase):
  def setUp(self):
    self.client = Client()
    self.V = Vendor.objects.create(name='test')

  def test_home(self):
    p = Part.objects.create(oem=self.V, partnum='xyz')
    R = self.client.get('')
    self.assertEqual(R.status_code, 200)
    self.assertEqual(list(R.context['object_list']), [p])
