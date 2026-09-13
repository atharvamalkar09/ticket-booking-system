from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentOrderResponse(BaseModel):

    payment_id: int
    razorpay_order_id: str
    amount: Decimal
    amount_in_paise: int
    currency: str
    razorpay_key_id: str

class PaymentVerifyRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    razorpay_order_id: str
    razorpay_payment_id: str | None
    amount: Decimal
    currency: str
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )