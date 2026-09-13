import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';

import { Router } from '@angular/router';

import {
  VenueService,
  VenueResponse
} from '../../../core/services/venue/venue';

// NOTE: verify this import path against your actual project structure.
import { Dialog } from '../../../shared/dialog/dialog';
import { DialogService } from '../../../core/services/dialog/dialog';

@Component({
  selector: 'app-admin-venues',
  imports: [Dialog],
  templateUrl: './admin-venues.html',
  styleUrl: './admin-venues.css',
})
export class AdminVenues implements OnInit {

  private venueService = inject(VenueService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  readonly dialogService = inject(DialogService);

  venues: VenueResponse[] = [];

  isLoading = false;
  errorMessage = '';

  isDeleting = false;

  ngOnInit(): void {
    this.loadVenues();
  }

  loadVenues(): void {

    this.isLoading = true;
    this.errorMessage = '';

    this.venueService
      .getVenues()
      .subscribe({

        next: (venues: VenueResponse[]) => {

          console.log(
            'ADMIN VENUES:',
            venues
          );

          this.venues = venues;
          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {

          console.error(
            'FAILED TO LOAD ADMIN VENUES:',
            err
          );

          this.venues = [];
          this.isLoading = false;

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to load venues. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  createVenue(): void {

    this.router.navigate([
      '/admin/venues/create'
    ]);
  }

  viewVenue(venueId: number): void {

    this.router.navigate([
      '/admin/venues',
      venueId
    ]);
  }

  editVenue(venueId: number): void {

    this.router.navigate([
      '/admin/venues',
      venueId,
      'edit'
    ]);
  }

  async deleteVenue(venueId: number): Promise<void> {

    const venue = this.venues.find(
      venue => venue.id === venueId
    );

    if (!venue || this.isDeleting) {
      return;
    }

    const confirmed = await this.dialogService.confirm({
      title: 'Delete Venue?',
      message: `Are you sure you want to delete "${venue.name}"?`,
      confirmText: 'Delete',
      cancelText: 'Cancel'
    });

    if (!confirmed) {
      return;
    }

    console.log(
      'DELETING VENUE:',
      venue.id
    );

    this.isDeleting = true;
    this.cdr.detectChanges();

    this.venueService
      .deleteVenue(venue.id)
      .subscribe({

        next: () => {

          console.log(
            'VENUE DELETED:',
            venue.id
          );

          this.venues = this.venues.filter(
            item => item.id !== venue.id
          );

          this.isDeleting = false;
          this.cdr.detectChanges();

          this.dialogService.success(
            'Venue deleted',
            `"${venue.name}" was deleted successfully.`
          );
        },

        error: (err) => {

          console.error(
            'FAILED TO DELETE VENUE:',
            err
          );

          this.isDeleting = false;
          this.cdr.detectChanges();

          const message =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to delete venue. Please try again.';

          this.dialogService.error('Delete failed', message);
        }
      });
  }
}