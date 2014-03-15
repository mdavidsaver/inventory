#!/usr/bin/env python
"""
Copyright (C) 2013 Michael Davidsaver
Licensed under AGPL 3+
See file "LICENSE" for full terms
"""

import os, os.path, sys
import urllib2, re
import traceback

from tempfile import SpooledTemporaryFile

os.environ['DJANGO_SETTINGS_MODULE'] = 'inventory.settings'

from django.core.files import File

from inventory import models

# for http Content-Disposition
cdisp = re.compile('\W*attachment\W*;\W*filename\W*="([^"]*)"\W*')

for I in models.Info.objects.all():
  if I.file:
    continue

  print 'For',I.part
  print ' Fetch',I.url


  try:
    R = urllib2.urlopen(I.url)

    M = cdisp.match(R.info().get('Content-Disposition',''))
    if M:
      fname = os.path.basename(M.group(1))
      print ' Dispose as',fname

    else:
      U = urllib2.urlparse.urlparse(R.url)
      fname = os.path.basename(U.path)
      print ' Save as',fname

    F = SpooledTemporaryFile(max_size=R.info().get('content-length',0))

    while True:
        D = R.read(1024*1024)
        if len(D)==0:
            break
        F.write(D)

  except IOError:
    traceback.print_exc()
    continue

  else:
    FS = F.tell()
    F.seek(0,0)

    DF=File(F)
    DF.size = FS

    I.file.save(fname, DF)

  finally:
    R.close()

print 'Done'

