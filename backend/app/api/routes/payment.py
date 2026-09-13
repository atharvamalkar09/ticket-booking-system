from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db
from app.schemas.payment import (
    PaymentOrderResponse,
    PaymentResponse,
    PaymentVerifyRequest,
)
from app.services.paymentService import PaymentService


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.post(
    "/create-order/{booking_id}",
    response_model=PaymentOrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_payment_order(
    booking_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    payment_service = PaymentService(db)

    return payment_service.create_order(
        user_id=current_user.id,
        booking_id=booking_id
    )

@router.post(
    "/verify",
    response_model=PaymentResponse
)
def verify_payment(
    payment_data: PaymentVerifyRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    payment_service = PaymentService(db)

    return payment_service.verify_payment(
        payment_data=payment_data,
        user_id=current_user.id
    )

@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK
)
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_razorpay_signature: str = Header(
        ...,
        alias="X-Razorpay-Signature"
    )
):
    payment_service = PaymentService(db)

    return await payment_service.handle_webhook(
        request=request,
        signature=x_razorpay_signature
    )