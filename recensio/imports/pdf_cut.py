from StringIO import StringIO

import pyPdf


class RecensioPdfFileWriter(pyPdf.PdfFileWriter):
    def _sweepIndirectReferences(self, externMap, data):
        try:
            return super(RecensioPdfFileWriter, self)._sweepIndirectReferences(
                externMap, data
            )
        except KeyError:
            return data


def cutPDF(pdf, start, end):
    reader = pyPdf.PdfFileReader(pdf)
    writer = RecensioPdfFileWriter()
    inputPages = [reader.getPage(i) for i in range(reader.getNumPages())]
    pages = inputPages[int(start) - 1 : int(end)]
    for page in pages:
        writer.addPage(page)

    fakefile = StringIO()
    writer.write(fakefile)
    fakefile.seek(0)
    return fakefile
