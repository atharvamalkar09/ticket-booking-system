import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';

import {
  DatePipe
} from '@angular/common';

import {
  Router
} from '@angular/router';

import {
  BookingResponse,
  BookingService
} from '../../../core/services/booking/booking';
import { Navbar } from '../../../shared/navbar/navbar';

@Component({
  selector: 'app-my-bookings',
  imports: [DatePipe,Navbar],
  templateUrl: './my-bookings.html',
  styleUrl: './my-bookings.css',
})
export class MyBookings implements OnInit {

  private bookingService = inject(BookingService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  bookings: BookingResponse[] = [];

  isLoading = false;

  errorMessage = '';


  ngOnInit(): void {

    this.loadBookings();

  }


  loadBookings(): void {

    this.isLoading = true;

    this.errorMessage = '';


    this.bookingService.getMyBookings().subscribe({

      next: (res) => {

        console.log(
          'MY BOOKINGS:',
          res
        );

        this.bookings = res;

        this.isLoading = false;

        this.cdr.detectChanges();

      },


      error: (err) => {

        console.error(
          'Failed to load bookings:',
          err
        );

        this.errorMessage =
          err.error?.error?.message ||
          'Failed to load your bookings. Please try again.';

        this.isLoading = false;

        this.cdr.detectChanges();

      }

    });

  }


  viewBooking(bookingId: number): void {

    this.router.navigate([
      '/bookings',
      bookingId
    ]);

  }


  goToEvents(): void {

    this.router.navigate([
      '/events'
    ]);

  }


  getSeatLabels(booking: BookingResponse): string[] {

    return booking.booking_seats.map(
      bookingSeat =>
        `${bookingSeat.seat.row}${bookingSeat.seat.number}`
    );

  }


  getTicketCount(booking: BookingResponse): number {

    return booking.booking_seats.length;

  }

}