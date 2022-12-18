import asyncio
import functools
import hashlib
import logging
import random
import signal
import sys

from Bot import (
    Bot, RedisConnectionError, Lock,
    LockNotOwnedError, LockError)

from Config import Config


def shutdown(sig: signal, event: asyncio.Event):
    logging.getLogger('Main').info(f'Received signal {sig.name}, exiting')
    event.set()


async def wait_for_lock(
        lock: Lock,
        locked: asyncio.Event,
        stopped: asyncio.Event):

    while True:
        if stopped.is_set():
            return

        await asyncio.sleep(1)
        try:
            if await lock.acquire():
                locked.set()
                return

        except RedisConnectionError as e:
            r = random.random()
            if r <= 0.2:
                logging.info(f'RedisConnectionError: {e}')

            await asyncio.sleep(r * 5)


async def extend_lock(
        lock: Lock,
        unlocked: asyncio.Event,
        stopped: asyncio.Event,
        new_ttl: float):

    freq: int = 2
    interval: float = new_ttl / freq

    while True:
        if stopped.is_set():
            unlocked.set()
            return

        r = 1.0
        try:
            await asyncio.wait_for(
                lock.extend(
                    additional_time=new_ttl, replace_ttl=True),
                timeout=1.0)

        except asyncio.TimeoutError:
            continue

        except RedisConnectionError as e:
            r = random.random()
            if r <= 0.2:
                logging.warning(f'RedisConnectionError: {e}')

        except LockNotOwnedError as e:
            logging.warning('Lock lost')
            unlocked.set()
            return

        except Exception as e:
            logging.warning(
                f'Failed to extend lock. {e.__class__.__name__}: {e}')
            unlocked.set()
            return

        await asyncio.sleep(interval * r)


async def run(config: Config, stopped: asyncio.Event):
    logger = logging.getLogger('main')

    bot = Bot(config)

    await bot.setup()
    await bot.mount()

    if not config.redis.enable:
        asyncio.create_task(
            bot.client.start(bot.config.token),
            name='bot')

        return await stopped.wait()

    # Run with lock

    lock_timeout = 10.0

    lock_key = hashlib.sha256(bot.config.token.encode()).hexdigest()
    lock = bot.state_backend.client.lock(
        f'wordlebot:lock:{lock_key}',
        timeout=lock_timeout,
        blocking_timeout=1)

    locked = asyncio.Event()
    unlocked = asyncio.Event()

    logger.info('Attempting to acquire lock...')

    while not stopped.is_set():
        await wait_for_lock(
            lock=lock,
            locked=locked,
            stopped=stopped)

        unlocked.clear()

        if not locked.is_set or stopped.is_set():
            continue

        logger.info('Lock acquired')

        tasks = [
            asyncio.create_task(
                extend_lock(
                    lock=lock,
                    unlocked=unlocked,
                    stopped=stopped,
                    new_ttl=lock_timeout),
                name='extend_lock'),
            asyncio.create_task(
                bot.client.start(bot.config.token),
                name='bot')
        ]

        await unlocked.wait()

        for task in tasks:
            logging.info(f'Canceling task: {task.get_name()}')
            task.cancel()

    await stopped.wait()

    try:
        await lock.release()

    except LockNotOwnedError as e:
        logging.debug(e)

    except LockError as e:
        logging.debug(e)

    except Exception as e:
        logging.error(e.__class__, e)


def main():
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname)-.4s [%(name)-16s] %(message)s',
        level=logging.ERROR)

    try:
        config = Config()
    except ValueError as e:
        logging.error(e)
        exit(1)

    logging.getLogger('Main').setLevel(config.log_level)

    loop = asyncio.new_event_loop()
    stopped = asyncio.Event()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(
            sig, functools.partial(shutdown, sig, stopped))

    loop.run_until_complete(run(config, stopped))


if __name__ == '__main__':
    main()
