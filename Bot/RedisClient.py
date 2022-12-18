import aioredis.exceptions
from aioredis import Redis, lock
import functools

from .Lock import LockNotOwnedError, LockError


class RedisError(Exception):
    ...


class RedisConnectionError(RedisError):
    ...


def aioredis_error_wrapper(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except aioredis.exceptions.ConnectionError as e:
            raise RedisConnectionError(e)

        except aioredis.exceptions.LockNotOwnedError as e:
            raise LockNotOwnedError(e)

        except aioredis.exceptions.LockError as e:
            raise LockError(e)

    return wrapper


class RedisLock(lock.Lock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @aioredis_error_wrapper
    async def acquire(self, *args, **kwargs):
        return await super().acquire(*args, **kwargs)

    @aioredis_error_wrapper
    async def release(self, *args, **kwargs):
        return await super().release(*args, **kwargs)

    @aioredis_error_wrapper
    async def extend(self, *args, **kwargs):
        return await super().extend(*args, **kwargs)


class RedisClient(Redis):
    def path(self, *argv) -> str:
        return ':'.join(map(str, argv))

    @aioredis_error_wrapper
    async def execute_command(self, *args, **kwargs):
        return await super().execute_command(*args, **kwargs)

    def lock(self, *args, **kwargs) -> RedisLock:
        return super().lock(*args, lock_class=RedisLock, **kwargs)
