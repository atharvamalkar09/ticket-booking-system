import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import { DatePipe } from '@angular/common';

import { Router } from '@angular/router';

import {
  EventResponse,
  EventService
} from '../../../core/services/event/event';

import { Dialog } from '../../../shared/dialog/dialog';
import { DialogService } from '../../../core/services/dialog/dialog';

@Component({
  selector: 'app-admin-events',
  imports: [
    DatePipe,
    Dialog
  ],
  templateUrl: './admin-events.html',
  styleUrl: './admin-events.css',
})
export class AdminEvents implements OnInit {
  private eventService = inject(EventService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  dialogService = inject(DialogService);

  events: EventResponse[] = [];

  isLoading = false;
  errorMessage = '';

  ngOnInit(): void {
    this.loadEvents();
  }

  loadEvents(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.eventService
      .getEvents()
      .subscribe({
        next: (events: EventResponse[]) => {
          console.log(
            'ADMIN EVENTS:',
            events
          );

          this.events = events;
          this.isLoading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'FAILED TO LOAD ADMIN EVENTS:',
            err
          );

          this.events = [];
          this.isLoading = false;

          this.errorMessage =
            err.error?.detail ||
            err.error?.message ||
            'Failed to load events. Please try again.';

          this.cdr.detectChanges();
        }
      });
  }

  createEvent(): void {
    this.router.navigate([
      '/admin/events/create'
    ]);
  }

  viewEvent(eventId: number): void {
    this.router.navigate([
      '/admin/events',
      eventId
    ]);
  }

  editEvent(eventId: number): void {
    this.router.navigate([
      '/admin/events',
      eventId,
      'edit'
    ]);
  }

  async deleteEvent(
    eventId: number
  ): Promise<void> {
    const event = this.events.find(
      event => event.id === eventId
    );

    if (!event) {
      return;
    }

    const confirmed =
      await this.dialogService.confirm({
        title: 'Delete Event?',
        message:
          `Are you sure you want to delete "${event.title}"?`,
        type: 'confirm',
        confirmText: 'Delete',
        cancelText: 'Cancel',
        showCancel: true
      });

    this.cdr.detectChanges();

    if (!confirmed) {
      return;
    }

    console.log(
      'DELETING EVENT:',
      eventId
    );

    this.eventService
      .deleteEvent(eventId)
      .subscribe({
        next: async () => {
          console.log(
            'EVENT DELETED:',
            eventId
          );

          this.events =
            this.events.filter(
              event => event.id !== eventId
            );

          this.cdr.detectChanges();

          await this.dialogService.success(
            'Event deleted',
            `"${event.title}" was deleted successfully.`
          );

          this.cdr.detectChanges();
        },

        error: async (err) => {
          console.error(
            'FAILED TO DELETE EVENT:',
            err
          );

          const message =
            err.error?.error?.message ||
            err.error?.detail ||
            err.error?.message ||
            'Failed to delete event. Please try again.';

          this.cdr.detectChanges();

          await this.dialogService.error(
            'Delete failed',
            message
          );

          this.cdr.detectChanges();
        }
      });
  }
}