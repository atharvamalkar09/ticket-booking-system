import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';

import { DatePipe } from '@angular/common';
import { Router } from '@angular/router';

import { BookingService } from '../../../core/services/booking/booking';
import { PaymentService } from '../../../core/services/payment/payment';
import { Navbar } from '../../../shared/navbar/navbar';

import { BookingState } from '../booking-state/booking-state';

@Component({
  selector: 'app-booking',
  imports: [DatePipe, Navbar],
  templateUrl: './booking.html',
  styleUrl: './booking.css',
})
export class Booking implements OnInit {
  private readonly bookingService = inject(BookingService);
  private readonly bookingState = inject(BookingState);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly paymentService = inject(PaymentService);

  bookingId: number | null = null;

  event = this.bookingState.event;
  venue = this.bookingState.venue;
  selectedSeats = this.bookingState.selectedSeats;
  totalPrice = this.bookingState.totalPrice;

  isBooking = false;

  errorMessage = '';
  successMessage = '';

  showPaymentErrorDialog = false;
  showPaymentSuccessDialog = false;

  ngOnInit(): void {
    console.log('BOOKING EVENT:', this.event);
    console.log('BOOKING VENUE:', this.venue);
    console.log('BOOKING SEATS:', this.selectedSeats);
    console.log('BOOKING TOTAL:', this.totalPrice);

    if (
      !this.event ||
      !this.venue ||
      this.selectedSeats.length === 0
    ) {
      this.errorMessage =
        'Booking information is missing. Please select your seats again.';

      this.showPaymentErrorDialog = true;
      this.cdr.detectChanges();

      return;
    }
  }

  confirmBooking(): void {
    if (
      !this.event ||
      !this.venue ||
      this.selectedSeats.length === 0
    ) {
      this.errorMessage =
        'Booking information is missing. Please select your seats again.';

      this.showPaymentErrorDialog = true;
      this.cdr.detectChanges();

      return;
    }

    this.isBooking = true;
    this.errorMessage = '';
    this.successMessage = '';
    this.showPaymentErrorDialog = false;
    this.showPaymentSuccessDialog = false;

    const bookingRequest = {
      event_id: this.event.id,
      seat_ids: this.selectedSeats.map(
        seat => seat.id
      )
    };

    console.log(
      'BOOKING PAYLOAD:',
      bookingRequest
    );

    this.bookingService
      .createBooking(bookingRequest)
      .subscribe({
        next: (booking) => {
          console.log(
            'BOOKING CREATED:',
            booking
          );

          this.bookingId = booking.id;

          this.createPaymentOrder(booking.id);
        },

        error: (err) => {
          console.error(
            'Failed to create booking:',
            err
          );

          this.isBooking = false;

          this.handleError(
            err,
            'Failed to create booking. Please try again.'
          );
        }
      });
  }

  private createPaymentOrder(
    bookingId: number
  ): void {
    console.log(
      'Creating Razorpay order for booking:',
      bookingId
    );

    this.paymentService
      .createOrder(bookingId)
      .subscribe({
        next: (order) => {
          console.log(
            'RAZORPAY ORDER CREATED:',
            order
          );

          this.openRazorpayCheckout(order);
        },

        error: (err) => {
          console.error(
            'Failed to create Razorpay order:',
            err
          );

          this.isBooking = false;

          this.handleError(
            err,
            'Unable to start payment. Please try again.'
          );
        }
      });
  }

  private openRazorpayCheckout(
    order: any
  ): void {
    const options = {
      key: order.razorpay_key_id,
      amount: order.amount_in_paise,
      currency: order.currency,
      name: 'Ticket Booking System',
      description: `Booking #${this.bookingId}`,
      order_id: order.razorpay_order_id,

      handler: (response: any) => {
        console.log(
          'RAZORPAY PAYMENT SUCCESS:',
          response
        );

        this.verifyPayment(response);
      },

      prefill: {
        name: '',
        email: '',
        contact: ''
      },

      notes: {
        booking_id: String(this.bookingId)
      },

      theme: {
        color: '#3399cc'
      },

      modal: {
        ondismiss: () => {
          console.log(
            'Razorpay Checkout closed by user'
          );

          this.isBooking = false;

          this.errorMessage =
            'Payment was cancelled. Your booking is still pending.';

          this.showPaymentErrorDialog = true;
          this.cdr.detectChanges();
        }
      }
    };

    const razorpay = new Razorpay(options);

    razorpay.open();
  }

