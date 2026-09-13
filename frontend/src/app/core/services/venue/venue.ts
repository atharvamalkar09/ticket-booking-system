import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface VenueResponse {
  id: number;
  name: string;
  location: string;
  capacity: number;
  description?: string;
  created_at: string;
}

export interface VenueUpdateRequest {
  name?: string;
  location?: string;
  capacity?: number;
  description?: string;
}

export interface VenueCreateRequest {
  name: string;
  location: string;
  capacity: number;
  description?: string;
}

@Injectable({
  providedIn: 'root',
})
export class VenueService {
  private readonly API_URL =
    'http://localhost:8000/api/v1/venues';

  private readonly http = inject(HttpClient);

  getVenues(): Observable<VenueResponse[]> {
    return this.http.get<VenueResponse[]>(
      this.API_URL
    );
  }

  getVenue(
    venueId: number
  ): Observable<VenueResponse> {
    return this.http.get<VenueResponse>(
      `${this.API_URL}/${venueId}`
    );
  }

  createVenue(
    venue: VenueCreateRequest
  ): Observable<VenueResponse> {
    return this.http.post<VenueResponse>(
      this.API_URL,
      venue
    );
  }

  updateVenue(
    venueId: number,
    venue: VenueUpdateRequest
  ): Observable<VenueResponse> {
    return this.http.patch<VenueResponse>(
      `${this.API_URL}/${venueId}`,
      venue
    );
  }

  deleteVenue(
    venueId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.API_URL}/${venueId}`
    );
  }
}