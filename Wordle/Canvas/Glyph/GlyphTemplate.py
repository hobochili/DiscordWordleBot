from dataclasses import dataclass
import math
from typing import Tuple

from .GlyphFont import GlyphFont


@dataclass
class GlyphTemplate:
    font: GlyphFont
    width: float
    height: float
    vertical_offset: int

    def __init__(self,
                 font_path: str,
                 font_size: int,
                 alphabet: str,
                 horizontal_pad: int,
                 vertical_pad: int,
                 border_width: int,
                 square: bool):

        font = GlyphFont(font_path=font_path, size=font_size)

        bbox_sizes = [font.getbbox(char) for char in alphabet]

        x1s = [bbox[0] for bbox in bbox_sizes]
        x2s = [bbox[2] for bbox in bbox_sizes]
        y1s = [bbox[1] for bbox in bbox_sizes]
        y2s = [bbox[3] for bbox in bbox_sizes]

        x1, y1, x2, y2 = min(x1s), min(y1s), max(x2s), max(y2s)

        mode_y1 = max(y1s, key=y1s.count)

        top_buffer = abs(math.floor(((mode_y1 - y1))/2))

        base_height = y2 - y1 + 2 * vertical_pad
        glyph_height = base_height + top_buffer

        glyph_width = x2 - x1 + 2 * horizontal_pad

        self.font = font
        self.alphabet = alphabet

        self.width = max(glyph_width, glyph_height) if square else glyph_width
        self.height = max(
            glyph_width, glyph_height) if square else glyph_height

        self.border_width = border_width
        self.horizontal_offset = horizontal_pad
        self.vertical_offset = top_buffer + \
            math.ceil(((y1-mode_y1) - (y2 - base_height)) / 2)

    @ property
    def size(self) -> Tuple[int, int]:
        return self.width, self.height

    @ property
    def coords(self) -> Tuple[int, int, int, int]:
        return 0, 0, self.width, self.height

    @ property
    def char_coords(self) -> Tuple[int, int]:
        return (self.horizontal_offset, self.vertical_offset)
