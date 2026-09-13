import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface SeatResponse {
  id: number;
  venue_id: number;
  row: string;
  number: number;
  category: 'STANDARD' | 'PREMIUM' | 'VIP';
  label: string;
}

@Injectable({
  providedIn: 'root',
})
export class SeatService {

  private readonly API_URL = 'http://localhost:8000/api/v1/seats';

  private readonly http = inject(HttpClient);

  getSeatsByVenue(venueId: number): Observable<SeatResponse[]> {
    return this.http.get<SeatResponse[]>(
      `${this.API_URL}/venue/${venueId}`
    );
  }
}