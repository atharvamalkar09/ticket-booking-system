import redis

from app.services.redisService import RedisService
import app.services.redisService as redis_service_module


test_redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

redis_service_module.redis_client = test_redis_client


def test_lock_seat_success():

    event_id = 999
    seat_id = 999
    booking_id = 999

    RedisService.release_seat(
        event_id,
        seat_id,
        booking_id
    )

    result = RedisService.lock_seat(
        event_id=event_id,
        seat_id=seat_id,
        booking_id=booking_id,
        ttl_seconds=60
    )

    assert result is True

    assert RedisService.is_seat_locked(
        event_id,
        seat_id
    ) is True

    RedisService.release_seat(
        event_id,
        seat_id,
        booking_id
    )


def test_lock_same_seat_twice():

    event_id = 998
    seat_id = 998
    booking_id = 998

    RedisService.release_seat(
        event_id,
        seat_id,
        booking_id
    )

    first_lock = RedisService.lock_seat(
        event_id=event_id,
        seat_id=seat_id,
        booking_id=1,
        ttl_seconds=60
    )

    second_lock = RedisService.lock_seat(
        event_id=event_id,
        seat_id=seat_id,
        booking_id=2,
        ttl_seconds=60
    )

    assert first_lock is True
    assert second_lock is False

    RedisService.release_seat(
        event_id,
        seat_id,
        booking_id=1
    )


def test_release_seat_lock():

    event_id = 997
    seat_id = 997

    RedisService.lock_seat(
        event_id=event_id,
        seat_id=seat_id,
        booking_id=1,
        ttl_seconds=60
    )

    assert RedisService.is_seat_locked(
        event_id,
        seat_id
    ) is True

    released = RedisService.release_seat(
        event_id,
        seat_id,
        booking_id=1
    )

    assert released is True

    assert RedisService.is_seat_locked(
        event_id,
        seat_id
    ) is False


def test_seat_lock_expires():

    event_id = 996
    seat_id = 996

    RedisService.release_seat(
        event_id,
        seat_id,
        booking_id=1
    )

    RedisService.lock_seat(
        event_id=event_id,
        seat_id=seat_id,
        booking_id=1,
        ttl_seconds=1
    )

    assert RedisService.is_seat_locked(
        event_id,
        seat_id
    ) is True

    import time

    time.sleep(2)

    assert RedisService.is_seat_locked(
        event_id,
        seat_id
    ) is False