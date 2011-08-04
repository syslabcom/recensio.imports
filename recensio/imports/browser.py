# -*- coding: utf-8 -*-
from cStringIO import StringIO
from sha import sha
import urllib2
import xmlrpclib

from swiss.tabular import XlsReader
from swiss.tabular.xls import xlrd
import pyPdf
from pyPdf.utils import PdfReadError

from OFS.Image import File
from zc.testbrowser.browser import Browser
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import getUtility
import transaction

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry

from recensio.contenttypes.content.presentationcollection import \
    PresentationCollection
from recensio.contenttypes.content.presentationarticlereview import \
    PresentationArticleReview
from recensio.contenttypes.content.presentationmonograph import \
    PresentationMonograph
from recensio.contenttypes.content.presentationonlineresource import \
    PresentationOnlineResource
from recensio.contenttypes.content.reviewjournal import ReviewJournal
from recensio.contenttypes.content.reviewmonograph import ReviewMonograph
from recensio.contenttypes.setuphandlers import addOneItem
from recensio.policy import recensioMessageFactory as _
from recensio.policy.tools import convertToString

from recensio.imports.interfaces import IRecensioImport, \
    IRecensioImportConfiguration


def viewPage(br):
    file('/tmp/bla.html', 'w').write(str(br.contents))

class Import(BrowserView):
    """
    This view is responsible for importing reviews from another site.

    This view gets triggered by cron jobs. The cron job triggers a script
    that throws exceptions.
    So if this view triggers an exception, the script will give output,
    and the cronjob assumes, something went wrong and sends a notification
    mail. Therefor take care that every error condition throws exceptions.
    """
    def __call__(self, url, user, password):
        count = 0
        browser = Browser(url)
        browser.getControl(name = '__ac_name').value = user
        browser.getControl(name = '__ac_password').value = password
        browser.getControl('Log in').click()
        objects = xmlrpclib.loads(browser.contents)[0][0]
        import_utility = IRecensioImport(self.context)
        for object in objects:
            path = object['path']
            if import_utility.exists(path):
                raise Exception('Object already exists')
            else:
                self.add(object)
                count += 1
                import_utility.add(path)
        return "Successfully imported %i items" % count

    def add(self, obj):
        settings = self.registry_settings
        keys = settings.__schema__._v_attrs.keys()
        data = {}
        for key in keys:
            path = getattr(settings, key)
            if not path:
                continue
            path_elems = path.split('->')
            value = obj
            for path_elem in path_elems:
                value = value[path_elem]
            data[key] = value
        doc_id = sha(str(obj)).hexdigest()
        self.import_folder.invokeFactory('Review einer Monographie', doc_id, \
                                         **data)

    @property
    def import_folder(self):
        return self.context.imports

    @property
    def registry_settings(self):
        if not hasattr(self, '_settings'):
            registry = getUtility(IRegistry)
            self._settings = registry.forInterface(IRecensioImportConfiguration)
        return self._settings

class RecensioImportConfigurationEditForm(controlpanel.RegistryEditForm):
    schema = IRecensioImportConfiguration
    label = 'Recensio Import settings'
    description = ''

class RecensioImportConfigurationControlPanel(\
        controlpanel.ControlPanelFormWrapper):
    form = RecensioImportConfigurationEditForm

class FrontendException(Exception):
    pass

