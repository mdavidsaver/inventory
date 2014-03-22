"""
Copyright (C) 2013 Michael Davidsaver
Licensed under AGPL 3+
See file "LICENSE" for full terms
"""

import tempfile, os

from django.test import TestCase

from models import Vendor, Part, Supply, Info

class Parts(TestCase):
    pass

class Vendors(TestCase):
#  def setUp(self):
#    self.client = Client()

    def test_create(self):
        R = self.client.get('/vendor/edit/')
        self.assertEqual(R.status_code, 200)

        R = self.client.post('/vendor/edit/', {'name':'testa', 'site':'http://xyz.com/xyz'})
        self.assertRedirects(R, '/vendor/')

        M = Vendor.objects.get(name='testa')
        self.assertEqual(M.site,'http://xyz.com/xyz')

    def test_edit(self):
        M = Vendor.objects.create(name='testb', site='http://mmm.abc/nnn')

        R = self.client.get('/vendor/edit/testb/')
        self.assertEqual(R.status_code, 200)

        F = R.context['form']

        self.assertFalse(F.is_bound)
        self.assertFalse(F.is_valid())
        self.assertEqual(F['name'].value(), 'testb')
        self.assertEqual(F['site'].value(), 'http://mmm.abc/nnn')

        # Rename vendor
        R = self.client.post('/vendor/edit/testb/', {'name':'testc', 'site':'http://abc.xyz/a'})
        self.assertRedirects(R, '/vendor/')

        self.assertRaises(Vendor.DoesNotExist, Vendor.objects.get, name='testb')
        M = Vendor.objects.get(name='testc')
        self.assertEqual(M.site, 'http://abc.xyz/a')

    def test_delete(self):
        M = Vendor.objects.create(name='testd', site='http://mmm.abc/nnn')
    
        # Get confirmation page
        R = self.client.get('/vendor/delete/testd/')
        self.assertEqual(R.status_code, 200)
    
        N = Vendor.objects.get(name='testd')
        self.assertEqual(M, N)
    
        # Actually delete
        R = self.client.post('/vendor/delete/testd/')
        self.assertRedirects(R, '/vendor/')
    
        self.assertRaises(Vendor.DoesNotExist, Vendor.objects.get, name='testd')

class PartView(TestCase):
    def setUp(self):
        self.V = Vendor.objects.create(name='testv')

    def test_create(self):
        R = self.client.get('/part/edit/')
        self.assertEqual(R.status_code, 200)
    
        R = self.client.post('/part/edit/', {'oem':self.V.pk,'partnum':'abcd','count':0,
                                             'desc':'test part'})
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/part/testv/abcd/')
    
        R = self.client.get('/part/testv/abcd/')
        self.assertEqual(R.status_code, 200)
    
        R = self.client.get('/part/edit/testv/abcd/')
        self.assertEqual(R.status_code, 200)

    def test_delete(self):
        Part.objects.create(oem=self.V, partnum='xyz', desc='another part')
    
        R = self.client.get('/part/delete/testv/xyz/')
        self.assertEqual(R.status_code, 200)
    
        R = self.client.post('/part/delete/testv/xyz/')
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/')

    def test_edit(self):
        Part.objects.create(oem=self.V, partnum='xyz', desc='another part')
    
        R = self.client.get('/part/edit/testv/xyz/')
        self.assertEqual(R.status_code, 200)
    
        R = self.client.post('/part/edit/testv/xyz/',
                             {'oem':self.V.pk,'partnum':'other','count':42,
                              'desc':'another name'})
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/part/testv/other/')
    
        self.assertRaises(Part.DoesNotExist, Part.objects.get, oem=self.V, partnum='xyz')
    
        M = Part.objects.get(oem=self.V, partnum='other')
        self.assertEqual(M.desc, 'another name')
        self.assertEqual(M.count, 42)

    def test_dec(self):
        P = Part.objects.create(oem=self.V, partnum='xyz', count=5, desc='another part')

        R = self.client.get('/part/use/testv/xyz/?next=/')
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/')

        self.assertEqual(Part.objects.get(pk=P.pk).count, 4)

        R = self.client.get('/part/use/testv/xyz/')
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/part/testv/xyz/')

        self.assertEqual(Part.objects.get(pk=P.pk).count, 3)

    def test_home(self):
        p = Part.objects.create(oem=self.V, partnum='xyz')
        Part.indexer.update()
        R = self.client.get('')
        self.assertEqual(R.status_code, 200)
        self.assertEqual(list(R.context['object_list']), [p])

