from contextlib import contextmanager
from multiprocessing import Lock
from typing import Optional

from Wordle.Game import Game
from Wordle.Lock import LockError
from Wordle.Store import StoreType


class InMemoryStore():
    def __init__(self):
        self.games: dict = {}
        self.store_type: StoreType = StoreType.EPHEMERAL

    @property
    def type_desc(self) -> str:
        return self.store_type.value

    @contextmanager
    def game_lock(self, channel_id: int) -> Lock:
        try:
            with self.games[channel_id]['lock']:
                yield
        except KeyError:
            raise LockError('Lock not found')

    @contextmanager
    def run_lock(self, key: str, blocking_timeout: float) -> Lock:
        ''' Yield a dummy lock '''
        yield Lock()

    def update_game(self, channel_id: int, game: Game) -> Game:
        self.games[channel_id] = game
        return game

    def add_game(self, channel_id: int, game: Game) -> Game:
        self.games[channel_id] = {
            'game': game,
            'lock': Lock()
        }

        return game

    def remove_game(self, channel_id: int) -> bool:
        try:
            self.games.pop(channel_id)
            return True
        except KeyError:
            return False

    def get_game(self, channel_id: int) -> Optional[Game]:
        try:
            return self.games[channel_id]['game']
        except KeyError:
            return None
