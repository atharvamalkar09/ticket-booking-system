import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';

import {
  CurrencyPipe,
  DatePipe
} from '@angular/common';

import {
  ActivatedRoute,
  Router
} from '@angular/router';

import {
  EventResponse,
  EventService
} from '../../../core/services/event/event';

@Component({
  selector: 'app-admin-event-details',
  imports: [
    DatePipe,
    CurrencyPipe
  ],
  templateUrl: './admin-event-details.html',
  styleUrl: './admin-event-details.css',
})
export class AdminEventDetails implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private eventService = inject(EventService);
  private cdr = inject(ChangeDetectorRef);

  eventId!: number;

  event: EventResponse | null = null;

  isLoading = false;
  errorMessage = '';

  ngOnInit(): void {
    this.eventId = Number(
      this.route.snapshot.paramMap.get('eventId')
    );

    console.log(
      'ADMIN EVENT ID:',
      this.eventId
    );

    this.loadEvent();
  }

  loadEvent(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.eventService
      .getEvent(this.eventId)
      .subscribe({
        next: (event) => {
          console.log(
            'ADMIN EVENT DETAILS:',
            event
          );

          this.event = event;
          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'FAILED TO LOAD ADMIN EVENT:',
            err
          );

          this.event = null;
          this.isLoading = false;

          this.errorMessage =
            err.error?.detail ||
            err.error?.message ||
            'Failed to load event details. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  editEvent(): void {
    this.router.navigate([
      '/admin/events',
      this.eventId,
      'edit'
    ]);
  }

  goBack(): void {
    this.router.navigate([
      '/admin/events'
    ]);
  }
}