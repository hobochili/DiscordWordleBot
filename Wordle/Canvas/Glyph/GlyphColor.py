from enum import Enum
from itertools import chain

from PIL import ImageColor, ImagePalette

discord_dark = '#36393fff'
bg = discord_dark
# bg = '#86888aff'


class GlyphColor(Enum):
    GREEN = ('#6aaa64ff', '#6aaa64ff', bg)
    YELLOW = ('#c9b458ff', '#c9b458ff', bg)
    RED = ('#ff4646ff', '#ff4646ff', bg)

    CLEAR = ('#00000000', '#00000000', '#00000000')

    DARK_GRAY = ('#454545ff', '#454545ff', bg)
    INVERSE_DARK_GRAY = (bg, '#454545ff', '#454545ff')

    GRAY = ('#565758ff', '#565758ff', bg)
    INVERSE_GRAY = (bg, '#565758ff', '#565758ff')

    LIGHT_GRAY = ('#86888aff', '#86888aff', bg)
    INVERSE_LIGHT_GRAY = (bg, '#86888aff', '#86888aff')

    def __str__(self) -> str:
        return self.name


class xGlyphColor(Enum):
    GREEN = ('#6aaa64ff', '#6aaa64ff', '#ffffff00')
    YELLOW = ('#c9b458ff', '#c9b458ff', '#ffffff00')
    RED = ('#ff4646ff', '#ff4646ff', '#ffffff00')
    CLEAR = ('#00000000', '#00000000', '#00000000')

    DARK_GRAY = ('#454545ff', '#454545ff', '#ffffff00')
    INVERSE_DARK_GRAY = ('#ffffff00', '#454545ff', '#454545ff')

    GRAY = ('#565758ff', '#565758ff', '#ffffff00')
    INVERSE_GRAY = ('#ffffff00', '#565758ff', '#565758ff')

    LIGHT_GRAY = ('#86888aff', '#86888aff', '#ffffff00')
    INVERSE_LIGHT_GRAY = ('#ffffff00', '#86888aff', '#86888aff')

    def __str__(self) -> str:
        return self.name

    '''
    def palette(self) -> ImagePalette:
        colors = iter(self)
        rgbas = map(lambda x: ImageColor.getcolor(x[]))
        palette = map(lambda x: ImageColor.getcolor(x, mode='RGB'), sorted(set(chain(*[char[1].value for char in word])))))
        palette = list(chain(*palette))
    '''
