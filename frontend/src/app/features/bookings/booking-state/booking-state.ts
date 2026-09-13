import { Injectable } from '@angular/core';

import { EventResponse } from '../../../core/services/event/event';
import { VenueResponse } from '../../../core/services/venue/venue';
import { SeatResponse } from '../../../core/services/seat/seat';

@Injectable({
  providedIn: 'root',
})
export class BookingState {

  event: EventResponse | null = null;

  venue: VenueResponse | null = null;

  selectedSeats: SeatResponse[] = [];

  totalPrice = 0;


  setBookingData(
    event: EventResponse,
    venue: VenueResponse,
    selectedSeats: SeatResponse[]
  ): void {

    this.event = event;

    this.venue = venue;

    this.selectedSeats = selectedSeats;

    this.totalPrice =
      selectedSeats.length *
      Number(event.base_price);
  }


  clearBookingData(): void {

    this.event = null;

    this.venue = null;

    this.selectedSeats = [];

    this.totalPrice = 0;
  }

}