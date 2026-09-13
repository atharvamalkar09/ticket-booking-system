import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';

import { DatePipe } from '@angular/common';

import {
  ActivatedRoute,
  Router
} from '@angular/router';

import {
  VenueService,
  VenueResponse
} from '../../../core/services/venue/venue';

@Component({
  selector: 'app-admin-venue-details',
  imports: [
    DatePipe
  ],
  templateUrl: './admin-venue-details.html',
  styleUrl: './admin-venue-details.css',
})
export class AdminVenueDetails implements OnInit {

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private venueService = inject(VenueService);
  private cdr = inject(ChangeDetectorRef);

  venueId!: number;

  venue: VenueResponse | null = null;

  isLoading = false;
  errorMessage = '';

  ngOnInit(): void {
    this.venueId = Number(
      this.route.snapshot.paramMap.get('venueId')
    );

    console.log(
      'ADMIN VENUE ID:',
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
            'ADMIN VENUE DETAILS:',
            venue
          );

          this.venue = venue;
          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'FAILED TO LOAD ADMIN VENUE:',
            err
          );

          this.venue = null;
          this.isLoading = false;

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to load venue details. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  editVenue(): void {
    this.router.navigate([
      '/admin/venues',
      this.venueId,
      'edit'
    ]);
  }

  goBack(): void {
    this.router.navigate([
      '/admin/venues'
    ]);
  }
}