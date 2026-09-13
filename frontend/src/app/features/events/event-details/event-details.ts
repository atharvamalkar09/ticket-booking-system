import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';

import { EventResponse, EventService } from '../../../core/services/event/event';
import { Navbar } from '../../../shared/navbar/navbar';


@Component({
  selector: 'app-event-details',
  imports: [DatePipe,Navbar],
  templateUrl: './event-details.html',
  styleUrl: './event-details.css',
})
export class EventDetails implements OnInit {

  private eventService = inject(EventService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);


  event: EventResponse | null = null;

  isLoading = false;
  errorMessage = '';


  ngOnInit(): void {

    const eventId = Number(
      this.route.snapshot.paramMap.get('eventId')
    );

    if (!eventId) {

      this.errorMessage = 'Invalid event.';

      this.cdr.detectChanges();

      return;
    }

    this.loadEvent(eventId);
  }


  loadEvent(eventId: number): void {

    this.isLoading = true;
    this.errorMessage = '';

    this.eventService.getEvent(eventId).subscribe({

      next: (res) => {

        console.log('EVENT DETAILS:', res);

        this.event = res;

        this.isLoading = false;

        this.cdr.detectChanges();
      },

      error: (err) => {

        console.error('Failed to load event:', err);

        this.errorMessage =
          err.error?.error?.message ||
          'Failed to load event. Please try again.';

        this.isLoading = false;

        this.cdr.detectChanges();
      }

    });
  }


  selectVenues(): void {

    if (!this.event) {
      return;
    }

    console.log('Navigating to venue selection');
    console.log('Event ID:', this.event.id);

    this.router.navigate([
      '/events',
      this.event.id,
      'venue'
    ]);
  }


  goBack(): void {

    this.router.navigate(['/events']);

  }

}