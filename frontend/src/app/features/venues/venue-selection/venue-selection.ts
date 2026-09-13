import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';

import {
  ActivatedRoute,
  Router
} from '@angular/router';

import {
  EventService,
  EventResponse
} from '../../../core/services/event/event';
import { Navbar } from '../../../shared/navbar/navbar';

@Component({
  selector: 'app-venue-selection',
  imports:[Navbar],
  templateUrl: './venue-selection.html',
  styleUrl: './venue-selection.css'
})
export class VenueSelection implements OnInit {

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
      'VENUE SELECTION EVENT ID:',
      this.eventId
    );

    this.loadEvent();
  }


  loadEvent(): void {

    this.isLoading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();


    this.eventService
      .getEvent(this.eventId)
      .subscribe({

        next: (event: EventResponse) => {

          console.log(
            'EVENT RECEIVED:',
            event
          );

          console.log(
            'VENUES RECEIVED:',
            event.venues
          );

          this.event = event;

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
            'Failed to load venues. Please try again.';

          this.cdr.detectChanges();

        }

      });

  }


  selectVenue(venueId: number): void {

  this.router.navigate([
    '/events',
    this.eventId,
    'venue',
    venueId,
    'seats'
  ]);

  }

}