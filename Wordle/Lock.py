from typing import Protocol


class Lock(Protocol):
    def acquire(self):
        ...

    def release(self):
        ...


class LockError(Exception):
    ...
