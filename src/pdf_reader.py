#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from langdetect import detect
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTFigure, LTImage, LTTextLine

from pdf_block import PdfBlock


class PdfReader:
    def __init__(self, file_path: str):
        self.image_count: int = 0
        self.figure_count: int = 0
        self.table_count: int = 0
        self.text_blocks = list()
        self.__read_pages(file_path)

    def abstract(self) -> str:
        result = ''
        first_page_blocks = self.page_blocks(1)
        for block in first_page_blocks:
            match_abstract = re.fullmatch(r'(?s)abstract\W*(.*)', block.text, re.I)
            if match_abstract:
                result = re.sub(r'-[\r\n]', '', match_abstract.group(1))
                result = re.sub(r'\s+', ' ', result.strip())
                if not result and len(self.text_blocks) > block.block_number:
                    result = self.text_blocks[block.block_number].text
                    result = re.sub(r'-[\r\n]', '', match_abstract.group(1))
                    result = re.sub(r'\s+', ' ', result.strip())
                break
        return result

    def keywords(self) -> list:
        result = list()
        first_page_blocks = self.page_blocks(1)
        for block in first_page_blocks:
            text_stripped = re.sub(r'\s+', ' ', block.text)
            match_keywords = re.fullmatch(r"(?s)key ?words?\W+(.+?)\.?", text_stripped, re.I)
            if match_keywords:
                result = re.split(r'\s*[,;]\s*', match_keywords.group(1))
        return result

    def page_blocks(self, page_number: int, to_page: int = None) -> list:
        result = list()
        for block in self.text_blocks:
            if self.__is_number_in_range(block.page_number, page_number, to_page):
                result.append(block)
        return result

    def page_text(self, page_number: int, to_page: int = None) -> str:
        result = '\n'.join([block.text for block in self.page_blocks(page_number, to_page)])
        return result

    def text(self) -> str:
        result = '\n'.join([block.text for block in self.text_blocks])
        return result

    def title(self) -> str:
        first_page_blocks = self.page_blocks(1)
        title_blocks = self.__get_title_blocks(first_page_blocks)
        raw_text = ' '.join([block.text for block in title_blocks])
        cleaned_text = re.sub(r'[\s\r\n]+', ' ', raw_text.strip())
        return cleaned_text

    def language(self) -> str:
        result = detect(self.text())
        if result != 'unknown':
            return result
        else:
            return ''

    def __get_title_blocks(self, first_page_blocks: list) -> list:
        blocks = []
        text = ' '
        while not len(re.sub(r'\W', '', text)) and first_page_blocks:
            first_page_blocks = [b for b in first_page_blocks if b not in blocks]
            blocks = self.__filter_text_blocks(first_page_blocks)
            text = ' '.join([b.text for b in blocks])
        return blocks

    def __filter_text_blocks(self, text_blocks: list) -> list:
        max_font_size = self.__max_font_size(text_blocks)
        result_blocks = [b for b in text_blocks if b.font_size() == max_font_size
                         and b.is_bold() and b.top_margin_percent < 50]
        if not result_blocks:
            result_blocks = [b for b in text_blocks if b.font_size() == max_font_size]
        return result_blocks

    def __max_font_size(self, blocks: list) -> int:
        max_size = 0
        for block in blocks:
            if block.font_size() > max_size:
                max_size = block.font_size()
        return max_size

    def __is_number_in_range(self, number: int, start: int, end: int) -> bool:
        if end is None:
            return number == start
        else:
            return start <= number <= end

    def __read_font_stats(self, container: LTTextContainer) -> tuple:
        size_count = dict()
        bold_count = 0
        italic_count = 0
        char_count = 0
        for element in container:
            if isinstance(element, LTTextLine):
                for character in element:
                    if isinstance(character, LTChar):
                        char_count += 1
                        font_name = character.fontname.lower()
                        if 'bold' in font_name:
                            bold_count += 1
                        if 'italic' in font_name:
                            italic_count += 1
                        font_size = round(character.size)
                        if font_size in size_count:
                            size_count[font_size] += 1
                        else:
                            size_count[font_size] = 1
        if char_count:
            sizes = {s: c / char_count for s, c in size_count.items()}
            return sizes, bold_count / char_count, italic_count / char_count
        else:
            return dict(), 0.0, 0.0

    def __read_elements(self, parent):
        for element in parent:
            if isinstance(element, LTTextContainer):
                element_text = element.get_text().strip()
                if not element_text:
                    continue
                self.__block_count += 1
                sizes, bold, italic = self.__read_font_stats(element)
                top_margin = element.y0 * 100 / self.__page_height
                left_margin = element.x0 * 100 / self.__page_width
                self.text_blocks.append(
                    PdfBlock(
                        page_number=self.__page_count,
                        block_number=self.__block_count,
                        text=element_text,
                        top_margin_percent=top_margin,
                        left_margin_percent=left_margin,
                        font_sizes=sizes,
                        font_bold_rate=bold,
                        font_italic_rate=italic,
                    )
                )
                text_no_spaces = re.sub(r'\s+', '', element_text)
                if m := re.match(r'table(\d+)', text_no_spaces, re.I):
                    self.__table_ids.add(m.group(1))
                elif m := re.match(r'fig(?:\.?|ure)(\d+)', text_no_spaces, re.I):
                    self.__figure_ids.add(m.group(1))
            elif isinstance(element, LTFigure):
                self.__read_elements(element)
            elif isinstance(element, LTImage):
                if element.stream.objid:
                    self.__image_ids.add(element.stream.objid)
                else:
                    self.__image_ids.add(element.name)

    def __read_pages(self, file_path: str) -> None:
        self.__block_count = 0
        self.__page_count = 0
        self.__image_ids = set()
        self.__figure_ids = set()
        self.__table_ids = set()
        all_pages = list(extract_pages(file_path, maxpages=0))
        for page in all_pages:
            self.__page_count += 1
            self.__page_width = page.width
            self.__page_height = page.height
            self.__read_elements(page)
        self.image_count = len(self.__image_ids)
        self.figure_count = len(self.__figure_ids)
        self.table_count = len(self.__table_ids)
