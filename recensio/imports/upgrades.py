from Products.CMFCore.utils import getToolByName


def issue_language(context):
    cat = getToolByName(context, 'portal_catalog')
    issue_pdfs = cat(getId='issue.pdf')
    for brain in issue_pdfs:
        try:
            obj = brain.getObject()
        except:
            continue
        if obj.Language():
            obj.setLanguage('')
            obj.reindexObject()
