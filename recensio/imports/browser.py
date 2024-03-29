# -*- coding: utf-8 -*-
from logging import getLogger
from plone import api
from plone.app.async.interfaces import IAsyncService
from plone.app.registry.browser import controlpanel
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.registry.interfaces import IRegistry
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from recensio.contenttypes.setuphandlers import addOneItem
from recensio.imports.excel_converter import ExcelConverter
from recensio.imports.excel_converter import ExcelURNExtractor
from recensio.imports.interfaces import IRecensioImport
from recensio.imports.interfaces import IRecensioImportConfiguration
from recensio.imports.pdf_cut import cutPDF
from recensio.imports.zip_extractor import ZipExtractor
from recensio.policy import recensioMessageFactory as _
from sha import sha
from Testing import makerequest
from zc.testbrowser.browser import Browser
from ZODB.POSException import ConflictError
from zope.component import getUtility
from zope.event import notify

import transaction
import xmlrpclib


log = getLogger("recensio.imports.browser")


def viewPage(br):
    file("/tmp/bla.html", "w").write(str(br.contents))


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
        browser.getControl(name="__ac_name").value = user
        browser.getControl(name="__ac_password").value = password
        browser.getControl("Log in").click()
        objects = xmlrpclib.loads(browser.contents)[0][0]
        import_utility = IRecensioImport(self.context)
        for object in objects:
            path = object["path"]
            if import_utility.exists(path):
                raise Exception("Object already exists")
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
            path_elems = path.split("->")
            value = obj
            for path_elem in path_elems:
                value = value[path_elem]
            data[key] = value
        doc_id = sha(str(obj)).hexdigest()
        self.import_folder.invokeFactory("Review einer Monographie", doc_id, **data)

    @property
    def import_folder(self):
        return self.context.imports

    @property
    def registry_settings(self):
        if not hasattr(self, "_settings"):
            registry = getUtility(IRegistry)
            self._settings = registry.forInterface(IRecensioImportConfiguration)
        return self._settings


class RecensioImportConfigurationEditForm(controlpanel.RegistryEditForm):
    schema = IRecensioImportConfiguration
    label = "Recensio Import settings"
    description = ""


class RecensioImportConfigurationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = RecensioImportConfigurationEditForm


class FrontendException(Exception):
    pass


def batch_import(context, batch):
    for (uuid, urn) in batch:
        brain = uuidToCatalogBrain(uuid)
        document = context.restrictedTraverse(brain["path_string"])
        document.setUrn(urn)


class URNImport(object):
    template = ViewPageTemplateFile("templates/urn_import.pt")
    BATCH_SIZE = 1000

    def __init__(self, *args, **kwargs):
        self.import_successful = False
        self.errors = []
        super(URNImport, self).__init__(*args, **kwargs)

    def __call__(self):
        if "xls" in self.request.form:
            self.handleXLSImport(self.request.form["xls"])
        return self.template(self)

    def handleXLSImport(self, xls_document):
        self.import_successful = True
        data = ExcelURNExtractor()(xls_document)
        async = getUtility(IAsyncService)
        for index in range(0, len(data), self.BATCH_SIZE):
            batch_import(self.context, data[index : index + self.BATCH_SIZE])
            async.queueJob(
                batch_import, self.context, data[index : index + self.BATCH_SIZE]
            )


class MagazineImport(object):
    template = ViewPageTemplateFile("templates/mag_import.pt")

    def __init__(self, *args, **kwargs):
        self.warnings = []
        self.errors = []
        self.import_successful = False
        self.results = []
        self.header_error = []
        self.excel_converter = ExcelConverter()
        self.zip_extractor = ZipExtractor()
        super(MagazineImport, self).__init__(*args, **kwargs)

    def __call__(self):
        req_has_key = (
            lambda x: x in self.request.form.keys() and self.request.form[x].filename
        )
        if req_has_key("xls") and req_has_key("pdf"):
            try:
                self.addPDFContent(self.request.form["xls"], self.request.form["pdf"])
            except FrontendException, e:
                messages = IStatusMessage(self.request)
                for error in self.errors:
                    messages.addStatusMessage(error, type="error")
            else:
                pdf_id = self.context.invokeFactory(
                    "File", id="issue.pdf", title="issue.pdf"
                )
                obj = self.context[pdf_id]
                obj.setLanguage("")
                obj.update_data(self.request.form["pdf"])
                request = makerequest.makerequest(obj)
                event = ObjectInitializedEvent(obj, request)
                notify(event)
                self.import_successful = True
        elif req_has_key("zip"):
            try:
                self.addZIPContent(self.request.form["zip"])
            except FrontendException, e:
                messages = IStatusMessage(self.request)
                for error in self.errors:
                    messages.addStatusMessage(error, type="error")
            else:
                self.import_successful = True
        return self.template(self)

    def addPDFContent(self, xls, pdf):
        try:
            results = self.excel_converter.convert_xls(xls)
        except Exception, e:
            if isinstance(e, ConflictError):
                raise
            if hasattr(self.excel_converter, "header_error"):
                self.header_error = self.excel_converter.header_error
            log.exception(str(e))
            self.errors.append(str(e))
            transaction.doom()
            raise FrontendException()
        finally:
            self.warnings = self.excel_converter.warnings
        gnd_view = api.content.get_view(
            context=self.context, request=self.request, name="gnd-view",
        )
        pdf_name = pdf.filename
        for result in results:
            start, end = [int(result.pop("pdfPage" + x) or 0) for x in "Start", "End"]
            module, class_ = result.pop("portal_type")
            portal_type = self.type_getter(module, class_)
            result["pdf"] = cutPDF(pdf, start, end)

            authors = []
            for person in result["reviewAuthors"]:
                lastname = person["lastname"].replace("(", '"("').replace(")", '")"')
                firstname = person["firstname"].replace("(", '"("').replace(")", '")"')
                existing = gnd_view.getByName(
                    firstname=firstname,
                    lastname=lastname,
                    solr=False,  # solr is only committed on transaction commit
                )
                if existing:
                    authors.append(existing[0].getObject())
                else:
                    authors.append(
                        gnd_view.createPerson(
                            firstname=firstname,
                            lastname=lastname,
                        )
                    )
            result["reviewAuthors"] = authors

            result_item = addOneItem(self.context, portal_type, result)
            self.results.append(
                {"name": result_item.title, "url": result_item.absolute_url()}
            )
        if self.errors:
            raise FrontendException()

    def addZIPContent(self, zipfile):
        try:
            xls, docs = self.zip_extractor(zipfile)
            results = [x for x in self.excel_converter.convert_zip(xls)]
        except Exception, e:
            if isinstance(e, ConflictError):
                raise
            log.exception(str(e))
            self.errors.append(str(e))
            transaction.doom()
            raise FrontendException()
        finally:
            self.warnings = self.excel_converter.warnings
        if len(docs) != len(results):
            self.errors.append(
                _(
                    "The number of documents in the zip file do not match "
                    "the number of entries in the excel file"
                )
            )
            transaction.doom()
            raise FrontendException()
        for result, doc in zip(results, docs):
            result["doc"] = doc
            module, class_ = result.pop("portal_type")
            portal_type = self.type_getter(module, class_)
            result_item = addOneItem(self.context, portal_type, result)
            self.results.append(
                {"name": result_item.title, "url": result_item.absolute_url()}
            )
        if self.errors:
            raise FrontendException()

    def type_getter(self, module_path, class_):
        module = __import__(module_path)
        for modname in module_path.split(".")[1:]:
            module = getattr(module, modname)
        return getattr(module, class_)
