import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  inject
} from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router } from '@angular/router';
import {
  VenueCreateRequest,
  VenueService
} from '../../../core/services/venue/venue';

@Component({
  selector: 'app-admin-venue-create',
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './admin-venue-create.html',
  styleUrl: './admin-venue-create.css',
})
export class AdminVenueCreate {

  private fb = inject(FormBuilder);
  private venueService = inject(VenueService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

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

  createVenue(): void {
    this.errorMessage = '';

    if (this.venueForm.invalid) {
      this.venueForm.markAllAsTouched();
      return;
    }

    const formValue = this.venueForm.getRawValue();

    const venueData: VenueCreateRequest = {
      name: formValue.name!.trim(),
      location: formValue.location!.trim(),
      capacity: Number(formValue.capacity),
      description: formValue.description?.trim() || undefined
    };

    console.log('CREATING VENUE:', venueData);

    this.isSubmitting = true;

    this.venueService
      .createVenue(venueData)
      .subscribe({
        next: (venue) => {
          console.log('VENUE CREATED:', venue);

          this.isSubmitting = false;

          this.router.navigate([
            '/admin/venues'
          ]);
        },
        error: (err) => {
          console.error(
            'FAILED TO CREATE VENUE:',
            err
          );

          this.isSubmitting = false;

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to create venue. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  cancel(): void {
    this.router.navigate([
      '/admin/venues'
    ]);
  }
}