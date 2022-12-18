import uuid
from io import BytesIO
from typing import Optional, Tuple
from discord import File

from PIL import Image as PILImage


class Image:
    def __init__(self, image: PILImage, margin: int = 10, format: str = 'png'):
        self.id: str = str(uuid.uuid4())
        self.image: PILImage = image
        self.margin: int = margin
        self.format: str = format

    def __str__(self):
        return '.'.join([self.id, self.format])

    @property
    def name(self) -> str:
        return '.'.join([self.id, self.format])

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    @property
    def size(self) -> Tuple[int, int]:
        return (self.image.width, self.image.height)

    def with_margin(self, margin: Optional[int] = None) -> PILImage:
        if not margin:
            margin = self.margin

        width = self.image.width + 2 * margin
        height = self.image.height + 2 * margin
        res = PILImage.new(self.image.mode, (width, height))
        res.paste(self.image, (margin, margin))

        return res

    def to_discord_file(self) -> File:
        arr = BytesIO()
        if self.format in ['gif', 'GIF']:
            self.image.save(arr, save_all=True,
                            optimize=False, format=self.format)
        else:
            self.with_margin().save(arr, format=self.format)

        arr.seek(0)
        return File(arr, self.name)
