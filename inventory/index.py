from djapian import space, Indexer, CompositeIndexer

from models import *

class PartIndexer(Indexer):
  fields = ['desc','partnum']

space.add_index(Part, PartIndexer, attach_as='indexer')

complete_indexer = CompositeIndexer(Part.indexer)
