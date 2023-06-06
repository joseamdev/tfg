#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import unittest

sys.path.append('..')
from pdf_reader import PdfReader


class TestPdfReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        with open('reader.tsv') as file:
            tsv = csv.DictReader(file, dialect='excel-tab')
            cls.pa = list()
            for line in tsv:
                reader = PdfReader(line["filename"])
                cls.pa.append({'reader': reader, 'tsv': line})

    def test_abstract(self):
        for item in self.pa:
            self.assertEqual(item['reader'].abstract(), item['tsv']['description'])

    def test_figure_count(self):
        for item in self.pa:
            self.assertEqual(item['reader'].figure_count, int(item['tsv']['figures']))

    def test_keywords(self):
        for item in self.pa:
            subject = item['tsv']['subject'].split(' ; ') if item['tsv']['subject'] else []
            self.assertEqual(item['reader'].keywords(), subject)

    def test_table_count(self):
        for item in self.pa:
            self.assertEqual(item['reader'].table_count, int(item['tsv']['tables']))

    def test_title(self):
        for item in self.pa:
            self.assertEqual(item['reader'].title(), item['tsv']['title'])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPdfReader)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