  private verifyPayment(
    response: any
  ): void {
    console.log(
      'Verifying payment with backend...'
    );

    const paymentData = {
      razorpay_payment_id:
        response.razorpay_payment_id,

      razorpay_order_id:
        response.razorpay_order_id,

      razorpay_signature:
        response.razorpay_signature
    };

    this.paymentService
      .verifyPayment(paymentData)
      .subscribe({
        next: (payment) => {
          console.log(
            'PAYMENT VERIFIED:',
            payment
          );

          this.isBooking = false;

          this.successMessage =
            'Payment successful! Your booking is confirmed.';

          this.showPaymentSuccessDialog = true;

          this.bookingState.clearBookingData();

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Payment verification failed:',
            err
          );

          this.isBooking = false;

          this.handleError(
            err,
            'Payment verification failed. Please contact support if money was deducted.'
          );
        }
      });
  }

  private handleError(
    err: any,
    fallbackMessage: string
  ): void {
    console.log(
      'PAYMENT ERROR BODY:',
      err?.error
    );

    const message =
      err?.error?.error?.message;

    if (typeof message === 'string') {
      this.errorMessage = message;
    } else if (Array.isArray(message)) {
      this.errorMessage = message
        .map((item: any) => {
          const field = item?.loc?.[1];
          const msg = item?.msg;

          if (field && msg) {
            return `${this.getFieldName(field)}: ${msg}`;
          }

          return msg ?? 'Invalid payment request.';
        })
        .join('\n');
    } else if (Array.isArray(err?.error?.detail)) {
      this.errorMessage = err.error.detail
        .map((item: any) => {
          const field = item?.loc?.[1];
          const msg = item?.msg;

          if (field && msg) {
            return `${this.getFieldName(field)}: ${msg}`;
          }

          return msg ?? 'Invalid payment request.';
        })
        .join('\n');
    } else if (typeof err?.error?.detail === 'string') {
      this.errorMessage = err.error.detail;
    } else if (typeof err?.message === 'string') {
      this.errorMessage = err.message;
    } else {
      this.errorMessage = fallbackMessage;
    }

    this.showPaymentErrorDialog = true;
    this.cdr.detectChanges();

    console.log(
      'SHOW PAYMENT ERROR DIALOG:',
      this.showPaymentErrorDialog
    );
  }

  private getFieldName(field: string): string {
    const fieldNames: Record<string, string> = {
      booking_id: 'Booking',
      razorpay_payment_id: 'Payment ID',
      razorpay_order_id: 'Order ID',
      razorpay_signature: 'Payment signature'
    };

    return fieldNames[field] ?? field;
  }

  closePaymentErrorDialog(): void {
    this.showPaymentErrorDialog = false;
    this.cdr.detectChanges();
  }

  closePaymentErrorDialogOnBackdrop(
    event: MouseEvent
  ): void {
    if (event.target === event.currentTarget) {
      this.closePaymentErrorDialog();
    }
  }

  closePaymentSuccessDialog(): void {
    this.showPaymentSuccessDialog = false;
    this.cdr.detectChanges();

    this.router.navigate([
      '/bookings'
    ]);
  }

  closePaymentSuccessDialogOnBackdrop(
    event: MouseEvent
  ): void {
    if (event.target === event.currentTarget) {
      this.closePaymentSuccessDialog();
    }
  }

  goBack(): void {
    if (!this.event || !this.venue) {
      this.router.navigate([
        '/events'
      ]);

      return;
    }

    this.router.navigate([
      '/events',
      this.event.id,
      'venue',
      this.venue.id,
      'seats'
    ]);
  }

  cancelBooking(): void {
    this.bookingState.clearBookingData();

    this.router.navigate([
      '/events'
    ]);
  }
}