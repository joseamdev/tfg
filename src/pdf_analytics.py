#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from pdf_meta import PdfMeta
from pdf_nlp import PdfNlp
from pdf_reader import PdfReader

import pandas as pd


class PdfAnalytics:
    PDF_FORMAT = 'application/pdf'
    ENGLISH = 'en'

    def __init__(self, pdf_path: str):
        self.filepath = pdf_path
        self.filename = os.path.split(pdf_path)[1]
        self._meta = PdfMeta(self.filepath)
        self._reader = PdfReader(self.filepath)
        self._nlp = PdfNlp(self._reader.text())

    def page_count(self) -> int:
        return self._meta.num_pages

    def figure_count(self) -> int:
        return self._reader.figure_count

    def table_count(self) -> int:
        return self._reader.table_count

    def image_count(self) -> int:
        return self._reader.image_count

    def contributor(self) -> list[str]:
        return self._meta.xmp_contributor

    def coverage(self) -> list[str]:
        return self._meta.xmp_coverage

    def creator(self) -> list[str]:
        if self._meta.xmp_creator:
            return self._meta.xmp_creator
        return self._meta.doc_authors

    def date(self) -> list[str]:
        return self._meta.xmp_date

    def description(self) -> list[str]:
        if self._meta.xmp_description:
            return self._meta.xmp_description
        elif abstract := self._reader.abstract():
            return [abstract]
        return []

    def format_(self) -> list[str]:
        if self._meta.xmp_format:
            return self._meta.xmp_format
        return [self.PDF_FORMAT]

    def identifier(self) -> list[str]:
        return self._meta.xmp_identifier

    def language(self) -> list[str]:
        lang = []
        if xmp_lang := self._meta.xmp_language:
            lang = xmp_lang
        elif reader_lang := self._reader.language():
            lang = [reader_lang]
        return lang

    def publisher(self) -> list[str]:
        if self._meta.xmp_publisher:
            return self._meta.xmp_publisher
        elif self._meta.doc_creator:
            return [self._meta.doc_creator]
        return []

    def relation(self) -> list[str]:
        return self._meta.xmp_relation

    def rights(self) -> list[str]:
        return self._meta.xmp_rights

    def source(self) -> list[str]:
        return self._meta.xmp_source

    def subject(self) -> list[str]:
        if self._meta.xmp_subject:
            return self._meta.xmp_subject
        elif self._reader.keywords():
            return self._reader.keywords()
        bf5 = [' '.join(b[0]) for b in self._nlp.bigrams_freq(5)]
        return bf5

    def title(self) -> list[str]:
        if self._meta.xmp_title:
            return self._meta.xmp_title
        elif self._reader.title():
            return [self._reader.title()]
        return [self._meta.doc_title]

    def type_(self) -> list[str]:
        return self._meta.xmp_type

    def dc_dataframe(self) -> pd.DataFrame:
        dc_values = {
            'contributor': self.contributor(),
            'coverage': self.coverage(),
            'creator': self.creator(),
            'date': self.date(),
            'description': self.description(),
            'format': self.format_(),
            'identifier': self.identifier(),
            'language': self.language(),
            'publisher': self.publisher(),
            'relation': self.relation(),
            'rights': self.rights(),
            'source': self.source(),
            'subject': self.subject(),
            'title': self.title(),
            'type': self.type_()
            }
        df = pd.DataFrame.from_dict([dc_values])
        df.index = [self.filename]
        return df.transpose()

    def stats_dataframe(self) -> pd.DataFrame:
        values = dict()
        values['pages'] = self.page_count()
        values['figures'] = self.figure_count()
        values['tables'] = self.table_count()
        values['images'] = self.image_count()
        df = pd.DataFrame.from_dict([values])
        df.index = [self.filename]
        return df.transpose()
