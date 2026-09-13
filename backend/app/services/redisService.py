from app.core.redis import redis_client


class RedisService:

    @staticmethod
    def lock_seat(
        event_id: int,
        seat_id: int,
        booking_id: int,
        ttl_seconds: int = 300
    ) -> bool:

        key = f"seat_lock:{event_id}:{seat_id}"

        return bool(
            redis_client.set(
                key,
                booking_id,
                nx=True,
                ex=ttl_seconds
            )
        )

    @staticmethod
    def release_seat(
        event_id: int,
        seat_id: int,
        booking_id: int
    ) -> bool:

        key = f"seat_lock:{event_id}:{seat_id}"

        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

        result = redis_client.eval(
            lua_script,
            1,
            key,
            str(booking_id)
        )

        return bool(result)

    @staticmethod
    def is_seat_locked(
        event_id: int,
        seat_id: int
    ) -> bool:

        key = f"seat_lock:{event_id}:{seat_id}"

        return bool(
            redis_client.exists(key)
        )