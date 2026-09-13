import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface PaymentOrderResponse {
  payment_id: number;
  razorpay_order_id: string;
  amount: number;
  amount_in_paise: number;
  currency: string;
  razorpay_key_id: string;
}

export interface PaymentVerifyRequest {
  razorpay_payment_id: string;
  razorpay_order_id: string;
  razorpay_signature: string;
}

export interface PaymentResponse {
  id: number;
  booking_id: number;
  razorpay_order_id: string;
  razorpay_payment_id: string | null;
  amount: number;
  currency: string;
  status: string;
}

@Injectable({
  providedIn: 'root',
})
export class PaymentService {
  private readonly http = inject(HttpClient);

  private readonly API_URL =
    'http://localhost:8000/api/v1/payments';

  createOrder(
    bookingId: number
  ): Observable<PaymentOrderResponse> {
    return this.http.post<PaymentOrderResponse>(
      `${this.API_URL}/create-order/${bookingId}`,
      {}
    );
  }

  verifyPayment(
    paymentData: PaymentVerifyRequest
  ): Observable<PaymentResponse> {
    return this.http.post<PaymentResponse>(
      `${this.API_URL}/verify`,
      paymentData
    );
  }
}