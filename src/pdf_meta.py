#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import PyPDF2


class PdfMeta:

    CONTRIBUTOR = 'contributor'
    COVERAGE = 'coverage'
    CREATOR = 'creator'
    DATE = 'date'
    DESCRIPTION = 'description'
    FORMAT = 'format'
    IDENTIFIER = 'identifier'
    LANGUAGE = 'language'
    PUBLISHER = 'publisher'
    RELATION = 'relation'
    RIGHTS = 'rights'
    SOURCE = 'source'
    SUBJECT = 'subject'
    TITLE = 'title'
    TYPE = 'type'

    ENGLISH_TITLE = 'en'
    DEFAULT_TITLE = 'x-default'

    def __init__(self, pdf_path: str):
        with open(pdf_path, "rb") as pdf_file:
            try:
                reader = PyPDF2.PdfFileReader(pdf_file)
            except PyPDF2.errors.PyPdfError:
                raise Exception(f'Error occurred trying to read {pdf_path}')
            self.num_pages: int = len(reader.pages)
            self.doc_authors: list = self.__parse_doc_author(reader.metadata)
            self.doc_creator: str = self.__parse_doc_creator(reader.metadata)
            self.doc_producer: str = self.__parse_doc_producer(reader.metadata)
            self.doc_subject: str = self.__parse_doc_subject(reader.metadata)
            self.doc_title: str = self.__parse_doc_title(reader.metadata)
            self.xmp_info = dict()
            self.xmp_info[self.CONTRIBUTOR] = self.__parse_xmp_list_attribute(reader.xmp_metadata, self.CONTRIBUTOR)
            self.xmp_info[self.COVERAGE] = self.__parse_xmp_str_attribute(reader.xmp_metadata, self.COVERAGE)
            self.xmp_info[self.CREATOR] = self.__parse_xmp_list_attribute(reader.xmp_metadata, self.CREATOR)
            self.xmp_info[self.DATE] = self.__parse_xmp_date(reader.xmp_metadata)
            self.xmp_info[self.DESCRIPTION] = self.__parse_xmp_description(reader.xmp_metadata)
            self.xmp_info[self.FORMAT] = self.__parse_xmp_str_attribute(reader.xmp_metadata, self.FORMAT)
            self.xmp_info[self.IDENTIFIER] = self.__parse_xmp_str_attribute(reader.xmp_metadata, self.IDENTIFIER)
            self.xmp_info[self.LANGUAGE] = self.__parse_xmp_list_attribute(reader.xmp_metadata, self.LANGUAGE)
            self.xmp_info[self.PUBLISHER] = self.__parse_xmp_list_attribute(reader.xmp_metadata, self.PUBLISHER)
            self.xmp_info[self.RELATION] = self.__parse_xmp_list_attribute(reader.xmp_metadata, self.RELATION)
            self.xmp_info[self.RIGHTS] = self.__parse_xmp_rights(reader.xmp_metadata)
            self.xmp_info[self.SOURCE] = self.__parse_xmp_str_attribute(reader.xmp_metadata, self.SOURCE)
            self.xmp_info[self.SUBJECT] = self.__parse_xmp_list_attribute(reader.xmp_metadata, self.SUBJECT)
            self.xmp_info[self.TITLE] = self.__parse_xmp_title(reader.xmp_metadata)
            self.xmp_info[self.TYPE] = self.__parse_xmp_list_attribute(reader.xmp_metadata, self.TYPE)

    @property
    def xmp_contributor(self) -> list[str]:
        return self.xmp_info[self.CONTRIBUTOR]

    @property
    def xmp_coverage(self) -> list[str]:
        return self.xmp_info[self.COVERAGE]

    @property
    def xmp_creator(self) -> list[str]:
        return self.xmp_info[self.CREATOR]

    @property
    def xmp_date(self) -> list[str]:
        return self.xmp_info[self.DATE]

    @property
    def xmp_description(self) -> list[str]:
        return self.xmp_info[self.DESCRIPTION]

    @property
    def xmp_format(self) -> list[str]:
        return self.xmp_info[self.FORMAT]

    @property
    def xmp_identifier(self) -> list[str]:
        return self.xmp_info[self.IDENTIFIER]

    @property
    def xmp_language(self) -> list[str]:
        return self.xmp_info[self.LANGUAGE]

    @property
    def xmp_publisher(self) -> list[str]:
        return self.xmp_info[self.PUBLISHER]

    @property
    def xmp_relation(self) -> list[str]:
        return self.xmp_info[self.RELATION]

    @property
    def xmp_rights(self) -> list[str]:
        return self.xmp_info[self.RIGHTS]

    @property
    def xmp_source(self) -> list[str]:
        return self.xmp_info[self.SOURCE]

    @property
    def xmp_subject(self) -> list[str]:
        return self.xmp_info[self.SUBJECT]

    @property
    def xmp_title(self) -> list[str]:
        return self.xmp_info[self.TITLE]

    @property
    def xmp_type(self) -> list[str]:
        return self.xmp_info[self.TYPE]

    def __parse_doc_author(self, doc_info: PyPDF2.DocumentInformation) -> list[str]:
        authors = list()
        if doc_info and doc_info.author:
            authors = [author.strip() for author in re.split(r'(?:,|;|&|\sand\s)', str(doc_info.author), re.I)]
        return authors

    def __parse_doc_creator(self, doc_info: PyPDF2.DocumentInformation) -> str:
        creator = ''
        if doc_info and doc_info.creator is not None:
            creator = str(doc_info.creator).strip()
        return creator

    def __parse_doc_producer(self, doc_info: PyPDF2.DocumentInformation) -> str:
        producer = ''
        if doc_info and doc_info.producer is not None:
            producer = str(doc_info.producer).strip()
        return producer

    def __parse_doc_subject(self, doc_info: PyPDF2.DocumentInformation) -> str:
        subject = ''
        if doc_info and doc_info.subject is not None:
            subject = str(doc_info.subject).strip()
        return subject

    def __parse_doc_title(self, doc_info: PyPDF2.DocumentInformation) -> str:
        title = ''
        if doc_info and doc_info.title is not None:
            title = str(doc_info.title).strip()
        return title

    def __parse_xmp_list_attribute(self, xmp_info: PyPDF2.xmp.XmpInformation, attrib: str) -> list[str]:
        values = list()
        dc_attribute = self.__dc_attribute(attrib)
        if xmp_info and hasattr(xmp_info, dc_attribute):
            values = self.__stripped_list(getattr(xmp_info, dc_attribute))
        return values

    def __parse_xmp_str_attribute(self, xmp_info: PyPDF2.xmp.XmpInformation, attrib: str) -> list[str]:
        values = list()
        dc_attribute = self.__dc_attribute(attrib)
        if xmp_info and hasattr(xmp_info, dc_attribute):
            attrib_value = getattr(xmp_info, dc_attribute)
            if attrib_value and attrib_value.strip():
                values = [attrib_value.strip()]
        return values

    def __parse_xmp_date(self, xmp_info: PyPDF2.xmp.XmpInformation) -> list[str]:
        dates = list()
        dc_attribute = self.__dc_attribute(self.DATE)
        if xmp_info and hasattr(xmp_info, dc_attribute):
            dates = [i.date().isoformat() for i in xmp_info.dc_date]
        return dates

    def __parse_xmp_description(self, xmp_info: PyPDF2.xmp.XmpInformation) -> list[str]:
        description = list()
        dc_attribute = self.__dc_attribute(self.DESCRIPTION)
        if xmp_info and hasattr(xmp_info, dc_attribute):
            description = list(set(self.__stripped_list(xmp_info.dc_description.values())))
        return description

    def __parse_xmp_rights(self, xmp_info: PyPDF2.xmp.XmpInformation) -> list[str]:
        rights = list()
        dc_attribute = self.__dc_attribute(self.RIGHTS)
        if xmp_info and hasattr(xmp_info, dc_attribute):
            rights = list(set(self.__stripped_list(xmp_info.dc_rights.values())))
        return rights

    def __parse_xmp_title(self, xmp_info: PyPDF2.xmp.XmpInformation) -> list[str]:
        titles = list()
        dc_attribute = self.__dc_attribute(self.TITLE)
        if xmp_info and hasattr(xmp_info, dc_attribute):
            if self.ENGLISH_TITLE in xmp_info.dc_title:
                titles.append(xmp_info.dc_title[self.ENGLISH_TITLE].strip())
            if self.DEFAULT_TITLE in xmp_info.dc_title \
                    and xmp_info.dc_title[self.DEFAULT_TITLE] not in titles:
                titles.append(xmp_info.dc_title[self.DEFAULT_TITLE].strip())
            other_titles = [t for t in self.__stripped_list(xmp_info.dc_title.values())
                            if t not in titles]
            titles.extend(other_titles)
        return titles

    def __dc_attribute(self, attrib: str) -> str:
        return f'dc_{attrib}'

    def __stripped_list(self, strings: list) -> list[str]:
        return [s.strip() for s in strings if s.strip()]
