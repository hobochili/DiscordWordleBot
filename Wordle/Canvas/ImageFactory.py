import uuid

from io import BytesIO

from discord import File

from PIL import Image as PILImage


class ImageFactory:
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

    def with_margin(self) -> PILImage:
        width = self.image.width + 2 * self.margin
        height = self.image.height + 2 * self.margin
        res = PILImage.new('RGBA', (width, height))
        res.paste(self.image, (self.margin, self.margin))
        return res

    def to_discord_file(self) -> File:
        arr = BytesIO()
        self.with_margin().save(arr, format=self.format)
        arr.seek(0)
        return File(arr, self.name)
