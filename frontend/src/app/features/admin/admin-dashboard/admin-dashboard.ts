import {
  Component,
  ChangeDetectorRef,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { Auth } from '../../../core/services/auth/auth';
import { Router } from '@angular/router';
import { AdminDashboardService } from '../../../core/services/admin/admin-dashboard';
import { Navbar } from '../../../shared/navbar/navbar';

export interface RecentBooking {
  id: number;
  user_id: number;
  username: string;
  event_id: number;
  event_title: string;
  total_price: number;
  status:
    | 'PENDING'
    | 'CONFIRMED'
    | 'CANCELLED';
  created_at: string;
}

export interface AdminDashboardResponse {
  total_users: number;
  active_users: number;
  inactive_users: number;
  total_events: number;
  total_venues: number;
  total_bookings: number;
  confirmed_bookings: number;
  pending_bookings: number;
  cancelled_bookings: number;
  recent_bookings: RecentBooking[];
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    Navbar
  ],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.css',
})
export class AdminDashboard implements OnInit {
  private authService = inject(Auth);
  private router = inject(Router);
  private dashboardService = inject(AdminDashboardService);
  private cdr = inject(ChangeDetectorRef);

  dashboardData: AdminDashboardResponse | null = null;

  isLoading = true;
  errorMessage = '';
  isLoggingOut = false;

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    console.log('ADMIN DASHBOARD: Loading dashboard...');

    this.isLoading = true;
    this.errorMessage = '';
    this.dashboardData = null;

    this.dashboardService
      .getDashboard()
      .subscribe({
        next: (response) => {
          console.log(
            'ADMIN DASHBOARD RESPONSE:',
            response
          );

          this.dashboardData = response;
          this.isLoading = false;

          this.cdr.detectChanges();

          console.log(
            'ADMIN DASHBOARD: Loading complete'
          );
        },

        error: (error) => {
          console.error(
            'ADMIN DASHBOARD ERROR:',
            error
          );

          this.isLoading = false;

          this.errorMessage =
            error?.error?.detail ||
            error?.message ||
            'Unable to load dashboard data.';

          this.cdr.detectChanges();
        },

        complete: () => {
          console.log(
            'ADMIN DASHBOARD REQUEST COMPLETE'
          );
        }
      });
  }

  refreshDashboard(): void {
    this.loadDashboard();
  }

  goToEvents(): void {
    this.router.navigate([
      '/admin/events'
    ]);
  }

  goToVenues(): void {
    this.router.navigate([
      '/admin/venues'
    ]);
  }

  goToUsers(): void {
    this.router.navigate([
      '/admin/users'
    ]);
  }

  goToBookings(): void {
    this.router.navigate([
      '/admin/bookings'
    ]);
  }

  onLogout(): void {
    if (this.isLoggingOut) {
      return;
    }

    this.isLoggingOut = true;

    this.authService
      .logout()
      .subscribe({
        next: () => {
          this.router.navigate([
            '/login'
          ]);
        },

        error: (error) => {
          console.error(
            'Logout error:',
            error
          );

          this.authService.clearToken();

          this.router.navigate([
            '/login'
          ]);
        }
      });
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }
    );
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'CONFIRMED':
        return 'status-confirmed';

      case 'PENDING':
        return 'status-pending';

      case 'CANCELLED':
        return 'status-cancelled';

      default:
        return '';
    }
  }
}