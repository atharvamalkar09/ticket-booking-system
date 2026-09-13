from typing import Optional
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentStatusEnum


class PaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        payment_id: int
    ) -> Optional[Payment]:

        stmt = (
            select(Payment)
            .where(
                Payment.id == payment_id
            )
        )

        return self.db.scalars(stmt).first()

    def get_by_booking_id(
        self,
        booking_id: int
    ) -> Optional[Payment]:

        stmt = (
            select(Payment)
            .where(
                Payment.booking_id == booking_id
            )
        )

        return self.db.scalars(stmt).first()

    def get_by_razorpay_order_id(
        self,
        razorpay_order_id: str
    ) -> Optional[Payment]:

        stmt = (
            select(Payment)
            .where(
                Payment.razorpay_order_id == razorpay_order_id
            )
        )

        return self.db.scalars(stmt).first()

    def get_by_razorpay_payment_id(
        self,
        razorpay_payment_id: str
    ) -> Optional[Payment]:

        stmt = (
            select(Payment)
            .where(
                Payment.razorpay_payment_id
                == razorpay_payment_id
            )
        )

        return self.db.scalars(stmt).first()

    def create_payment(
        self,
        booking_id: int,
        razorpay_order_id: str,
        amount:Decimal,
        currency: str = "INR"
    ) -> Payment:

        payment = Payment(
            booking_id=booking_id,
            razorpay_order_id=razorpay_order_id,
            amount=amount,
            currency=currency,
            status=PaymentStatusEnum.CREATED
        )

        self.db.add(payment)
        self.db.flush()

        return payment

    def mark_success(
        self,
        payment: Payment,
        razorpay_payment_id: str
    ) -> Payment:

        payment.razorpay_payment_id = razorpay_payment_id
        payment.status = PaymentStatusEnum.SUCCESS

        self.db.add(payment)
        self.db.flush()

        return payment

    def update_status(
        self,
        payment: Payment,
        status: PaymentStatusEnum
    ) -> Payment:

        payment.status = status

        self.db.add(payment)
        self.db.flush()

        return payment