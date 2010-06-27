from Products.CMFCore.utils import getToolByName
from logging import getLogger

log = getLogger('recensio.imports.setuphandlers.py')

def guard(func):
    def wrapper(self):
        if self.readDataFile('recensio.imports_marker.txt') is None:
            return
        return func(self)
    return wrapper

@guard
def setUpImportFolder(context):
    portal = context.getSite()
    wftool = getToolByName(portal, 'portal_workflow')
    def getOrAdd(context, type, name):
        if name not in context.objectIds():
            context.invokeFactory(type, name)
            new_object = context[name]
            wftool.doActionFor(new_object, 'publish')
        return context[name]

    getOrAdd(portal, 'Folder', 'imports')
