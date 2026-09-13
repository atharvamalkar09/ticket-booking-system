import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface VenueSummary {
  id: number;
  name: string;
  location: string;
  capacity?: number;
  description?: string;
}

export interface EventResponse {
  id: number;
  title: string;
  description?: string;
  category: string;
  start_time: string;
  end_time: string;
  base_price: number;
  venues: VenueSummary[];
}

export interface EventCreateRequest {
  title: string;
  description?: string;
  category: string;
  start_time: string;
  end_time: string;
  base_price: number;
  venue_ids: number[];
}

export interface EventUpdateRequest {
  title?: string;
  description?: string;
  category?: string;
  start_time?: string;
  end_time?: string;
  base_price?: number;
  venue_ids?: number[];
}

@Injectable({
  providedIn: 'root',
})
export class EventService {
  private readonly API_URL =
    'http://localhost:8000/api/v1/events';

  private readonly http = inject(HttpClient);

  getEvents(): Observable<EventResponse[]> {
    return this.http.get<EventResponse[]>(
      this.API_URL
    );
  }

  getEvent(
    eventId: number
  ): Observable<EventResponse> {
    return this.http.get<EventResponse>(
      `${this.API_URL}/${eventId}`
    );
  }

  createEvent(
    event: EventCreateRequest
  ): Observable<EventResponse> {
    return this.http.post<EventResponse>(
      this.API_URL,
      event
    );
  }

  updateEvent(
    eventId: number,
    event: EventUpdateRequest
  ): Observable<EventResponse> {
    return this.http.patch<EventResponse>(
      `${this.API_URL}/${eventId}`,
      event
    );
  }

  deleteEvent(
    eventId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.API_URL}/${eventId}`
    );
  }
}