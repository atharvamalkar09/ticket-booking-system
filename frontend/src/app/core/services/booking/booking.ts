import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface BookingCreate {
  event_id: number;
  seat_ids: number[];
}

export interface VenueSummary {
  id: number;
  name: string;
  location: string;
}

export interface VenueResponse {
  id: number;
  name: string;
  location: string;
}

export interface BookingSeatResponse {
  id: number;
  seat_id: number;
  price: number;
  seat: {
    id: number;
    row: string;
    number: number;
    venue: VenueResponse;
  };
}

export interface UserSummary {
  username: string;
  email: string;
  phone_no: string;
}

export interface BookingResponse {
  id: number;
  user_id: number;
  user?: UserSummary;
  event_id: number;
  total_price: number;
  status: BookingStatus;
  created_at: string;
  event?: {
    id: number;
    title: string;
    description?: string;
    category: string;
    start_time: string;
    end_time: string;
    base_price: number | string;
    venues: VenueSummary[];
  };
  booking_seats: BookingSeatResponse[];
}

export type BookingStatus =
  | 'PENDING'
  | 'CONFIRMED'
  | 'CANCELLED';

export interface BookingStatusUpdate {
  status: BookingStatus;
}

@Injectable({
  providedIn: 'root',
})
export class BookingService {
  private readonly API_URL =
    'http://localhost:8000/api/v1/bookings';

  private readonly http = inject(HttpClient);

  createBooking(
    booking: BookingCreate
  ): Observable<BookingResponse> {
    return this.http.post<BookingResponse>(
      this.API_URL,
      booking
    );
  }

  getMyBookings(): Observable<BookingResponse[]> {
    return this.http.get<BookingResponse[]>(
      `${this.API_URL}/me`
    );
  }

  getAllBookings(
    status?: BookingStatus
  ): Observable<BookingResponse[]> {
    let url = `${this.API_URL}/admin`;

    if (status) {
      url += `?status=${status}`;
    }

    return this.http.get<BookingResponse[]>(url);
  }

  updateBookingStatus(
    bookingId: number,
    status: BookingStatus
  ): Observable<BookingResponse> {
    const bookingStatus: BookingStatusUpdate = {
      status,
    };

    return this.http.patch<BookingResponse>(
      `${this.API_URL}/admin/${bookingId}/status`,
      bookingStatus
    );
  }

  getBooking(
    bookingId: number
  ): Observable<BookingResponse> {
    return this.http.get<BookingResponse>(
      `${this.API_URL}/${bookingId}`
    );
  }

  cancelBooking(
    bookingId: number
  ): Observable<BookingResponse> {
    return this.http.patch<BookingResponse>(
      `${this.API_URL}/${bookingId}/cancel`,
      {}
    );
  }

  getBookedSeats(
    eventId: number,
    venueId: number
  ): Observable<number[]> {
    return this.http.get<number[]>(
      `${this.API_URL}/event/${eventId}/venue/${venueId}/booked-seats`
    );
  }
}