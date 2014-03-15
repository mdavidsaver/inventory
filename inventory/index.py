"""
Copyright (C) 2013 Michael Davidsaver
Licensed under AGPL 3+
See file "LICENSE" for full terms
"""

from djapian import space, Indexer, CompositeIndexer

from models import *

class PartIndexer(Indexer):
  fields = ['desc','partnum']

space.add_index(Part, PartIndexer, attach_as='indexer')

complete_indexer = CompositeIndexer(Part.indexer)
