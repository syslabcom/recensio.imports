from zope.interface import Interface
from zope import schema

class IRecensioImport(Interface):
    pass

class IRecensioImportConfiguration(Interface):
    authors = schema.TextLine(title = u'authors')
    url = schema.TextLine(title = u'url')
    bezugsautoren = schema.TextLine(title = u'bezugsautoren')
    seitenzahl = schema.TextLine(title = u'seitenzahl')
    reihe = schema.TextLine(title = u'reihe')
    reihennummer = schema.TextLine(title = u'reihennummer')
    rezensionAutor = schema.TextLine(title = u'rezensionAutor')
    praesentiertenSchriftTextsprache = schema.TextLine(title = u'praesentiertenSchriftTextsprache')
    praesentationTextsprache = schema.TextLine(title = u'praesentationTextsprache')
    recensioID = schema.TextLine(title = u'recensioID')
    schlagwoerter = schema.TextLine(title = u'schlagwoerter')
    pdf = schema.TextLine(title = u'pdf')
    doc = schema.TextLine(title = u'doc')
    rezension = schema.TextLine(title = u'rezension')
    ddcRaum = schema.TextLine(title = u'ddcRaum')
    ddcSach = schema.TextLine(title = u'ddcSach')
    ddcZeit = schema.TextLine(title = u'ddcZeit')
    untertitel = schema.TextLine(title = u'untertitel')
    erscheinungsjahr = schema.TextLine(title = u'erscheinungsjahr')
    erscheinungsort = schema.TextLine(title = u'erscheinungsort')
    verlag = schema.TextLine(title = u'verlag')
    verbundID = schema.TextLine(title = u'verbundID')
    trefferdaten = schema.TextLine(title = u'trefferdaten')
    isbn = schema.TextLine(title = u'isbn')
