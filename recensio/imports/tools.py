import sys, urllib

def triggerPloneImportFromRecensio():
    trigger_url = sys.argv[1]
    target_url = urllib.quote(sys.argv[2])
    urllib.urlopen('%s?url=%s' % (trigger_url, target_url))
