import sys, urllib
from zc.testbrowser.browser import Browser

def triggerPloneImportFromRecensio():
    trigger_url, trigger_user, trigger_pass = sys.argv[1:4]
    target_url, user, password = map(urllib.quote, sys.argv[4:7])
    browser = Browser('%s?url=%s&user=%s&password=%s' % (trigger_url, target_url,\
        user, password))
    browser.getControl(name = '__ac_name').value = trigger_user
    browser.getControl(name = '__ac_password').value = trigger_pass
    browser.getControl('Anmelden').click()
