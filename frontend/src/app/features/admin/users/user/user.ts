import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  UserResponse,
  UserService
} from '../../../../core/services/user/user';

import { Auth } from '../../../../core/services/auth/auth';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule
  ],
  templateUrl: './user.html',
  styleUrl: './user.css'
})
export class AdminUsers implements OnInit {

  private readonly userService = inject(UserService);
  private readonly auth = inject(Auth);
  private readonly cdr = inject(ChangeDetectorRef);

  users: UserResponse[] = [];

  isLoading = false;

  errorMessage = '';
  successMessage = '';

  isUpdatingStatus = false;

  statusErrorMessage = '';
  statusSuccessMessage = '';

  statusUserId: number | null = null;

  showStatusConfirmation = false;

  userPendingStatusChange: UserResponse | null = null;

  pendingStatus = false;

  showErrorDialog = false;
  showSuccessDialog = false;

  searchTerm = '';

  selectedStatus: 'ALL' | 'ACTIVE' | 'INACTIVE' = 'ALL';

  selectedUser: UserResponse | null = null;

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;

    this.errorMessage = '';
    this.successMessage = '';

    this.showErrorDialog = false;
    this.showSuccessDialog = false;

    this.cdr.detectChanges();

    this.userService.getAllUsers().subscribe({
      next: (response) => {
        this.users = response;

        this.isLoading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {
        console.error(
          'FAILED TO LOAD ADMIN USERS:',
          error
        );

        this.isLoading = false;

        this.errorMessage =
          this.extractErrorMessage(
            error,
            'Failed to load users. Please try again.'
          );

        this.showErrorDialog = true;

        this.cdr.detectChanges();
      }
    });
  }

  get filteredUsers(): UserResponse[] {
    return this.users.filter(user => {
      const search = this.searchTerm
        .trim()
        .toLowerCase();

      const matchesSearch =
        !search ||
        user.username.toLowerCase().includes(search) ||
        user.email.toLowerCase().includes(search);

      const matchesStatus =
        this.selectedStatus === 'ALL' ||
        (
          this.selectedStatus === 'ACTIVE' &&
          user.is_active
        ) ||
        (
          this.selectedStatus === 'INACTIVE' &&
          !user.is_active
        );

      return matchesSearch && matchesStatus;
    });
  }

  viewUser(user: UserResponse): void {
    this.selectedUser = user;

    this.statusErrorMessage = '';
    this.statusSuccessMessage = '';

    console.log(
      'VIEW USER:',
      user
    );

    this.cdr.detectChanges();
  }

  isCurrentUser(user: UserResponse): boolean {
    const token = this.auth.get_token();

    if (!token) {
      return false;
    }

    try {
      const payload = JSON.parse(
        atob(
          token
            .split('.')[1]
            .replace(/-/g, '+')
            .replace(/_/g, '/')
        )
      );

      return Number(payload.sub) === user.id;
    } catch {
      return false;
    }
  }

  changeUserStatus(
    user: UserResponse
  ): void {
    if (
      user.is_active &&
      this.isCurrentUser(user)
    ) {
      this.statusErrorMessage =
        'You cannot deactivate your own admin account.';

      this.statusSuccessMessage = '';

      this.showErrorDialog = true;

      this.cdr.detectChanges();

      return;
    }

    if (this.isUpdatingStatus) {
      return;
    }

    this.userPendingStatusChange = user;

    this.pendingStatus = !user.is_active;

    this.statusErrorMessage = '';
    this.statusSuccessMessage = '';

    this.showStatusConfirmation = true;

    this.cdr.detectChanges();
  }

