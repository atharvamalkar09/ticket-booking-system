import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import { DatePipe} from '@angular/common';

import {
  BookingResponse,
  BookingService,
  BookingStatus
} from '../../../../core/services/booking/booking';

import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-admin-bookings',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule
  ],
  templateUrl: './admin-bookings.html',
  styleUrl: './admin-bookings.css'
})
export class AdminBookings implements OnInit {

  private bookingService = inject(BookingService);
  private cdr = inject(ChangeDetectorRef);

  bookings: BookingResponse[] = [];
  isLoading = false;
  errorMessage = '';

  selectedStatus: BookingStatus | 'ALL' = 'ALL';

  ngOnInit(): void {
    this.loadBookings();
  }

  loadBookings(): void {
    this.isLoading = true;
    this.errorMessage = '';

    const status =
      this.selectedStatus === 'ALL'
        ? undefined
        : this.selectedStatus;

    this.bookingService
      .getAllBookings(status)
      .subscribe({
        next: (response) => {
          this.bookings = response;
          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'FAILED TO LOAD ADMIN BOOKINGS:',
            error
          );

          this.errorMessage =
            'Failed to load bookings. Please try again.';

          this.isLoading = false;

          this.cdr.detectChanges();
        }
      });
  }

  filterBookings(): void {
    this.loadBookings();
  }

  selectedBooking: BookingResponse | null = null;

  viewBooking(booking: BookingResponse): void {
    this.selectedBooking = booking;

    console.log(
      'VIEW BOOKING:',
      booking
    );
  }

  changeStatus(
    booking: BookingResponse,
    newStatus: BookingStatus
  ): void {
    this.bookingService
      .updateBookingStatus(
        booking.id,
        newStatus
      )
      .subscribe({
        next: (updatedBooking) => {
          booking.status = updatedBooking.status;

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'FAILED TO UPDATE BOOKING STATUS:',
            error
          );

          this.loadBookings();
        }
      });
  }

  closeBookingDetails(): void {
    this.selectedBooking = null;
  }
}