class MagazineImport(object):
    portal_type_mappings =  {
        'rm' : {
            'portal_type' : ReviewMonograph
           ,'isbn/issn' : 'isbn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. vorname' : 'firstname_review_authors_1'
           ,'rez. nachname' : 'lastname_review_authors_1'
           ,'titel werk' : 'title'
           ,'print seite start' : 'pageStart'
           ,'print seite ende' : 'pageEnd'
           ,'pdf start' : 'pdfPageStart'
           ,'pdf ende' : 'pdfPageEnd'
           ,'typ' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rez.sprache' : 'languageReview'
           ,'textsprache' : 'languageReviewedText'
           ,'rj' : 'ignore'
           ,'partner url' : 'uri'
           ,'optionales zitierschema' : 'customCitation'}
        ,'rj' : {
            'portal_type' : ReviewJournal
           ,'isbn/issn' : 'issn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. vorname' : 'firstname_review_authors_1'
           ,'rez. nachname' : 'lastname_review_authors_1'
           ,'titel werk' : 'title'
           ,'print seite start' : 'pageStart'
           ,'print seite ende' : 'pageEnd'
           ,'pdf start' : 'pdfPageStart'
           ,'pdf ende' : 'pdfPageEnd'
           ,'typ' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'rez.sprache' : 'languageReview'
           ,'textsprache' : 'languageReviewedText'
           ,'partner url' : 'uri'
           ,'optionales zitierschema' : 'customCitation'}
        ,'pm' : {
            'portal_type' : PresentationMonograph
           ,'isbn/issn' : 'isbn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. vorname' : 'firstname_review_authors_1'
           ,'rez. nachname' : 'lastname_review_authors_1'
           ,'titel werk' : 'title'
           ,'print seite start' : 'pageStart'
           ,'print seite ende' : 'pageEnd'
           ,'pdf start' : 'pdfPageStart'
           ,'pdf ende' : 'pdfPageEnd'
           ,'typ' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'partner url' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        ,'pace' : {
            'portal_type' : PresentationCollection
           ,'isbn/issn' : 'isbn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. vorname' : 'firstname_review_authors_1'
           ,'rez. nachname' : 'lastname_review_authors_1'
           ,'titel werk' : 'title'
           ,'print seite start' : 'pageStart'
           ,'print seite ende' : 'pageEnd'
           ,'pdf start' : 'pdfPageStart'
           ,'pdf ende' : 'pdfPageEnd'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'typ' : 'ignore'
           ,'partner url' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        ,'paj' : {
            'portal_type' : PresentationArticleReview
           ,'isbn/issn' : 'issn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. vorname' : 'firstname_review_authors_1'
           ,'rez. nachname' : 'lastname_review_authors_1'
           ,'titel werk' : 'title'
           ,'print seite start' : 'pageStart'
           ,'print seite ende' : 'pageEnd'
           ,'pdf start' : 'pdfPageStart'
           ,'pdf ende' : 'pdfPageEnd'
           ,'typ' : 'ignore'
           ,'partner url' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'typ' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        ,'por' : {
            'portal_type' : PresentationOnlineResource
           ,'isbn/issn' : 'isbn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. vorname' : 'firstname_review_authors_1'
           ,'rez. nachname' : 'lastname_review_authors_1'
           ,'titel werk' : 'title'
           ,'print seite start' : 'pageStart'
           ,'print seite ende' : 'pageEnd'
           ,'pdf start' : 'pdfPageStart'
           ,'pdf ende' : 'pdfPageEnd'
           ,'typ' : 'ignore'
           ,'partner url' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'typ' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}

        }
    ignored_fields = ['typ', '']

    reference_header = ['', u'isbn/issn', u'jahr', u'rez. vorname',
                        u'rez. nachname', u'titel werk', u'print seite start',
                        u'print seite ende', u'pdf start', u'pdf ende',
                        u'typ', u'rez.sprache',
                        u'textsprache', u'partner url',
                        u'optionales zitierschema', '', u'review journal',
                        u'rj']
    translate_headers = {
        'isbn/issn werk' : 'isbn/issn'
       ,'isbn/issn (work)' : 'isbn/issn'
       ,'jahr werk' : 'jahr'
       ,'year (work)' : 'jahr'
       ,'rez. vorname' : 'rez. vorname'
       ,'reviewer firstname' : 'rez. vorname'
       ,'rez. nachname' : 'rez. nachname'
       ,'reviewer last name' : 'rez. nachname'
       ,'titel werk' : 'titel werk'
       ,'title of the work' : 'titel werk'
       ,'print seite start' : 'print seite start'
       ,'print start page' : 'print seite start'
       ,'print seite ende' : 'print seite ende'
       ,'print end page' : 'print seite ende'
       ,'pdf start' : 'pdf start'
       ,'pdf ende' : 'pdf ende'
       ,'pdf end' : 'pdf ende'
       ,'typ' : 'typ'
       ,'type' : 'typ'
       ,'rez.sprache' : 'rez.sprache'
       ,'language rev.' : 'rez.sprache'
       ,'textsprache' : 'textsprache'
       ,'language text' : 'textsprache'
       ,'partner url' : 'partner url'
       ,'optionales zitierschema' : 'optionales zitierschema'
       ,'optional custom citation format' : 'optionales zitierschema'
    }

    unicode_convert = [u'isbn/issn', u'jahr', u'rez. vorname',
        u'rez. nachname', u'titel werk',
        u'optionales zitierschema', u'rez.sprache', u'textsprache']

    template = ViewPageTemplateFile('templates/mag_import.pt')

    def __init__(self, *args, **kwargs):
        self.warnings = []
        super(MagazineImport, self).__init__(*args, **kwargs)

    def __call__(self):
        self.import_successful = False
        self.results = []
        self.errors = []
        self.header_error = []
        for key in ['xls', 'pdf']:
            if key not in self.request.form.keys():
                return self.template(self)
        try:
            self.addContent(self.request.form['xls'], self.request.form['pdf'])
        except FrontendException, e:
            messages = IStatusMessage(self.request)
            for error in self.errors:
                messages.addStatusMessage(error, type='error')
            return self.template(self)
        self.import_successful = True
        return self.template(self)

    def addContent(self, xls, pdf):
        if xls.filename == "" or pdf.filename == "":
            self.errors.append(
                _(u"help_import_error_file_missing",
                  default=(u"Please ensure that you have selected both "
                           "a PDF file and an Excel file")
                  )
                )
            raise FrontendException()
        try:
            xls_data = XlsReader(xls).read().data
            keys = [self.translate_headers.get(x.strip().lower(), x.strip().lower()) for x in xls_data[4]]
            if keys != self.reference_header:
                columns = []
                for i in range(max(len(keys), len(self.reference_header))):
                    column = []
                    try:
                        column.append(self.reference_header[i])
                    except IndexError:
                        column.append(_('Spalte muss leer sein!'))
                    try:
                        column.append(xls_data[4][i])
                    except IndexError:
                        column.append(_('Spalte ist Leer!'))
                    try:
                        column.append(self.reference_header[i] == \
                        xls_data[4][i].strip().lower() and \
                                      _('Ja') or _('Nein')
                                      )
                    except IndexError:
                        column.append(_("Nein"))
                    if column[-1] == _('Nein'):
                        css_class = 'bad'
                    else:
                        css_class = 'good'
                    columns.append({'columns' : column, \
                                    'css_class' : css_class})
                self.header_error = columns
                raise FrontendException()
        except TypeError, e:
            self.errors.append(_(u'Excel Datei konnte nicht gelesen werden, '
                                 'evtl. mit PDF vertauscht?'))
            transaction.doom()
            raise FrontendException()
        except FrontendException, e:
            self.errors.append(_(u'Die Excel Datei enthält Daten, '
                                 'die das Programm nicht versteht'))
            transaction.doom()
            raise FrontendException()
        except xlrd.XLRDError, e:
            self.errors.append(
                _(u"help_import_error_unsupported_xls",
                  u"Please ensure that the xls file you selected is a valid "
                  "Excel file")
                )
            transaction.doom()
            raise FrontendException()

        for count, row in enumerate(xls_data[6:]):
            if len([x for x in row[1:15] if x]) <= 1:
                continue
            mapping = self.portal_type_mappings[row[keys.index('typ')]]
            data = {'portal_type' : mapping['portal_type']}
            for index, key in enumerate(keys):
                if key not in self.ignored_fields:
                    if key in self.unicode_convert:
                        try:
                            data[mapping[key]] = unicode(int(row[index]))
                        except ValueError:
                            data[mapping[key]] = unicode(row[index])
                    else:
                        data[mapping[key]] = row[index]
            portal_type = data.pop('portal_type')
            data['reviewAuthors'] = 'firstname:%(firstname_review_authors_1)s,'\
                'lastname:%(lastname_review_authors_1)s' % data
            data['pageStart'], data['pageEnd'] = map(int, [data['pageStart'],
                                                           data['pageEnd']])
            data['pdfPageStart'], data['pdfPageEnd'] = \
                map(int, [data['pdfPageStart'],
                          data['pdfPageEnd']])
            data['languageReview'] =\
                self.convertLanguages(data['languageReview'])
            data['languageReviewedText'] =\
                self.convertLanguages(data['languageReviewedText'])
            fname = pdf.filename
            data['pdf'] = File(id=fname, title=fname,
                        file=self.splitPages(pdf, data['pdfPageStart']-1, \
                                                  data['pdfPageEnd']), 
                        content_type='application/pdf')
            del data['pdfPageStart']
            del data['pdfPageEnd']
            data = convertToString(data)
            result = addOneItem(self.context, portal_type, data)
            self.results.append({'name' : result.title, \
                                 'url' : result.absolute_url()})
        if self.errors:
            raise FrontendException()

    def splitPages(self, pdf, start, end):
        try:
            reader = pyPdf.PdfFileReader(pdf)
        except PdfReadError:
            transaction.doom()
            self.errors.append(_('PDF Datei kann nicht gelesen werden'))
            raise FrontendException()
        writer = pyPdf.PdfFileWriter()

        inputPages = [reader.getPage(i) for i in range(reader.getNumPages())]
        pages = inputPages[start:end]
        for page in pages:
            writer.addPage(page)

        fakefile = StringIO()
        writer.write(fakefile)
        return fakefile

    def convertLanguages(self, data):
        data = data.replace(';', ' ').replace('.', ' ')\
            .replace(':', ' ').replace(',', ' ')
        data = [x.strip().lower() for x in data.split() if x.strip()]
        retval = []
        for lang in data:
            if lang in self.supported_languages:
                retval.append(lang)
            else:
                warning = _('The language "${lang}" is unknown',
                            default='Die Sprache "${lang}" is unbekannt',
                            mapping={"lang": lang})
                self.warnings.append(warning)
        return tuple(retval)

    @property
    def supported_languages(self):
        if not hasattr(self, '_supported_languages'):
            util = getUtility(IVocabularyFactory,
                              'recensio.policy.vocabularies.'
                              'available_content_languages')
            vocab = util(self)
            self._supported_languages = vocab.by_token.keys()
        return self._supported_languages
