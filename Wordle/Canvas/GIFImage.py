import uuid

from io import BytesIO
from typing import List, Optional, Union

from discord import File

from PIL.Image import Image as PILImage


class GIFImage:
    def __init__(
            self,
            images: List[PILImage],
            duration: Union[int, List[int]] = 500,
            loop: Optional[int] = None,
            transparency: int = 0,
            dispose: int = 0,
            format: str = 'gif'):

        self.id: str = str(uuid.uuid4())
        self.images = images
        self.loop = loop
        self.duration = duration
        self.transparency = transparency
        self.dispose = dispose
        self.format = format

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

    def save(self, path: str) -> File:
        self.images[0].save(
            path,
            save_all=True,
            append_images=self.images[1:],
            optimize=False,
            duration=self.duration,
            format=self.format,
            dispose=self.dispose)

        return path

    def to_discord_file(self) -> File:
        arr = BytesIO()
        self.images[0].save(
            arr,
            save_all=True,
            append_images=self.images[1:],
            optimize=True,
            duration=self.duration,
            format=self.format,
            dispose=self.dispose)

        arr.seek(0)
        return File(arr, self.name)
