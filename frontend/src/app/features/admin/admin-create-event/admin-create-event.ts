import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit,
} from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import {
  EventCreateRequest,
  EventService,
} from '../../../core/services/event/event';
import {
  VenueResponse,
  VenueService,
} from '../../../core/services/venue/venue';

@Component({
  selector: 'app-admin-create-event',
  imports: [
    CommonModule,
    ReactiveFormsModule,
  ],
  templateUrl: './admin-create-event.html',
  styleUrl: './admin-create-event.css',
})
export class AdminCreateEvent implements OnInit {
  private fb = inject(FormBuilder);
  private eventService = inject(EventService);
  private venueService = inject(VenueService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  venues: VenueResponse[] = [];

  isLoadingVenues = false;
  isSubmitting = false;

  errorMessage = '';
  successMessage = '';

  eventForm = this.fb.group({
    title: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(150),
      ],
    ],
    description: [
      '',
      [
        Validators.maxLength(1000),
      ],
    ],
    category: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(50),
      ],
    ],
    start_time: [
      '',
      Validators.required,
    ],
    end_time: [
      '',
      Validators.required,
    ],
    base_price: [
      null as number | null,
      [
        Validators.required,
        Validators.min(0.01),
      ],
    ],
  });

  selectedVenueIds: number[] = [];

  ngOnInit(): void {
    this.loadVenues();
  }

  loadVenues(): void {
    this.isLoadingVenues = true;
    this.errorMessage = '';

    this.venueService.getVenues().subscribe({
      next: (venues) => {
        console.log(
          'ADMIN CREATE EVENT VENUES:',
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
      },
    });
  }

  toggleVenue(venueId: number): void {
    if (this.selectedVenueIds.includes(venueId)) {
      this.selectedVenueIds =
        this.selectedVenueIds.filter(
          id => id !== venueId
        );
    } else {
      this.selectedVenueIds = [
        ...this.selectedVenueIds,
        venueId,
      ];
    }
  }

  isVenueSelected(venueId: number): boolean {
    return this.selectedVenueIds.includes(venueId);
  }

  createEvent(): void {
    this.errorMessage = '';
    this.successMessage = '';

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

    const eventData: EventCreateRequest = {
      title: formValue.title!.trim(),
      description:
        formValue.description?.trim() || undefined,
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
        this.selectedVenueIds,
    };

    console.log(
      'CREATING EVENT:',
      eventData
    );

    this.isSubmitting = true;

    this.eventService
      .createEvent(eventData)
      .subscribe({
        next: (event) => {
          console.log(
            'EVENT CREATED:',
            event
          );

          this.isSubmitting = false;

          this.router.navigate([
            '/admin/events',
          ]);
        },
        error: (err) => {
          console.error(
            'FAILED TO CREATE EVENT:',
            err
          );

          this.isSubmitting = false;

          this.errorMessage =
            err.error?.detail ||
            err.error?.message ||
            'Failed to create event. Please try again.';

          this.cdr.detectChanges();
        },
      });
  }

  cancel(): void {
    this.router.navigate([
      '/admin/events',
    ]);
  }
}