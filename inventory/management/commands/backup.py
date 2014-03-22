# -*- coding: utf-8 -*-
"""
Copyright (C) 2013 Michael Davidsaver
Licensed under AGPL 3+
See file "LICENSE" for full terms

Backup DB, media, and static files.
aka, all non-code data
"""

import os.path, time, shutil
import tempfile

from optparse import make_option

import tarfile

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.commands.dumpdata import Command as DumpCommand

class Command(BaseCommand):
    option_list = DumpCommand.option_list + (
        make_option('-M', '--media', action='store_true', default=False,
                    help='Include MEDIA_ROOT in backup'),
        make_option('-S', '--static', action='store_true', default=False,
                    help='Include STATIC_ROOT in backup'),
        make_option('-O', '--output', default='backup.tar.gz',
                    help='Output backup archive'),
        make_option('-B', '--backup', metavar='NUM', default='0',
                    help='Number of old backups to keep'),
    )

    args = DumpCommand.args

    help = ('Create a tarfile containing a json dump of '
            'some or all of the app DBs and optionally '
            'MEDIA_ROOT and/or STATIC_ROOT files')

    def handle(self, *args, **options):
        print 'backupcmd',args,options

        pdict = {'origin':'django app backup'}
        outfile = options.get('output')

        bnum = int(options.get('backup'))
        if bnum and os.path.isfile(outfile):
            # backup file names
            backups = ['%s.%d'%(outfile,n) for n in range(bnum)]
            backups.reverse() # .2, .1, .0
            print 'backups',backups

            # rotate
            for n in range(1,len(backups)):
                TO, FROM = backups[n-1], backups[n]
                print 'rotate',FROM,TO
                if os.path.isfile(FROM):
                    # eg. Replace .1 with .0
                    if os.path.isfile(TO):
                        os.remove(TO)
                    os.rename(FROM, TO)

            # .0 should not exist
            assert not os.path.isfile(backups[-1])

            os.rename(outfile, backups[-1])

        output = tarfile.open(name=outfile, mode='w:gz',
                              format=tarfile.PAX_FORMAT, pax_headers=pdict)
        try:
            with tempfile.SpooledTemporaryFile(mode='w+') as dout:

                dumpcmd = DumpCommand()

                dumpcmd.stdout = dout
                dumpcmd.stderr = self.stderr
                dumpcmd.handle(*args, **options)
                print 'raw DB dump size',dout.tell()

                dname = output.tarinfo('db.json')
                dname.type = tarfile.REGTYPE
                dname.size = dout.tell()
                dname.mtime = time.time()
                dname.uid = os.geteuid()
                dname.gid = os.getegid()

                dout.seek(0)
                output.addfile(dname, dout)

            if options.get('media') and os.path.isdir(settings.MEDIA_ROOT):
                print 'backup MEDIA_ROOT =',settings.MEDIA_ROOT
                output.add(settings.MEDIA_ROOT, 'media')

            if options.get('static') and os.path.isdir(settings.STATIC_ROOT):
                print 'backup STATIC_ROOT =',settings.STATIC_ROOT
                output.add(settings.STATIC_ROOT, 'static')

            output.list()
            output.close()
        except:
            # delete partial output on error
            output.close()
            os.remove(outfile)
            raise
