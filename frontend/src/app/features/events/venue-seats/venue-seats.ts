import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import {
  VenueResponse,
  VenueService
} from '../../../core/services/venue/venue';

import {
  SeatResponse,
  SeatService
} from '../../../core/services/seat/seat';


@Component({
  selector: 'app-venue-seats',
  imports: [],
  templateUrl: './venue-seats.html',
  styleUrl: './venue-seats.css',
})
export class VenueSeats implements OnInit {

  private route = inject(ActivatedRoute);
  private router = inject(Router);

  private venueService = inject(VenueService);
  private seatService = inject(SeatService);

  private cdr = inject(ChangeDetectorRef);


  eventId: number = 0;
  venueId: number = 0;

  venue: VenueResponse | null = null;
  seats: SeatResponse[] = [];

  selectedSeats: SeatResponse[] = [];

  isLoading = false;
  errorMessage = '';


  ngOnInit(): void {

    this.eventId = Number(
      this.route.snapshot.paramMap.get('eventId')
    );

    this.venueId = Number(
      this.route.snapshot.paramMap.get('venueId')
    );


    if (!this.eventId || !this.venueId) {

      this.errorMessage = 'Invalid event or venue.';

      this.cdr.detectChanges();

      return;
    }


    this.loadVenue();
    this.loadSeats();
  }


  loadVenue(): void {

    this.venueService.getVenue(this.venueId).subscribe({

      next: (res) => {

        console.log('VENUE:', res);

        this.venue = res;

        this.cdr.detectChanges();
      },

      error: (err) => {

        console.error('Venue loading error:', err);

        this.errorMessage =
          err.error?.error?.message ||
          'Failed to load venue.';

        this.cdr.detectChanges();
      }

    });
  }


  loadSeats(): void {

    this.isLoading = true;
    this.errorMessage = '';

    this.seatService.getSeatsByVenue(this.venueId).subscribe({

      next: (res) => {

        console.log('SEATS:', res);

        this.seats = res;

        this.isLoading = false;

        this.cdr.detectChanges();
      },

      error: (err) => {

        console.error('Seat loading error:', err);

        this.errorMessage =
          err.error?.error?.message ||
          'Failed to load seats.';

        this.isLoading = false;

        this.cdr.detectChanges();
      }

    });
  }


  toggleSeat(seat: SeatResponse): void {

    const index = this.selectedSeats.findIndex(
      selected => selected.id === seat.id
    );


    if (index !== -1) {

      this.selectedSeats.splice(index, 1);

    } else {

      this.selectedSeats.push(seat);

    }

    this.cdr.detectChanges();
  }


  isSeatSelected(seat: SeatResponse): boolean {

    return this.selectedSeats.some(
      selected => selected.id === seat.id
    );

  }


  continueToBooking(): void {

    if (this.selectedSeats.length === 0) {

      this.errorMessage = 'Please select at least one seat.';

      this.cdr.detectChanges();

      return;
    }


    console.log(
      'Selected seats:',
      this.selectedSeats
    );


    // We will connect this to the booking page next.
    console.log(
      'Continue to booking for event:',
      this.eventId
    );
  }


  goBack(): void {

    this.router.navigate([
      '/events',
      this.eventId
    ]);

  }

}