import os
import urllib.request
import logging

from discord import Message, Intents, Client, Thread
from discord.ext import commands

from Config import Config
from Helpers.RandomText import RandomText

from ErrorHandler.ErrorHandler import ErrorHandler
from Ping.Ping import Ping
from Bot.RedisClient import RedisClient, RedisConnectionError
from Wordle.Store import InMemoryStore, RedisStore, Store
from Wordle.Wordle import Wordle
from Wordle.Words import Words


class Bot:
    config: Config
    logger: logging.Logger
    client: Client
    state_backend: Store

    def __init__(self, config: Config):
        self.config = config
        self.client = commands.Bot(command_prefix='%', intents=Intents(
            messages=True,
            message_content=True,
            guilds=True,
            dm_messages=True))

        logger = logging.getLogger('WordleBot')
        if config.verbose:
            logger = logging.getLogger()
        logger.setLevel(config.log_level)
        self.logger = logger

    async def _bootstrap(self):
        if os.path.exists(Words.DATABASE):
            return

        logger = self.logger

        logger.info('Performing first time setup.')

        logger.info('Creating database...')
        Words.create_db()

        logger.info('Downloading wordlist...')
        urllib.request.urlretrieve(self.config.wordlist, Words.WORDLIST)

        logger.info('Seeding database...')
        Words.seed()

        logger.info('Setup complete.')

    async def _configure_state_backend(self):
        self.state_backend = InMemoryStore()

        redis_config = self.config.redis
        if not redis_config.enable:
            return

        try:
            redis = RedisClient(
                host=redis_config.host,
                port=redis_config.port)

            await redis.ping()

        except RedisConnectionError as e:
            self.logger.error(f'Unable to connect to Redis backend: {e}')
            return

        self.logger.info(
            f'Connected to Redis server at {redis_config.host}:{redis_config.port}')

        self.state_backend = RedisStore(redis)

    async def _add_cogs(self):
        await self.client.add_cog(
            ErrorHandler(self.client, logger=self.logger))

        await self.client.add_cog(
            Wordle(
                self.client, config=self.config,
                state_backend=self.state_backend, logger=self.logger))

        await self.client.add_cog(
            Ping(self.client, logger=self.logger))

    async def _add_event_handlers(self):
        @self.client.event
        async def on_ready():
            self.logger.info(
                f'Bot ready with {self.state_backend.type_desc} state')

        @ self.client.event
        async def on_message(msg: Message):
            channel = msg.channel.parent if isinstance(
                msg.channel, Thread) else msg.channel

            if channel.id in self.config.deny_channels:
                return

            if self.config.allow_channels and channel.id not in self.config.allow_channels:
                return

            if self.client.user.mentioned_in(msg):
                return await msg.channel.send(RandomText.hal_9000(msg.author.mention))

            await self.client.process_commands(msg)

    async def setup(self):
        await self._bootstrap()
        await self._configure_state_backend()

    async def mount(self):
        await self._add_cogs()
        await self._add_event_handlers()
