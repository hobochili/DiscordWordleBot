import hashlib
import os
import urllib.request

from dynaconf import Dynaconf

from discord.ext import commands

from Ping.Ping import Ping
from Wordle.Lock import LockError
from Wordle.Wordle import Wordle
from Wordle.Words import Words
from Wordle.RedisClient import RedisClient
from Wordle.Store import InMemoryStore, RedisStore

if __name__ == '__main__':
    # TODO: Extract all this setup to a separate function or class

    config = Dynaconf(
        load_dotenv=True,
        envvar_prefix='WORDLEBOT',
        settings_files=['config.yaml'])

    if config.get('token') is None:
        print(
            'Make sure you have a config.toml or .env file with your bot\'s discord token.')
        exit()

    if not os.path.exists(Words.DATABASE):
        print('Performing first time setup.')
        print('Creating database...')
        Words.create_db()
        print('Downloading wordlist...')
        urllib.request.urlretrieve(config.get('wordlist'), Words.WORDLIST)
        print('Seeding database...')
        Words.seed()
        print('Setup complete.')

    redis = RedisClient(
        config.get('redis.host'),
        config.get('redis.port', 6379))

    state_backend = RedisStore(redis) if redis.ping() else InMemoryStore()

    bot = commands.Bot(command_prefix='%')
    bot.add_cog(Wordle(bot, state_backend))
    bot.add_cog(Ping(bot))

    try:
        with state_backend.run_lock(
                hashlib.sha256(config.get('token').encode()).hexdigest(),
                blocking_timeout=2):

            print(f'Bot started with {state_backend.type_desc} state')
            bot.run(config.get('token'))

    except LockError as e:
        print(f'Failed to start bot: {e}')
