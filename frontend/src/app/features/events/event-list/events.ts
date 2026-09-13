import { CommonModule, DatePipe } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { Auth } from '../../../core/services/auth/auth';
import {
  EventResponse,
  EventService
} from '../../../core/services/event/event';
import { Navbar } from '../../../shared/navbar/navbar';

@Component({
  selector: 'app-events',
  imports: [
    CommonModule,
    DatePipe,
    FormsModule,
    Navbar
  ],
  templateUrl: './events.html',
  styleUrl: './events.css',
})
export class Event implements OnInit {

  private authService = inject(Auth);
  private router = inject(Router);
  private eventService = inject(EventService);
  private cdr = inject(ChangeDetectorRef);

  events: EventResponse[] = [];
  filteredEvents: EventResponse[] = [];

  isLoading = false;
  errorMessage = '';

  searchTerm = '';
  selectedCategory = '';
  selectedDate = '';
  minPrice: number | null = null;
  maxPrice: number | null = null;
  sortBy = 'date';

  categories: string[] = [];

  ngOnInit(): void {
    this.load_events();
  }

  load_events(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.eventService.getEvents().subscribe({
      next: (res) => {
        this.events = res;

        this.categories = [
          ...new Set(
            res.map(event => event.category)
          )
        ].sort();

        this.applyFilters();

        this.isLoading = false;
        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error('Failed to load events:', err);

        this.errorMessage =
          err.error?.error?.message ||
          'Failed to load events. Please try again.';

        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  applyFilters(): void {
    const search = this.searchTerm.trim().toLowerCase();

    this.filteredEvents = this.events.filter(event => {
      const matchesSearch =
        !search ||
        event.title.toLowerCase().includes(search);

      const matchesCategory =
        !this.selectedCategory ||
        event.category === this.selectedCategory;

      const matchesDate =
        !this.selectedDate ||
        this.isSameDate(
          event.start_time,
          this.selectedDate
        );

      const matchesMinPrice =
        this.minPrice === null ||
        Number(event.base_price) >= this.minPrice;

      const matchesMaxPrice =
        this.maxPrice === null ||
        Number(event.base_price) <= this.maxPrice;

      return (
        matchesSearch &&
        matchesCategory &&
        matchesDate &&
        matchesMinPrice &&
        matchesMaxPrice
      );
    });

    this.sortEvents();
  }

  private isSameDate(
    eventDate: string,
    selectedDate: string
  ): boolean {
    const date = new Date(eventDate);

    const year = date.getFullYear();
    const month = String(
      date.getMonth() + 1
    ).padStart(2, '0');
    const day = String(
      date.getDate()
    ).padStart(2, '0');

    return `${year}-${month}-${day}` === selectedDate;
  }

  sortEvents(): void {
    switch (this.sortBy) {
      case 'date':
        this.filteredEvents.sort(
          (a, b) =>
            new Date(a.start_time).getTime() -
            new Date(b.start_time).getTime()
        );
        break;

      case 'price-low':
        this.filteredEvents.sort(
          (a, b) =>
            Number(a.base_price) -
            Number(b.base_price)
        );
        break;

      case 'price-high':
        this.filteredEvents.sort(
          (a, b) =>
            Number(b.base_price) -
            Number(a.base_price)
        );
        break;

      case 'name':
        this.filteredEvents.sort(
          (a, b) =>
            a.title.localeCompare(b.title)
        );
        break;
    }
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedCategory = '';
    this.selectedDate = '';
    this.minPrice = null;
    this.maxPrice = null;
    this.sortBy = 'date';

    this.applyFilters();
  }

  selectEvent(eventId: number): void {
    this.router.navigate([
      '/events',
      eventId
    ]);
  }
}