import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  ActivatedRoute,
  Router
} from '@angular/router';

import {
  EventResponse,
  EventService,
  EventUpdateRequest
} from '../../../core/services/event/event';

import {
  VenueResponse,
  VenueService
} from '../../../core/services/venue/venue';

@Component({
  selector: 'app-admin-event-edit',
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './admin-event-edit.html',
  styleUrl: './admin-event-edit.css',
})
export class AdminEventEdit implements OnInit {
  private fb = inject(FormBuilder);
  private eventService = inject(EventService);
  private venueService = inject(VenueService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  eventId!: number;
  event: EventResponse | null = null;
  venues: VenueResponse[] = [];
  selectedVenueIds: number[] = [];

  isLoading = false;
  isLoadingVenues = false;
  isSubmitting = false;

  errorMessage = '';

  eventForm = this.fb.group({
    title: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(150)
      ]
    ],

    description: [
      '',
      [
        Validators.maxLength(1000)
      ]
    ],

    category: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(50)
      ]
    ],

    start_time: [
      '',
      Validators.required
    ],

    end_time: [
      '',
      Validators.required
    ],

    base_price: [
      null as number | null,
      [
        Validators.required,
        Validators.min(0.01)
      ]
    ]
  });

  ngOnInit(): void {
    this.eventId = Number(
      this.route.snapshot.paramMap.get('eventId')
    );

    if (!this.eventId) {
      this.errorMessage = 'Invalid event ID.';
      return;
    }

    this.loadEvent();
    this.loadVenues();
  }

  loadEvent(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.eventService
      .getEvent(this.eventId)
      .subscribe({
        next: (event) => {
          console.log(
            'EVENT TO EDIT:',
            event
          );

          this.event = event;
          this.populateForm(event);
          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'FAILED TO LOAD EVENT:',
            err
          );

          this.event = null;
          this.isLoading = false;

          this.errorMessage =
            err.error?.detail ||
            err.error?.message ||
            'Failed to load event. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  loadVenues(): void {
    this.isLoadingVenues = true;

    this.venueService
      .getVenues()
      .subscribe({
        next: (venues) => {
          console.log(
            'VENUES FOR EVENT EDIT:',
            venues
          );

          this.venues = venues;
          this.isLoadingVenues = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'FAILED TO LOAD VENUES:',
            err
          );

          this.venues = [];
          this.isLoadingVenues = false;

          this.errorMessage =
            err.error?.detail ||
            err.error?.message ||
            'Failed to load venues. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  populateForm(event: EventResponse): void {
    this.eventForm.patchValue({
      title: event.title,
      description: event.description || '',
      category: event.category,
      start_time: this.toDateTimeLocal(
        event.start_time
      ),
      end_time: this.toDateTimeLocal(
        event.end_time
      ),
      base_price: event.base_price
    });

    this.selectedVenueIds = event.venues.map(
      venue => venue.id
    );
  }

  toDateTimeLocal(dateString: string): string {
    const date = new Date(dateString);

    const year = date.getFullYear();

    const month = String(
      date.getMonth() + 1
    ).padStart(2, '0');

    const day = String(
      date.getDate()
    ).padStart(2, '0');

    const hours = String(
      date.getHours()
    ).padStart(2, '0');

    const minutes = String(
      date.getMinutes()
    ).padStart(2, '0');

    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  toggleVenue(venueId: number): void {
    if (
      this.selectedVenueIds.includes(venueId)
    ) {
      this.selectedVenueIds =
        this.selectedVenueIds.filter(
          id => id !== venueId
        );
    } else {
      this.selectedVenueIds = [
        ...this.selectedVenueIds,
        venueId
      ];
    }
  }

  isVenueSelected(venueId: number): boolean {
    return this.selectedVenueIds.includes(
      venueId
    );
  }

  updateEvent(): void {
    this.errorMessage = '';

    if (this.eventForm.invalid) {
      this.eventForm.markAllAsTouched();
      return;
    }

    if (this.selectedVenueIds.length === 0) {
      this.errorMessage =
        'Please select at least one venue.';
      return;
    }

    const formValue =
      this.eventForm.getRawValue();

    const eventData: EventUpdateRequest = {
      title: formValue.title!.trim(),

      description:
        formValue.description?.trim() ||
        undefined,

      category:
        formValue.category!.trim(),

      start_time:
        new Date(
          formValue.start_time!
        ).toISOString(),

      end_time:
        new Date(
          formValue.end_time!
        ).toISOString(),

      base_price:
        Number(formValue.base_price),

      venue_ids:
        this.selectedVenueIds
    };

    console.log(
      'UPDATING EVENT:',
      eventData
    );

    this.isSubmitting = true;

    this.eventService
      .updateEvent(
        this.eventId,
        eventData
      )
      .subscribe({
        next: (updatedEvent) => {
          console.log(
            'EVENT UPDATED:',
            updatedEvent
          );

          this.isSubmitting = false;

          this.router.navigate([
            '/admin/events',
            this.eventId
          ]);
        },

        error: (err) => {
          console.error(
            'FAILED TO UPDATE EVENT:',
            err
          );

          this.isSubmitting = false;

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to update event. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  cancel(): void {
    this.router.navigate([
      '/admin/events',
      this.eventId
    ]);
  }
}