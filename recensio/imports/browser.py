from Products.Five.browser import BrowserView
from zc.testbrowser.browser import Browser
from plone.app.registry.browser import controlpanel
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import urllib2
import xmlrpclib
from sha import sha

from recensio.imports.interfaces import IRecensioImport, IRecensioImportConfiguration

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
        self.import_folder.invokeFactory('Review einer Monographie', doc_id, **data)

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

class RecensioImportConfigurationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = RecensioImportConfigurationEditForm
