import asyncio
import logging

from app.db.database import Sessionlocal
from app.services.bookingService import BookingService

logger = logging.getLogger(__name__)


async def booking_expiry_worker():
    while True:
        db = Sessionlocal()

        try:
            service = BookingService(db)

            expired_count = service.expire_pending_bookings()

            if expired_count > 0:
                logger.info(
                    "[Booking Expiry] Expired %d booking(s)",
                    expired_count
                )

        except Exception:
            logger.exception("[Booking Expiry] Worker error")

        finally:
            db.close()

        await asyncio.sleep(10)