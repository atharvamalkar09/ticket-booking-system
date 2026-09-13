import { DatePipe } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  inject,
  OnInit
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { Auth } from '../../core/services/auth/auth';
import {
  UserResponse,
  UserService,
  UserUpdate
} from '../../core/services/user/user';
import { Navbar } from '../../shared/navbar/navbar';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    Navbar
  ],
  templateUrl: './profile.html',
  styleUrl: './profile.css',
})
export class Profile implements OnInit {

  private readonly authService = inject(Auth);
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);

  user: UserResponse | null = null;

  isLoading = true;
  errorMessage = '';

  isEditing = false;
  isSaving = false;
  isDeleting = false;

  showDeleteConfirmation = false;

  editForm: UserUpdate = {};

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.userService.getMyProfile().subscribe({
      next: (user) => {
        this.user = user;
        this.isLoading = false;

        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error(
          'Failed to load profile:',
          err
        );

        this.errorMessage =
          err.error?.error?.message ||
          err.error?.detail ||
          'Failed to load your profile. Please try again.';

        this.isLoading = false;

        this.cdr.detectChanges();
      }
    });
  }

  goToEvents(): void {
    this.router.navigate(['/events']);
  }

  goToBookings(): void {
    this.router.navigate(['/bookings']);
  }

  goToAdmin(): void {
    this.router.navigate(['/admin/dashboard']);
  }

  onLogout(): void {
    this.authService.logout().subscribe({
      next: () => {
        this.router.navigate(['/']);
      },

      error: (err) => {
        console.error(
          'Logout error:',
          err
        );

        this.authService.clearToken();
        this.router.navigate(['/']);
      }
    });
  }

  startEditing(): void {
    if (!this.user) {
      return;
    }

    this.editForm = {
      username: this.user.username,
      email: this.user.email,
      phone_no: this.user.phone_no,
      address: this.user.address || '',
      city: this.user.city
    };

    this.isEditing = true;
  }

  cancelEditing(): void {
    this.isEditing = false;
    this.editForm = {};
  }

  saveProfile(): void {
    if (!this.user) {
      return;
    }

    this.isSaving = true;

    this.userService
      .updateMyProfile(this.editForm)
      .subscribe({
        next: (updatedUser) => {
          this.user = updatedUser;
          this.isEditing = false;
          this.isSaving = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Failed to update profile:',
            err
          );

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            'Failed to update your profile.';

          this.isSaving = false;

          this.cdr.detectChanges();
        }
      });
  }

  confirmDeleteAccount(): void {
    this.showDeleteConfirmation = true;
  }

  cancelDeleteAccount(): void {
    this.showDeleteConfirmation = false;
  }

  deleteAccount(): void {
    if (!this.user || this.isDeleting) {
      return;
    }

    this.isDeleting = true;

    this.userService
      .deleteMyAccount(this.user.id)
      .subscribe({
        next: () => {
          this.authService.clearToken();
          this.router.navigate(['/']);
        },

        error: (err) => {
          console.error(
            'Failed to delete account:',
            err
          );

          this.errorMessage =
            err.error?.error?.message ||
            err.error?.detail ||
            'Failed to delete your account.';

          this.isDeleting = false;
          this.showDeleteConfirmation = false;

          this.cdr.detectChanges();
        }
      });
  }
}