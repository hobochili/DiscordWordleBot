import pickle

from contextlib import contextmanager
from typing import Optional

from Wordle.Game import Game
from Wordle.Lock import Lock
from Wordle.RedisClient import RedisClient
from Wordle.Store import StoreType


class RedisStore():
    def __init__(self, client: RedisClient):
        self.client: RedisClient = client
        self.path_prefix: str = self.client.path('wordle', 'channel')
        self.store_type: StoreType = StoreType.PERSISTENT

    @property
    def type_desc(self) -> str:
        return self.store_type.value

    def _path(self, channel_id: int, key: str = None) -> str:
        tokens = [self.path_prefix, channel_id, key]
        return self.client.path(*filter(None, tokens))

    @contextmanager
    def game_lock(self, channel_id: int) -> Lock:
        with self.client.lock(
                self._path(channel_id, 'lock'),
                timeout=5,
                blocking_timeout=10):

            yield

    @contextmanager
    def run_lock(self, key: str, blocking_timeout: float) -> Lock:
        with self.client.lock(
                self._path(key, 'lock'),
                blocking_timeout=blocking_timeout):

            yield

    def get_game(self, channel_id: int) -> Optional[Game]:
        pickled_game = self.client.get(self._path(channel_id, 'state'))
        if not pickled_game:
            return None

        return pickle.loads(pickled_game)

    def update_game(self, channel_id: str, game: Game) -> Game:
        self.client.set(
            self._path(channel_id, 'state'),
            pickle.dumps(game))

        return game

    def add_game(self, channel_id: str, game: Game) -> Game:
        return self.update_game(channel_id, game)

    def remove_game(self, channel_id: int) -> bool:
        keys = self.client.keys(self._path(channel_id, '*'))
        return self.client.delete(*keys) == len(keys)