  confirmStatusChange(): void {
    if (
      !this.userPendingStatusChange ||
      this.isUpdatingStatus
    ) {
      return;
    }

    const user =
      this.userPendingStatusChange;

    const newStatus =
      this.pendingStatus;

    if (
      user.is_active &&
      !newStatus &&
      this.isCurrentUser(user)
    ) {
      this.cancelStatusChange();

      this.statusErrorMessage =
        'You cannot deactivate your own admin account.';

      this.showErrorDialog = true;

      this.cdr.detectChanges();

      return;
    }

    this.showStatusConfirmation = false;

    this.isUpdatingStatus = true;
    this.statusUserId = user.id;

    this.statusErrorMessage = '';
    this.statusSuccessMessage = '';

    this.cdr.detectChanges();

    this.userService
      .updateUserStatus(
        user.id,
        newStatus
      )
      .subscribe({
        next: (updatedUser) => {
          const index =
            this.users.findIndex(
              u => u.id === user.id
            );

          if (index !== -1) {
            this.users[index] = updatedUser;
          }

          if (
            this.selectedUser?.id === user.id
          ) {
            this.selectedUser =
              updatedUser;
          }

          this.isUpdatingStatus = false;
          this.statusUserId = null;

          this.statusSuccessMessage =
            `${updatedUser.username} has been ${
              updatedUser.is_active
                ? 'activated'
                : 'deactivated'
            } successfully.`;

          this.statusErrorMessage = '';

          this.showSuccessDialog = true;

          this.userPendingStatusChange = null;
          this.pendingStatus = false;

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'FAILED TO UPDATE USER STATUS:',
            error
          );

          this.isUpdatingStatus = false;
          this.statusUserId = null;

          this.statusErrorMessage =
            this.extractErrorMessage(
              error,
              'Failed to update user status. Please try again.'
            );

          this.statusSuccessMessage = '';

          this.showErrorDialog = true;

          this.cdr.detectChanges();
        }
      });
  }

  private extractErrorMessage(
    error: any,
    fallbackMessage: string
  ): string {
    const message =
      error?.error?.error?.message;

    if (typeof message === 'string') {
      return message;
    }

    if (Array.isArray(message)) {
      return message
        .map((item: any) => {
          const field = item?.loc?.[1];
          const msg = item?.msg;

          if (field && msg) {
            return `${this.getFieldName(field)}: ${msg}`;
          }

          return msg ?? 'Invalid request.';
        })
        .join('\n');
    }

    if (Array.isArray(error?.error?.detail)) {
      return error.error.detail
        .map((item: any) => {
          const field = item?.loc?.[1];
          const msg = item?.msg;

          if (field && msg) {
            return `${this.getFieldName(field)}: ${msg}`;
          }

          return msg ?? 'Invalid request.';
        })
        .join('\n');
    }

    if (typeof error?.error?.detail === 'string') {
      return error.error.detail;
    }

    if (typeof error?.message === 'string') {
      return error.message;
    }

    return fallbackMessage;
  }

  private getFieldName(field: string): string {
    const fieldNames: Record<string, string> = {
      username: 'Username',
      email: 'Email',
      phone_no: 'Phone number',
      city: 'City',
      address: 'Address',
      role: 'Role',
      is_active: 'Status'
    };

    return fieldNames[field] ?? field;
  }

  closeErrorDialog(): void {
    this.showErrorDialog = false;

    this.cdr.detectChanges();
  }

  closeErrorDialogOnBackdrop(
    event: MouseEvent
  ): void {
    if (event.target === event.currentTarget) {
      this.closeErrorDialog();
    }
  }

  closeSuccessDialog(): void {
    this.showSuccessDialog = false;

    this.cdr.detectChanges();
  }

  closeSuccessDialogOnBackdrop(
    event: MouseEvent
  ): void {
    if (event.target === event.currentTarget) {
      this.closeSuccessDialog();
    }
  }

  cancelStatusChange(): void {
    if (this.isUpdatingStatus) {
      return;
    }

    this.showStatusConfirmation = false;

    this.userPendingStatusChange = null;

    this.pendingStatus = false;

    this.cdr.detectChanges();
  }

  closeUserDetails(): void {
    if (this.isUpdatingStatus) {
      return;
    }

    this.selectedUser = null;

    this.statusErrorMessage = '';
    this.statusSuccessMessage = '';

    this.cdr.detectChanges();
  }
}