class SupplyView(TestCase):
    def setUp(self):
        self.V = Vendor.objects.create(name='testv')
        self.S = Vendor.objects.create(name='tests')
        self.P = Part.objects.create(oem=self.V, partnum='apart', desc='something')

    def test_create(self):
        R = self.client.get('/part/supply/add/testv/apart/')
        self.assertEqual(R.status_code, 200)
    
        R = self.client.post('/part/supply/add/testv/apart/',
                             {'seller':self.S.pk,'partnum':'altnum','url':'http://tests.com'})
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/part/testv/apart/')
    
        S = Supply.objects.get(part=self.P, seller=self.S, partnum='altnum')
        self.assertEqual(S.partnum, 'altnum')

    def test_delete(self):
        S = Supply.objects.create(part=self.P, seller=self.S, partnum='altnum', url='http://tests.com')
    
        R = self.client.get('/part/supply/edit/testv/apart/tests/')
        self.assertEqual(R.status_code, 200)
    
        R = self.client.post('/part/supply/delete/testv/apart/tests/')
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/part/testv/apart/')
    
        self.assertRaises(Supply.DoesNotExist, Supply.objects.get, part=self.P,
                          seller=self.S, partnum='altnum')
          
    def test_edit(self):
        S = Supply.objects.create(part=self.P, seller=self.S, partnum='altnum', url='http://tests.com')
    
        R = self.client.get('/part/supply/edit/testv/apart/tests/')
        self.assertEqual(R.status_code, 200)
    
        R = self.client.post('/part/supply/edit/testv/apart/tests/',
                             {'seller':self.V.pk, 'partnum':'second', 'url':'http://tests.com'})
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/part/testv/apart/')

class InfoView(TestCase):
    def setUp(self):
        self.V = Vendor.objects.create(name='testv')
        self.P = Part.objects.create(oem=self.V, partnum='apart', desc='something')

    def test_info(self):
        R = self.client.post('/part/addinfo/testv/apart/',
                             {'desc':'aaa', 'url':'http://xyz.com/'})
        self.assertEqual(R.status_code, 302)
        self.assertRedirects(R, '/part/testv/apart/')
    
        fp, fname = tempfile.mkstemp()
        fp = os.fdopen(fp, 'r+b')
        try:
            fp.write('test data')
            fp.seek(0)
    
            R = self.client.post('/part/addinfo/testv/apart/',
                                 {'desc':'bbb', 'url':'http://abc.com/','file':fp})
            self.assertEqual(R.status_code, 302)
            self.assertRedirects(R, '/part/testv/apart/')
    
        finally:
            fp.close()
            os.remove(fname)
    
        R = self.client.get('/part/testv/apart/')
        self.assertContains(R, 'http://xyz.com')
    
        O = Info.objects.filter(part=self.P)
        self.assertEqual(len(O), 2)
    
        O = Info.objects.get(part=self.P, desc='bbb')
        O.file.open()
        self.assertEqual(O.file.read(), 'test data')
        O.file.close()
        O.file.delete()

class SearchTest(TestCase):
    def setUp(self):
        self.V1 = Vendor.objects.create(name='testv1')
        self.V2 = Vendor.objects.create(name='testv2')
        C = Part.objects.create
        self.P = [
            C(oem=self.V1, partnum='v1p1', desc='something'),
            C(oem=self.V1, partnum='v1p2', desc='something and another'),
            C(oem=self.V1, partnum='v1p3', desc='a keyword and some others...'),
            C(oem=self.V2, partnum='v2p1', desc='some interesting thing'),
            C(oem=self.V2, partnum='v2p2', desc='plural somethings'),
            C(oem=self.V2, partnum='v2p3', desc='random'),
        ]
        Part.indexer.update()

    def test_listall(self):
        R = self.client.get('')
        self.assertEqual(R.status_code, 200)
        self.assertSetEqual(set(R.context['object_list']), set(self.P))

    def test_vendorfilt(self):
        R = self.client.get('', {'vendor':'testv1'})
        self.assertEqual(R.status_code, 200)
        self.assertSetEqual(set(R.context['object_list']), set(self.P[:3]))

    def test_work(self):
        R = self.client.get('', {'query':'keyword'})
        self.assertEqual(R.status_code, 200)
        self.assertSetEqual(set(R.context['object_list']), set(self.P[2:3]))

        R = self.client.get('', {'query':'something'})
        self.assertEqual(R.status_code, 200)
        self.assertSetEqual(set(R.context['object_list']), set([self.P[n] for n in [0,1,4]]))

    def test_wild(self):
        R = self.client.get('', {'query':'some*'})
        self.assertEqual(R.status_code, 200)
        self.assertSetEqual(set(R.context['object_list']), set(self.P[0:5]))
