from StringIO import StringIO

import pyPdf

def cutPDF(pdf, start, end):
    reader = pyPdf.PdfFileReader(pdf)
    writer = pyPdf.PdfFileWriter()
    inputPages = [reader.getPage(i) for i in range(reader.getNumPages())]
    pages = inputPages[int(start) - 1:int(end)]
    for page in pages:
        writer.addPage(page)

    fakefile = StringIO()
    writer.write(fakefile)
    fakefile.seek(0)
    return fakefile
