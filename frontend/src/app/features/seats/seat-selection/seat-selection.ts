import { DatePipe } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';
import {
  ActivatedRoute,
  Router
} from '@angular/router';

import {
  BookingService
} from '../../../core/services/booking/booking';
import {
  EventResponse,
  EventService
} from '../../../core/services/event/event';
import {
  SeatResponse,
  SeatService
} from '../../../core/services/seat/seat';
import {
  VenueResponse,
  VenueService
} from '../../../core/services/venue/venue';
import { Navbar } from '../../../shared/navbar/navbar';
import {
  BookingState
} from '../../bookings/booking-state/booking-state';

@Component({
  selector: 'app-seat-selection',
  imports: [
    DatePipe,
    Navbar
  ],
  templateUrl: './seat-selection.html',
  styleUrl: './seat-selection.css',
})
export class SeatSelection implements OnInit {

  private seatService = inject(SeatService);
  private eventService = inject(EventService);
  private venueService = inject(VenueService);
  private bookingService = inject(BookingService);
  private bookingState = inject(BookingState);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  eventId = 0;
  venueId = 0;

  event: EventResponse | null = null;
  venue: VenueResponse | null = null;

  seats: SeatResponse[] = [];
  selectedSeats: SeatResponse[] = [];
  bookedSeatIds: number[] = [];

  totalPrice = 0;

  isLoading = false;
  errorMessage = '';

  ngOnInit(): void {
    this.eventId = Number(
      this.route.snapshot.paramMap.get('eventId')
    );

    this.venueId = Number(
      this.route.snapshot.paramMap.get('venueId')
    );

    console.log('EVENT ID:', this.eventId);
    console.log('VENUE ID:', this.venueId);

    if (!this.eventId || !this.venueId) {
      this.errorMessage =
        'Invalid event or venue.';

      this.cdr.detectChanges();

      return;
    }

    this.loadEvent();
    this.loadVenue();
    this.loadSeats();
    this.loadBookedSeats();
  }

  loadEvent(): void {
    this.eventService
      .getEvent(this.eventId)
      .subscribe({
        next: (res) => {
          console.log('EVENT:', res);

          this.event = res;
          this.updateTotalPrice();

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Failed to load event:',
            err
          );

          this.errorMessage =
            err.error?.error?.message ||
            'Failed to load event. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  loadVenue(): void {
    this.venueService
      .getVenue(this.venueId)
      .subscribe({
        next: (res) => {
          console.log('VENUE:', res);

          this.venue = res;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Failed to load venue:',
            err
          );

          this.errorMessage =
            err.error?.error?.message ||
            'Failed to load venue. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  loadSeats(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.seatService
      .getSeatsByVenue(this.venueId)
      .subscribe({
        next: (res) => {
          console.log('SEATS:', res);

          this.seats = res;
          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Failed to load seats:',
            err
          );

          this.errorMessage =
            err.error?.error?.message ||
            'Failed to load seats. Please try again.';

          this.isLoading = false;

          this.cdr.detectChanges();
        }
      });
  }

  loadBookedSeats(): void {
    this.bookingService
      .getBookedSeats(
        this.eventId,
        this.venueId
      )
      .subscribe({
        next: (res) => {
          console.log(
            'BOOKED SEATS:',
            res
          );

          this.bookedSeatIds = res;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Failed to load booked seats:',
            err
          );

          this.errorMessage =
            err.error?.error?.message ||
            'Failed to load booked seats. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  isBooked(seat: SeatResponse): boolean {
    return this.bookedSeatIds.includes(
      seat.id
    );
  }

  toggleSeat(seat: SeatResponse): void {
    if (this.isBooked(seat)) {
      console.log(
        'Seat already booked:',
        seat.label
      );

      return;
    }

    const index =
      this.selectedSeats.findIndex(
        selectedSeat =>
          selectedSeat.id === seat.id
      );

    if (index >= 0) {
      this.selectedSeats.splice(
        index,
        1
      );
    } else {
      this.selectedSeats.push(seat);
    }

    this.updateTotalPrice();

    console.log(
      'SELECTED SEATS:',
      this.selectedSeats
    );

    console.log(
      'TOTAL PRICE:',
      this.totalPrice
    );

    this.cdr.detectChanges();
  }

  isSelected(
    seat: SeatResponse
  ): boolean {
    return this.selectedSeats.some(
      selectedSeat =>
        selectedSeat.id === seat.id
    );
  }

  updateTotalPrice(): void {
    if (!this.event) {
      this.totalPrice = 0;
      return;
    }

    const basePrice =
      Number(this.event.base_price);

    this.totalPrice =
      this.selectedSeats.length *
      basePrice;
  }

  getTotalPrice(): number {
    return this.totalPrice;
  }

  continueToBooking(): void {
    if (this.selectedSeats.length === 0) {
      this.errorMessage =
        'Please select at least one seat.';

      this.cdr.detectChanges();

      return;
    }

    if (!this.event) {
      this.errorMessage =
        'Event details are not available.';

      this.cdr.detectChanges();

      return;
    }

    if (!this.venue) {
      this.errorMessage =
        'Venue details are not available.';

      this.cdr.detectChanges();

      return;
    }

    console.log(
      'Continuing to booking...'
    );

    console.log(
      'Event:',
      this.event
    );

    console.log(
      'Venue:',
      this.venue
    );

    console.log(
      'Selected seats:',
      this.selectedSeats
    );

    console.log(
      'Total price:',
      this.totalPrice
    );

    this.bookingState.setBookingData(
      this.event,
      this.venue,
      [...this.selectedSeats]
    );

    this.router.navigate([
      '/events',
      this.eventId,
      'venue',
      this.venueId,
      'booking'
    ]);
  }

  goBack(): void {
    this.router.navigate([
      '/events',
      this.eventId
    ]);
  }
}