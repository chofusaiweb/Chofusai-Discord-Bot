import os

from redis.asyncio.client import Redis


class UnarchiveClient:
    async def __aenter__(self) -> "UnarchiveClient":
        self._conn = Redis.from_url(os.environ["REDIS_URL"])
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._conn.close()

    async def add_unarchive_target(self, target: int) -> int:
        return await self._conn.sadd("unarchive_targets", str(target))

    async def remove_unarchive_target(self, target: int) -> int:
        return await self._conn.srem("unarchive_targets", str(target))

    async def get_unarchive_targets(self) -> tuple[int, ...]:
        result = await self._conn.smembers("unarchive_targets")
        return tuple(int(i) for i in result)

    async def is_unarchive_target(self, target: int) -> bool:
        return await self._conn.sismember("unarchive_targets", str(target))
