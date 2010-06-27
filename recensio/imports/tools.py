import sys, urllib

def triggerPloneImportFromRecensio():
    url = sys.argv[1]
    urllib.urlopen(url)
