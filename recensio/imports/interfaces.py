from zope.interface import Interface
from zope import schema

class IRecensioImport(Interface):
    pass

class IRecensioImportConfiguration(Interface):
    authors = schema.TextLine(title = u'authors')
    url = schema.TextLine(title = u'url')
    referenceAuthors = schema.TextLine(title = u'referenceAuthors')
    pages = schema.TextLine(title = u'pages')
    series = schema.TextLine(title = u'series')
    seriesVol = schema.TextLine(title = u'seriesVol')
    reviewAuthor = schema.TextLine(title = u'reviewAuthor')
    languageReview = schema.TextLine(title = u'languageReview')
    languagePresentation = schema.TextLine(title = u'languagePresentation')
    recensioID = schema.TextLine(title = u'recensioID')
    subject = schema.TextLine(title = u'subject')
    pdf = schema.TextLine(title = u'pdf')
    doc = schema.TextLine(title = u'doc')
    review = schema.TextLine(title = u'review')
    ddcPlace = schema.TextLine(title = u'ddcPlace')
    ddcSubject = schema.TextLine(title = u'ddcSubject')
    ddcTime = schema.TextLine(title = u'ddcTime')
    subtitle = schema.TextLine(title = u'subtitle')
    yearOfPublication = schema.TextLine(title = u'yearOfPublication')
    placeOfPublication = schema.TextLine(title = u'placeOfPublication')
    publisher = schema.TextLine(title = u'publisher')
    idBvb = schema.TextLine(title = u'idBvb')
    searchresults = schema.TextLine(title = u'searchresults')
    isbn = schema.TextLine(title = u'isbn')
