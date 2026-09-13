import { Component, ChangeDetectorRef, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';

import { Auth, LoginRequest } from '../../../../core/services/auth/auth';
import { Navbar } from '../../../../shared/navbar/navbar';

@Component({
  selector: 'app-login',
  imports: [FormsModule, Navbar],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  private readonly authService = inject(Auth);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);

  userData: LoginRequest = {
    email: '',
    password: '',
  };

  errorMessage = '';
  isLoading = false;
  showLoginDialog = false;

  onLogin(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.showLoginDialog = false;

    this.authService
      .login(this.userData)
      .pipe(
        finalize(() => {
          this.isLoading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: () => {
          console.log('Is Admin:', this.authService.isAdmin());

          if (this.authService.isAdmin()) {
            this.router.navigate(['/admin/dashboard']);
          } else {
            this.router.navigate(['/events']);
          }
        },

        error: (err) => {
          console.error('Login error:', err);
          console.log('Login error body:', err.error);
          console.log('Login error status:', err.status);

          if (typeof err.error === 'string') {
            this.errorMessage = err.error;
          } else if (err.error?.detail) {
            this.errorMessage = err.error.detail;
          } else if (err.error?.error?.message) {
            this.errorMessage = err.error.error.message;
          } else {
            this.errorMessage = 'Invalid email or password.';
          }

          this.showLoginDialog = true;
          this.cdr.detectChanges();

          console.log(
            'SHOW LOGIN DIALOG:',
            this.showLoginDialog
          );
        },
      });
  }

  closeLoginDialog(): void {
    this.showLoginDialog = false;
    this.cdr.detectChanges();
  }

  closeLoginDialogOnBackdrop(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.closeLoginDialog();
    }
  }
}