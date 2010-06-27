from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.interfaces import ISiteRoot

from recensio.imports.interfaces import IRecensioImport

RECENSIO_IMPORTS = 'recensio.imports'

class RecensioImportData(object):
    implements(IRecensioImport)
    adapts(ISiteRoot)

    def __init__(self, context):
        self.context = context

    def exists(self, path):
        return path in self.existing_paths

    def add(self, path):
        self.existing_paths.append(path)

    @property
    def existing_paths(self):
        if not hasattr(self, '_paths'):
            annotations = IAnnotations(self.context)
            self._paths = annotations.get(RECENSIO_IMPORTS, [])
        return self._paths
