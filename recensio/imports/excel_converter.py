# -*- coding: utf-8 -*-

from recensio.policy import recensioMessageFactory as _
from recensio.policy.tools import convertToString
from swiss.tabular import XlsReader
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import xlrd


class ExcelURNExtractor(object):
    """
    Convert a given excel file to a dictionary of UUID->URN
    """

    REFERENCE_HEADER = ["recensio-id", "urn"]

    def __call__(self, xls_file):
        retval = []
        try:
            xls_data = XlsReader(xls_file).read().data
        except TypeError:
            raise TypeError(_(u"Excel Datei konnte nicht gelesen werden"))
        except xlrd.XLRDError:
            raise Exception(
                _(
                    u"help_import_error_unsupported_xls",
                    (
                        u"Please ensure that the xls file you selected is a valid "
                        u"Excel file"
                    ),
                )
            )
        header = xls_data[0]
        errors = []
        for i in range(max(len(header), len(self.REFERENCE_HEADER))):
            if len(header) < i - 1:
                errors.append(
                    "Das Excel Dokument enthält zu wenige Spalten. Folgende Spalten sind das Minimum: %s"
                    % (" ".join(self.REFERENCE_HEADER))
                )
                break
            if len(self.REFERENCE_HEADER) < i - 1:
                errors.append(
                    "Das Excel Dokument enthält zu viele Spalten. Es dürfen nur folgende Spalten vorkommen: %s"
                    % (" ".join(self.REFERENCE_HEADER))
                )
                break
            if header[0].lower().strip() != self.REFERENCE_HEADER[0]:
                errors.append(
                    "Spalte %i ist falsch. Ist: %s, Soll: %s (Gross und Kleinschreibung wird ignoriert"
                    % (i + 1, header[0].strip(), self.REFERENCE_HEADER[i])
                )
        if errors:
            raise TypeError("Do not understand Excel File", errors=errors)

        retval = []
        for count, row in enumerate(xls_data[1:]):
            retval.append(row)
        return retval


