# -*- coding: utf-8 -*-
from OFS.Image import File
from Products.statusmessages.interfaces import IStatusMessage
from cStringIO import StringIO
from recensio.contenttypes.content.presentationcollection import \
    PresentationCollection
from recensio.contenttypes.content.presentationarticlereview import \
    PresentationArticleReview
from recensio.contenttypes.content.presentationmonograph import \
    PresentationMonograph
from recensio.contenttypes.content.reviewjournal import ReviewJournal
from swiss.tabular import XlsReader
from recensio.contenttypes.content.reviewmonograph import ReviewMonograph
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from zc.testbrowser.browser import Browser
from plone.app.registry.browser import controlpanel
from pyPdf.utils import PdfReadError
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import pyPdf
import transaction
import urllib2
import xmlrpclib
from sha import sha

from recensio.imports.interfaces import IRecensioImport, \
    IRecensioImportConfiguration
from recensio.contenttypes.setuphandlers import addOneItem

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
           ,'rez. nachname' : 'reviewAuthorLastname'
           ,'rez. vorname' : 'reviewAuthorFirstname'
           ,'autor vorname' : 'firstname_authors_1'
           ,'autor nachname' : 'lastname_authors_1'
           ,'titel werk' : 'title'
           ,'start' : 'pageStart'
           ,'ende' : 'pageEnd'
           ,'typ' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'partner url' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        ,'rz' : {
            'portal_type' : ReviewJournal
           ,'isbn/issn' : 'issn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. nachname' : 'reviewAuthorLastname'
           ,'rez. vorname' : 'reviewAuthorFirstname'
           ,'autor vorname' : 'firstname_authors_1'
           ,'autor nachname' : 'lastname_authors_1'
           ,'titel werk' : 'title'
           ,'start' : 'pageStart'
           ,'ende' : 'pageEnd'
           ,'typ' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'partner url' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        ,'pm' : {
            'portal_type' : PresentationMonograph
           ,'isbn/issn' : 'isbn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. nachname' : 'reviewAuthorLastname'
           ,'rez. vorname' : 'reviewAuthorFirstname'
           ,'autor vorname' : 'firstname_authors_1'
           ,'autor nachname' : 'lastname_authors_1'
           ,'titel werk' : 'title'
           ,'start' : 'pageStart'
           ,'ende' : 'pageEnd'
           ,'typ' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'partner url' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        ,'pasb' : {
            'portal_type' : PresentationCollection
           ,'isbn/issn' : 'isbn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. nachname' : 'reviewAuthorLastname'
           ,'rez. vorname' : 'reviewAuthorFirstname'
           ,'autor vorname' : 'firstname_authors_1'
           ,'autor nachname' : 'lastname_authors_1'
           ,'titel werk' : 'title'
           ,'start' : 'pageStart'
           ,'ende' : 'pageEnd'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'typ' : 'ignore'
           ,'partner url' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        ,'paz' : {
            'portal_type' : PresentationArticleReview
           ,'isbn/issn' : 'isbn'
           ,'jahr' : 'yearOfPublication'
           ,'rez. nachname' : 'reviewAuthorLastname'
           ,'rez. vorname' : 'reviewAuthorFirstname'
           ,'autor vorname' : 'firstname_authors_1'
           ,'autor nachname' : 'lastname_authors_1'
           ,'titel werk' : 'title'
           ,'start' : 'pageStart'
           ,'ende' : 'pageEnd'
           ,'typ' : 'ignore'
           ,'partner url' : 'ignore'
           ,'review journal' : 'ignore'
           ,'rj' : 'ignore'
           ,'typ' : 'ignore'
           ,'optionales zitierschema' : 'customCitation'}
        }
    portal_type_mappings[''] = portal_type_mappings['rz']
    ignored_fields = ['typ', '']

    reference_header = ['', u'isbn/issn', u'jahr', u'rez. vorname', \
        u'rez. nachname', u'autor vorname', u'autor nachname', u'titel werk', \
        u'start', u'ende', u'typ', u'partner url', \
        u'optionales zitierschema', '', u'review journal', u'rj']
    unicode_convert = [u'isbn/issn', u'jahr', u'rez. vorname', \
        u'rez. nachname', u'autor vorname', u'autor nachname', u'titel werk', \
        u'optionales zitierschema']


    template = ViewPageTemplateFile('templates/mag_import.pt')

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
        try:
            xls_data = XlsReader(xls).read().data
            keys = [x.strip().lower() for x in xls_data[4]]
            if keys != self.reference_header:
                columns = []
                for i in range(max(len(keys), len(self.reference_header))):
                    column = []
                    try:
                        column.append(self.reference_header[i])
                    except IndexError:
                        column.append('Spalte muss leer sein!')
                    try:
                        column.append(xls_data[4][i])
                    except IndexError:
                        column.append('Spalte ist Leer!')
                    try:
                        column.append(self.reference_header[i] == \
                            xls_data[4][i].strip().lower() and 'Ja' or 'Nein')
                    except IndexError:
                        column.append("Nein")
                    if column[-1] == 'Nein':
                        css_class = 'bad'
                    else:
                        css_class = 'good'
                    columns.append({'columns' : column, \
                                    'css_class' : css_class})
                self.header_error = columns
                raise FrontendException()
        except TypeError, e:
            self.errors.append('Excel Datei konnte nicht gelesen werden, '\
                               'evtl. mit PDF vertauscht?')
            transaction.doom()
            raise FrontendException()
        except FrontendException, e:
            self.errors.append(u'Die Excel Datei enthält Daten, '\
                               u'die das Programm nicht versteht')
            transaction.doom()
            raise FrontendException()

        for count, row in enumerate(xls_data[6:]):
            if len([x for x in row if x]) <= 1:
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
            data['authors'] = 'firstname:%(firstname_authors_1)s,'\
                              'lastname:%(lastname_authors_1)s' % data
            data['pageStart'], data['pageEnd'] = map(int, [data['pageStart'], \
                                                           data['pageEnd']])
            fname = pdf.filename
            data['pdf'] = File(id=fname, title=fname,
                        file=self.splitPages(pdf, data['pageStart'], \
                                                  data['pageEnd']),
                        content_type='application/pdf')
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
            self.errors.append('PDF Datei kann nicht gelesen werden')
            raise FrontendException()
        writer = pyPdf.PdfFileWriter()

        inputPages = [reader.getPage(i) for i in range(reader.getNumPages())]
        pages = inputPages[start:end]
        for page in pages:
            writer.addPage(page)

        fakefile = StringIO()
        writer.write(fakefile)
        return fakefile
