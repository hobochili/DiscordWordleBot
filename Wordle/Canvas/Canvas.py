
import logging
import math
import random
import textwrap

import itertools
from typing import List, Tuple

from PIL import Image as PILImage
from Config import CanvasConfig

from Wordle.Canvas.Glyph import (
    Glyph, GlyphCollection, GlyphColor, GlyphShape,
    GlyphFactory, GlyphNotFound)
from Wordle.Canvas.Image import Image
from Wordle.Canvas.GIFImage import GIFImage


class Canvas:
    def __init__(self, config: CanvasConfig):
        self._glyphs: GlyphCollection = GlyphCollection()
        self._glyph_factory: GlyphFactory = GlyphFactory(config.glyph)

        self.margin = config.margin
        self.spacer_width = config.spacer_width
        self.text_wrap_width = config.text_wrap_width

    @staticmethod
    def map_random_color(input: str) -> Tuple[str, GlyphColor]:
        colors = [
            GlyphColor.GREEN,
            GlyphColor.YELLOW,
            GlyphColor.INVERSE_LIGHT_GRAY
        ]

        return list(map(lambda x: (x, random.choice(colors)) if x != ' ' else (
            x, GlyphColor.CLEAR), input))

    def draw_char(
            self,
            char: str,
            shape: GlyphShape,
            color: GlyphColor) -> Glyph:

        try:
            return self._glyphs.get(name=char, shape=shape, color=color)
        except GlyphNotFound:
            ...

        glyph = self._glyph_factory.create_glyph(
            char=char, shape=shape, color=color)
        self._glyphs.add(glyph)

        logging.getLogger('WordleBot.Canvas').debug(
            f'Added {glyph} to the collection')

        return glyph

    def draw_word(
            self,
            word: List[Tuple[str, GlyphColor]],
            shape: GlyphShape = GlyphShape.DEFAULT) -> Image:

        if not word:
            word = [(' ', GlyphColor.CLEAR)]

        cols = len(word)

        glyphs = [
            self.draw_char(
                char=char[0], shape=shape, color=char[1])
            for char in word if char]

        word_width = sum(
            [glyph.width for glyph in glyphs[0:cols]])
        img_width = word_width + \
            (cols * self.spacer_width) - self.spacer_width

        word_height = max([glyph.height for glyph in glyphs])
        img_height = word_height

        img = PILImage.new('RGBA', (img_width, img_height), color=(0, 0, 0, 0))

        for idx, glyph in enumerate(glyphs):
            x_off = (idx % cols) * (glyph.width + self.spacer_width)
            img.paste(glyph.image, (x_off, 0))

        return Image(image=img)

    def vertical_join(self, images: List[Image], center: bool = True) -> Image:
        if len(images) == 1:
            return images[0]

        width = max([im.width for im in images])
        height = sum(
            [im.height + self.spacer_width for im in images]) - self.spacer_width

        res = PILImage.new('RGBA', size=(width, height))

        y_offset = 0
        for im in images:
            x_offset = max(0, math.ceil(
                (width - im.width) / 2)) if center else 0
            res.paste(im.image, box=(x_offset, y_offset))
            y_offset = y_offset + im.height + self.spacer_width

        return Image(res)

    def draw_text(self, input: str, center: bool = False) -> Image:
        # Split input on line boundaries and replace blank lines
        # with spaces to preserve input format
        lines = map(lambda x: ' ' if x == '\n' else x,
                    input.splitlines(keepends=True))

        # Wrap each line of input text to the configured width
        wrapped = itertools.chain(*map(lambda x: textwrap.wrap(
            text=x, width=self.text_wrap_width, drop_whitespace=False),
            lines))

        return self.vertical_join(
            list(map(lambda x:
                     self.draw_word(word=self.map_random_color(x.strip())),
                     wrapped)),
            center=center)

    def animate_word(
            self,
            word: List[Tuple[str, GlyphColor]],
            shape: GlyphShape = GlyphShape.DEFAULT) -> Image:

        if not word:
            word = [(' ', GlyphColor.CLEAR)]

        if isinstance(word, str):
            word = self.map_random_color(word)

        cols = len(word)

        margin = self.margin

        template = self.draw_word(
            word=word, shape=shape).image

        background = PILImage.new(
            mode='RGBA',
            size=(template.width + 2 * margin,
                  template.height + 2 * margin),
            color=(0, 0, 0, 0))
        empty_boxes = self.draw_word(
            word=[(' ', GlyphColor.INVERSE_LIGHT_GRAY)] * cols, shape=shape).image
        background.paste(empty_boxes, tuple(
            map(lambda x: x + margin, (0, 0, empty_boxes.width, empty_boxes.height))))

        frames = []
        frames.append(background.copy())

        glyph_width, glyph_height = self.draw_char(
            char=' ', shape=shape, color=GlyphColor.INVERSE_LIGHT_GRAY).size

        for idx in range(0, cols):
            x_off = (idx % cols) * (
                glyph_width + self.spacer_width)
            glyph = template.crop(
                (x_off, 0, x_off + glyph_width, glyph_height))

            next_img = frames[-1].copy()
            next_img.paste(glyph, (x_off + margin, margin))
            frames.append(next_img)

        return GIFImage(images=frames, duration=500)
