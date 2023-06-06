#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as etree

import pandas as pd

from pdf_analytics import PdfAnalytics


class PdfFolder:
    DC_NS = {'dc': 'http://purl.org/dc/elements/1.1/'}

    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.analytics = self.__get_pdf_analytics()
        etree.register_namespace('dc', self.DC_NS['dc'])

    def pdf_paths(self) -> list[str]:
        return [pdf.filepath for pdf in self.analytics]

    def to_file(self, xml_path: str) -> None:
        tree = self.__xml()
        with open(xml_path, 'w') as xml_file:
            tree.write(xml_file, encoding='unicode', xml_declaration=True)

    def to_xml(self) -> str:
        tree = self.__xml()
        result = etree.tostring(tree.getroot(), encoding='unicode')
        return result

    def dc_dataframe(self) -> pd.DataFrame:
        result = list()
        for pa in self.analytics:
            values = {'filename': pa.filename}
            values.update(self.__get_tag_values(pa))
            result.append(values)
        return pd.DataFrame.from_dict(result)

    def stats_dataframe(self) -> pd.DataFrame:
        result = list()
        for pa in self.analytics:
            values = {'filename': pa.filename}
            values['pages'] = pa.page_count()
            values['figures'] = pa.figure_count()
            values['tables'] = pa.table_count()
            values['images'] = pa.image_count()
            result.append(values)
        return pd.DataFrame.from_dict(result)

    def __get_pdf_files(self) -> list:
        result = list()
        for file in os.listdir(self.folder_path):
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(self.folder_path, file)
                result.append(pdf_path)
        return result

    def __get_pdf_analytics(self) -> list:
        result = list()
        for pdf_path in self.__get_pdf_files():
            pa = PdfAnalytics(pdf_path)
            result.append(pa)
        return result

    def __dc_tag(self, tag: str) -> str:
        return f'{{{self.DC_NS["dc"]}}}{tag}'

    def __get_tag_values(self, pdf: PdfAnalytics) -> dict:
        return {
            'contributor': pdf.contributor(),
            'coverage': pdf.coverage(),
            'creator': pdf.creator(),
            'date': pdf.date(),
            'description': pdf.description(),
            'format': pdf.format_(),
            'identifier': pdf.identifier(),
            'language': pdf.language(),
            'publisher': pdf.publisher(),
            'relation': pdf.relation(),
            'rights': pdf.rights(),
            'source': pdf.source(),
            'subject': pdf.subject(),
            'title': pdf.title(),
            'type': pdf.type_()
            }

    def __analytics_to_xml(self, pdf: PdfAnalytics) -> etree.Element:
        pdf_tree = etree.Element('paper', attrib={'filename': pdf.filename})
        pdf_tree.set('pages', str(pdf.page_count()))
        pdf_tree.set('tables', str(pdf.table_count()))
        pdf_tree.set('figures', str(pdf.figure_count()))
        tag_values = self.__get_tag_values(pdf)
        for tag in tag_values:
            for value in tag_values[tag]:
                element = etree.SubElement(pdf_tree, self.__dc_tag(tag))
                element.text = value
        return pdf_tree

    def __xml(self) -> etree.ElementTree:
        root = etree.Element('metadata')
        for pdf in self.analytics:
            pdf_xml = self.__analytics_to_xml(pdf)
            root.append(pdf_xml)
        tree = etree.ElementTree(root)
        etree.indent(tree, space="\t", level=0)
        return tree
