from contextlib import asynccontextmanager

from discord import TextChannel

from Wordle.Canvas import Canvas
from Wordle.Game import Game
from Wordle.Lock import Lock
from Wordle.Store import Store


class GameManager:
    def __init__(self, backend: Store):
        self.store: Store = backend
        self.canvas: Canvas = Canvas()

    def create_game(self, word_length: int, mode: str) -> Game:
        return Game(word_length=word_length, mode=mode, canvas=self.canvas)

    @asynccontextmanager
    async def lock(self, channel: TextChannel) -> Lock:
        """ raises LockNotFoundError """
        async with self.store.lock(channel.guild.id, channel.id):
            yield

    async def add_game(self, channel: TextChannel, game: Game) -> Game:
        """ raises GameNotAddedError """
        return await self.store.add_game(channel.guild.id, channel.id, game)

    async def get_current_game(self, channel: TextChannel) -> Game:
        """ raises GameNotFoundError """
        game = await self.store.get_game(channel.guild.id, channel.id)
        if not hasattr(game, 'canvas') or game.canvas is None:
            game.canvas = self.canvas

        return game

    async def stop_current_game(self, channel: TextChannel) -> bool:
        return await self.store.remove_game(channel.guild.id, channel.id)

    async def update_game(self, channel: TextChannel, game: Game) -> Game:
        """ raises GameNotUpdatedError """
        return await self.store.update_game(channel.guild.id, channel.id, game)