class ExcelConverter(object):
    """
    Convert a given excel file to a list of content types and their initial data
    """

    translate_headers = {
        "isbn/issn werk": "isbn/issn",
        "isbn/issn (work)": "isbn/issn",
        "jahr werk": "jahr",
        "year (work)": "jahr",
        "rez. vorname": "rez. vorname",
        "reviewer firstname": "rez. vorname",
        "rez. nachname": "rez. nachname",
        "reviewer last name": "rez. nachname",
        "titel werk": "titel werk",
        "title of the work": "titel werk",
        "print seite start": "print seite start",
        "print start page": "print seite start",
        "print seite ende": "print seite ende",
        "print end page": "print seite ende",
        "pdf start": "pdf start",
        "pdf ende": "pdf ende",
        "pdf end": "pdf ende",
        "typ": "typ",
        "type": "typ",
        "rez.sprache": "rez.sprache",
        "language rev.": "rez.sprache",
        "textsprache": "textsprache",
        "language text": "textsprache",
        "original url": "original url",
        "optionales zitierschema": "optionales zitierschema",
        "optional custom citation format": "optionales zitierschema",
        "doi": "doi",
    }

    ignored_fields = ["typ", ""]

    unicode_convert = [
        u"isbn/issn",
        u"jahr",
        u"rez. vorname",
        u"rez. nachname",
        u"titel werk",
        u"optionales zitierschema",
        u"rez.sprache",
        u"textsprache",
    ]

    reference_header_zip = [
        "",
        u"isbn/issn",
        u"jahr",
        u"rez. vorname",
        u"rez. nachname",
        u"titel werk",
        u"print seite start",
        u"print seite ende",
        u"filename",
        u"typ",
        u"rez.sprache",
        u"textsprache",
        u"original url",
        u"optionales zitierschema",
        "doi",
        "",
        "",
        u"review journal",
        u"rj",
    ]
    reference_header_xls = [
        "",
        u"isbn/issn",
        u"jahr",
        u"rez. vorname",
        u"rez. nachname",
        u"titel werk",
        u"print seite start",
        u"print seite ende",
        u"pdf start",
        u"pdf ende",
        u"typ",
        u"rez.sprache",
        u"textsprache",
        u"original url",
        u"optionales zitierschema",
        "doi",
        "",
        u"review journal",
        u"rj",
    ]

    portal_type_mappings = {
        "rm": {
            "portal_type": (
                "recensio.contenttypes.content.reviewmonograph",
                "ReviewMonograph",
            ),
            "isbn/issn": "isbn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStartOfReviewInJournal",
            "print seite ende": "pageEndOfReviewInJournal",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "review journal": "ignore",
            "rez.sprache": "languageReview",
            "textsprache": "languageReviewedText",
            "rj": "ignore",
            "original url": "canonical_uri",
            "optionales zitierschema": "customCitation",
            "doi": "doi",
        },
        "rj": {
            "portal_type": (
                "recensio.contenttypes.content.reviewjournal",
                "ReviewJournal",
            ),
            "isbn/issn": "issn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStartOfReviewInJournal",
            "print seite ende": "pageEndOfReviewInJournal",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "review journal": "ignore",
            "rj": "ignore",
            "rez.sprache": "languageReview",
            "textsprache": "languageReviewedText",
            "original url": "canonical_uri",
            "optionales zitierschema": "customCitation",
            "doi": "doi",
        },
        "raj": {
            "portal_type": (
                "recensio.contenttypes.content.reviewarticlejournal",
                "ReviewArticleJournal",
            ),
            "isbn/issn": "issn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStartOfReviewInJournal",
            "print seite ende": "pageEndOfReviewInJournal",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "review journal": "ignore",
            "rj": "ignore",
            "rez.sprache": "languageReview",
            "textsprache": "languageReviewedText",
            "original url": "canonical_uri",
            "optionales zitierschema": "customCitation",
            "doi": "doi",
        },
        "raev": {
            "portal_type": (
                "recensio.contenttypes.content.reviewarticlecollection",
                "ReviewArticleCollection",
            ),
            "isbn/issn": "issn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStartOfReviewInJournal",
            "print seite ende": "pageEndOfReviewInJournal",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "review journal": "ignore",
            "rj": "ignore",
            "rez.sprache": "languageReview",
            "textsprache": "languageReviewedText",
            "original url": "canonical_uri",
            "optionales zitierschema": "customCitation",
            "doi": "doi",
        },
        "re": {
            "portal_type": (
                "recensio.contenttypes.content.reviewexhibition",
                "ReviewExhibition",
            ),
            "isbn/issn": "ignore",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStartOfReviewInJournal",
            "print seite ende": "pageEndOfReviewInJournal",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "review journal": "ignore",
            "rj": "ignore",
            "rez.sprache": "languageReview",
            "textsprache": "ignore",
            "original url": "canonical_uri",
            "optionales zitierschema": "customCitation",
            "doi": "doi",
        },
        "pm": {
            "portal_type": (
                "recensio.contenttypes.content" ".presentationmonograph",
                "PresentationMonograph",
            ),
            "isbn/issn": "isbn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStart",
            "print seite ende": "pageEnd",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "review journal": "ignore",
            "rj": "ignore",
            "original url": "ignore",
            "optionales zitierschema": "customCitation",
        },
        "pace": {
            "portal_type": (
                "recensio.contenttypes.content.presentation" "collection",
                "PresentationCollection",
            ),
            "isbn/issn": "isbn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStart",
            "print seite ende": "pageEnd",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "review journal": "ignore",
            "rj": "ignore",
            "typ": "ignore",
            "original url": "ignore",
            "optionales zitierschema": "customCitation",
        },
        "paj": {
            "portal_type": (
                "recensio.contenttypes.content.presentation" "articlereview",
                "PresentationArticleReview",
            ),
            "isbn/issn": "issn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStart",
            "print seite ende": "pageEnd",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "original url": "ignore",
            "review journal": "ignore",
            "rj": "ignore",
            "typ": "ignore",
            "optionales zitierschema": "customCitation",
        },
        "por": {
            "portal_type": (
                "recensio.contenttypes.presentation" "onlineresource",
                "PresentationOnlineResource",
            ),
            "isbn/issn": "isbn",
            "jahr": "yearOfPublication",
            "rez. vorname": "firstname_review_authors_1",
            "rez. nachname": "lastname_review_authors_1",
            "titel werk": "title",
            "print seite start": "pageStart",
            "print seite ende": "pageEnd",
            "filename": "filename",
            "pdf start": "pdfPageStart",
            "pdf ende": "pdfPageEnd",
            "typ": "ignore",
            "original url": "ignore",
            "review journal": "ignore",
            "rj": "ignore",
            "typ": "ignore",
            "optionales zitierschema": "customCitation",
        },
    }

    def __init__(self):
        self.warnings = []

    def convert_zip(self, xls_file):
        return self.convert(xls_file, self.reference_header_zip)

    def convert_xls(self, xls_file):
        return self.convert(xls_file, self.reference_header_xls)

    def convert(self, xls_file, reference_header):
        retval = []
        try:
            xls_data = XlsReader(xls_file).read().data
        except TypeError:
            raise TypeError(
                _(
                    u"Excel Datei konnte nicht gelesen werden, "
                    "evtl. mit PDF vertauscht?"
                )
            )
        except xlrd.XLRDError, e:
            raise Exception(
                _(
                    u"help_import_error_unsupported_xls",
                    (
                        u"Please ensure that the xls file you selected is a valid "
                        u"Excel file"
                    ),
                )
            )

        keys = [
            self.translate_headers.get(x.strip().lower(), x.strip().lower())
            for x in xls_data[4]
        ]
        if keys != reference_header:
            columns = []
            for i in range(max(len(keys), len(reference_header))):
                column = []
                try:
                    column.append(reference_header[i])
                except IndexError:
                    column.append(_("Spalte muss leer sein!"))
                try:
                    column.append(xls_data[4][i])
                except IndexError:
                    column.append(_("Spalte ist Leer!"))
                try:
                    column.append(
                        reference_header[i] == xls_data[4][i].strip().lower()
                        and _("Ja")
                        or _("Nein")
                    )
                except IndexError:
                    column.append(_("Nein"))
                if column[-1] == _("Nein"):
                    css_class = "bad"
                else:
                    css_class = "good"
                columns.append({"columns": column, "css_class": css_class})
            self.header_error = columns
            raise Exception(
                _(u"Die Excel Datei enthaelt Daten, " "die das Programm nicht versteht")
            )

        for count, row in enumerate(xls_data[6:]):
            if len([x for x in row[1:15] if x]) <= 1:
                continue
            try:
                mapping = self.portal_type_mappings[row[keys.index("typ")]]
            except KeyError, e:
                raise KeyError(
                    _(
                        u"Die Excel Datei beinhaltet Daten, "
                        u"die das Programm nicht versteht."
                        u" Bitte schauen Sie, ob jeder Date"
                        u"nsatz einen Typ angegeben hat."
                    )
                )
            data = {"portal_type": mapping["portal_type"]}
            for index, key in enumerate(keys):
                if key not in self.ignored_fields:
                    if key in self.unicode_convert:
                        try:
                            data[mapping[key]] = unicode(int(row[index]))
                        except ValueError:
                            data[mapping[key]] = unicode(row[index])
                    else:
                        data[mapping[key]] = row[index]
            data["reviewAuthors"] = [
                {
                    "firstname": data["firstname_review_authors_1"],
                    "lastname": data["lastname_review_authors_1"],
                },
            ]
            # data['reviewAuthors'] = 'firstname:%(firstname_review_authors_1)s,'\
            #    'lastname:%(lastname_review_authors_1)s' % data
            (
                data["pageStartOfReviewInJournal"],
                data["pageEndOfReviewInJournal"],
            ) = map(
                int,
                [
                    data["pageStartOfReviewInJournal"] or 0,
                    data["pageEndOfReviewInJournal"] or 0,
                ],
            )
            data["languageReview"] = self.convertLanguages(data["languageReview"])
            if data.get("languageReviewedText"):
                data["languageReviewedText"] = self.convertLanguages(
                    data["languageReviewedText"]
                )
            data = convertToString(data)
            retval.append(data)
        return retval

    def convertLanguages(self, data):
        data = (
            data.replace(";", " ").replace(".", " ").replace(":", " ").replace(",", " ")
        )
        data = [x.strip().lower() for x in data.split() if x.strip()]
        retval = []
        for lang in data:
            if lang in self.supported_languages:
                retval.append(lang)
            else:
                warning = _(
                    'The language "${lang}" is unknown',
                    default='Die Sprache "${lang}" is unbekannt',
                    mapping={"lang": lang},
                )
                self.warnings.append(warning)
        return tuple(retval)

    @property
    def supported_languages(self):
        if not hasattr(self, "_supported_languages"):
            util = getUtility(
                IVocabularyFactory,
                "recensio.policy.vocabularies." "available_content_languages",
            )
            vocab = util(self)
            self._supported_languages = vocab.by_token.keys()
        return self._supported_languages
