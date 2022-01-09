from typing import Optional

from contextlib import contextmanager

from Wordle.Game import Game
from Wordle.Lock import Lock
from Wordle.Store import Store


class GameManager:
    def __init__(self, backend: Store):
        self.store: Store = backend

    @contextmanager
    def lock(self, channel_id: int) -> Lock:
        yield self.store.game_lock(channel_id)

    def add_game(self, channel_id: int, game: Game) -> Game:
        return self.store.add_game(channel_id, game)

    def get_current_game(self, channel_id: int) -> Optional[Game]:
        return self.store.get_game(channel_id)

    def stop_current_game(self, channel_id: int) -> bool:
        return self.store.remove_game(channel_id)

    def update_game(self, channel_id: int, game: Game) -> Game:
        return self.store.update_game(channel_id, game)
