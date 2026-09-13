import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';

import {
  CommonModule
} from '@angular/common';

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
  VenueService,
  VenueResponse,
  VenueUpdateRequest
} from '../../../core/services/venue/venue';

@Component({
  selector: 'app-admin-venue-edit',
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './admin-venue-edit.html',
  styleUrl: './admin-venue-edit.css',
})
export class AdminVenueEdit implements OnInit {

  private fb = inject(FormBuilder);
  private venueService = inject(VenueService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  venueId!: number;

  venue: VenueResponse | null = null;

  isLoading = false;
  isSubmitting = false;

  errorMessage = '';

  venueForm = this.fb.group({
    name: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(100)
      ]
    ],

    location: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(255)
      ]
    ],

    capacity: [
      null as number | null,
      [
        Validators.required,
        Validators.min(1)
      ]
    ],

    description: [
      '',
      [
        Validators.maxLength(500)
      ]
    ]
  });

  ngOnInit(): void {
    this.venueId = Number(
      this.route.snapshot.paramMap.get('venueId')
    );

    console.log(
      'ADMIN VENUE EDIT ID:',
      this.venueId
    );

    if (!this.venueId) {
      this.errorMessage = 'Invalid venue ID.';
      return;
    }

    this.loadVenue();
  }

  loadVenue(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.venueService
      .getVenue(this.venueId)
      .subscribe({
        next: (venue) => {
          console.log(
            'VENUE TO EDIT:',
            venue
          );

          this.venue = venue;

          this.populateForm(venue);

          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'FAILED TO LOAD VENUE:',
            err
          );

          this.venue = null;
          this.isLoading = false;

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to load venue. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  populateForm(venue: VenueResponse): void {
    this.venueForm.patchValue({
      name: venue.name,
      location: venue.location,
      capacity: venue.capacity,
      description: venue.description || ''
    });
  }

  updateVenue(): void {
    this.errorMessage = '';

    if (this.venueForm.invalid) {
      this.venueForm.markAllAsTouched();
      return;
    }

    const formValue = this.venueForm.getRawValue();

    const venueData: VenueUpdateRequest = {
      name: formValue.name!.trim(),
      location: formValue.location!.trim(),
      capacity: Number(formValue.capacity),
      description: formValue.description?.trim() || undefined
    };

    console.log(
      'UPDATING VENUE:',
      venueData
    );

    this.isSubmitting = true;

    this.venueService
      .updateVenue(
        this.venueId,
        venueData
      )
      .subscribe({
        next: (updatedVenue) => {
          console.log(
            'VENUE UPDATED:',
            updatedVenue
          );

          this.isSubmitting = false;

          this.router.navigate([
            '/admin/venues',
            this.venueId
          ]);
        },

        error: (err) => {
          console.error(
            'FAILED TO UPDATE VENUE:',
            err
          );

          this.isSubmitting = false;

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to update venue. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  cancel(): void {
    this.router.navigate([
      '/admin/venues',
      this.venueId
    ]);
  }
}