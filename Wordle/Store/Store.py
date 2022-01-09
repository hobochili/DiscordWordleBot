from contextlib import contextmanager
from enum import Enum
from typing import Optional, Protocol

from Wordle.Game import Game
from Wordle.Lock import Lock


class StoreType(Enum):
    EPHEMERAL = 'ephemeral'
    PERSISTENT = 'persistent'


class Store(Protocol):
    @property
    def type_desc(self) -> str:
        ...

    @contextmanager
    def game_lock(self, channel_id: int) -> Lock:
        ...

    @contextmanager
    def run_lock(self, key: str, blocking_timeout: float) -> Lock:
        ...

    def update_game(self, channel_id: int, game: Game) -> Game:
        ...

    def add_game(self, channel_id: int, game: Game) -> Game:
        ...

    def remove_game(self, channel_id: int) -> bool:
        ...

    def get_game(self) -> Optional[Game]:
        ...
