import math
import string
from typing import Dict

from PIL import ImageDraw
from PIL import Image as PILImage

from Config import GlyphConfig

from .Glyph import Glyph
from .GlyphColor import GlyphColor
from .GlyphShape import GlyphShape
from .GlyphTemplate import GlyphTemplate


class GlyphFactory:
    def __init__(self, config: GlyphConfig):
        self._alphabet: str = ' ' + string.digits + \
            string.ascii_letters + string.punctuation + '💩' + '😄'
        self._error_char = '?'
        self._error_color = GlyphColor.RED

        assert self._error_char in self._alphabet

        self._templates: Dict[GlyphShape] = {
            GlyphShape.DEFAULT: GlyphTemplate(
                alphabet=self._alphabet,
                font_path=config.font_path,
                font_size=config.font_size,
                horizontal_pad=config.horizontal_pad,
                vertical_pad=config.vertical_pad,
                border_width=config.border_width,
                square=config.square),
            GlyphShape.WIDE: GlyphTemplate(
                alphabet=self._alphabet,
                font_path=config.font_path,
                font_size=config.font_size,
                horizontal_pad=config.wide_horizontal_pad,
                vertical_pad=config.wide_vertical_pad,
                border_width=config.border_width,
                square=False)}

    def create_glyph(self,
                     char: str,
                     color: GlyphColor,
                     shape: GlyphShape) -> Glyph:

        tpl = self._templates[shape]

        if char not in self._alphabet:
            char = self._error_char
            color = self._error_color

        fill_color = color.value[0]
        border_color = color.value[1]
        font_color = color.value[2]

        # Create the main glyph tile
        tile = PILImage.new('RGBA', tpl.size)
        draw = ImageDraw.Draw(tile, 'RGBA')
        draw.rectangle(tpl.coords, fill=fill_color)

        draw.text(
            tpl.char_coords,
            text=char,
            font=tpl.font,
            fill=font_color)

        draw.rectangle(
            xy=(0, 0, tile.width-1, tile.height-1),
            fill=None,
            outline=border_color,
            width=tpl.border_width)

        return Glyph(name=char, image=tile, font=tpl.font,
                     shape=shape, color=color)
