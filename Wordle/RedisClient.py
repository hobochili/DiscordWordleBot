from typing import Union
from datetime import timedelta
from contextlib import contextmanager

from redis import Redis, ConnectionError
from redis.exceptions import LockError as RedisLockError

from Wordle.Lock import Lock, LockError


class RedisClient:
    def __init__(self, host: str, port: int = 6379):
        self.conn = Redis(host=host, port=port)

    def ping(self) -> bool:
        try:
            return self.conn.ping()
        except ConnectionError:
            return False

    def path(self, *argv) -> str:
        return ':'.join(map(str, argv))

    def keys(self, pattern: Union[str, bytes]) -> list[Union[str, bytes]]:
        return self.conn.keys(pattern)

    @contextmanager
    def lock(self,
             name: str,
             timeout: Union[None, float] = None,
             sleep: float = 0.1,
             blocking_timeout: Union[None, float] = None,
             thread_local: bool = True) -> Lock:

        try:
            with self.conn.lock(
                    name,
                    timeout=timeout,
                    sleep=sleep,
                    blocking_timeout=blocking_timeout,
                    thread_local=thread_local):
                yield

        except RedisLockError as e:
            raise LockError(e)

    def get(self, key: str) -> Union[str, bytes]:
        return self.conn.get(key)

    def set(self,
            name: Union[str, bytes],
            value: Union[bytes, float, int, str],
            ex: Union[None, int, timedelta] = None,
            px: Union[None, int, timedelta] = None,
            nx: bool = False,
            xx: bool = False,
            keepttl: bool = False,
            get: bool = False,
            exat: Union[object, None] = None,
            pxat: Union[object, None] = None) -> Union[bool, None]:

        return self.conn.set(
            name=name,
            value=value,
            ex=ex,
            px=px,
            nx=nx,
            xx=xx,
            keepttl=keepttl,
            get=get,
            exat=exat,
            pxat=pxat)

    def delete(self, *names: Union[str, bytes]) -> int:
        return self.conn.delete(*names)
