#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass
class PdfBlock:
    page_number: int
    block_number: int
    text: str
    top_margin_percent: float
    left_margin_percent: float
    font_sizes: dict[int, float]
    font_bold_rate: float
    font_italic_rate: float

    def font_size(self) -> int:
        if self.font_sizes:
            return sorted(self.font_sizes.items(), key=lambda x: x[1], reverse=True)[0][0]
        else:
            return 0

    def is_bold(self) -> bool:
        return self.font_bold_rate > 0.5

    def is_italic(self) -> bool:
        return self.font_bold_italic > 0.5
