import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import {
  Auth,
  RegisterRequest
} from '../../../../core/services/auth/auth';

import { Navbar } from '../../../../shared/navbar/navbar';

@Component({
  selector: 'app-register',
  imports: [FormsModule, Navbar],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class Register {
  private readonly authService = inject(Auth);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);

  userData: RegisterRequest = {
    username: '',
    email: '',
    phone_no: '',
    address: '',
    city: '',
    password: ''
  };

  errorMessage = '';
  isLoading = false;
  showRegisterDialog = false;

  onRegister(): void {
    this.errorMessage = '';
    this.showRegisterDialog = false;

    const validationError = this.validateForm();

    if (validationError) {
      this.errorMessage = validationError;
      this.showRegisterDialog = true;

      this.cdr.detectChanges();

      return;
    }

    this.isLoading = true;

    this.authService.register(this.userData).subscribe({
      next: () => {
        this.isLoading = false;

        this.cdr.detectChanges();

        this.router.navigate(['/login']);
      },

      error: (err) => {
        this.isLoading = false;

        console.log('STATUS:', err.status);
        console.log('ERROR BODY:', err.error);

        this.errorMessage = this.getRegistrationError(err);
        this.showRegisterDialog = true;

        this.cdr.detectChanges();

        console.log(
          'SHOW REGISTER DIALOG:',
          this.showRegisterDialog
        );
      }
    });
  }

  private validateForm(): string {
    const username = this.userData.username.trim();
    const email = this.userData.email.trim();
    const phone = this.userData.phone_no.trim();
    const city = this.userData.city.trim();
    const password = this.userData.password;

    if (!username) {
      return 'Username is required.';
    }

    if (username.length < 3) {
      return 'Username must be at least 3 characters.';
    }

    if (!email) {
      return 'Email is required.';
    }

    if (!this.isValidEmail(email)) {
      return 'Please enter a valid email address.';
    }

    if (!phone) {
      return 'Phone number is required.';
    }

    if (phone.length < 10) {
      return 'Phone number must be at least 10 characters.';
    }

    if (!/^[0-9+\-\s()]+$/.test(phone)) {
      return 'Please enter a valid phone number.';
    }

    if (!city) {
      return 'City is required.';
    }

    if (city.length < 2) {
      return 'City must be at least 2 characters.';
    }

    if (!password) {
      return 'Password is required.';
    }

    if (password.length < 8) {
      return 'Password must be at least 8 characters.';
    }

    return '';
  }

  private isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  private getRegistrationError(err: any): string {
    const message = err.error?.error?.message;

    if (Array.isArray(message)) {
      return message
        .map((item: any) => {
          const field = item?.loc?.[1];
          const backendMessage = item?.msg;

          if (field && backendMessage) {
            return `${this.getFieldName(field)}: ${backendMessage}`;
          }

          return backendMessage ?? 'Invalid input.';
        })
        .join('\n');
    }

    if (typeof message === 'string') {
      return message;
    }

    if (typeof err.error?.detail === 'string') {
      return err.error.detail;
    }

    return 'Registration failed. Please check your details and try again.';
  }

  private getFieldName(field: string): string {
    const fieldNames: Record<string, string> = {
      username: 'Username',
      email: 'Email',
      phone_no: 'Phone number',
      city: 'City',
      password: 'Password',
      address: 'Address'
    };

    return fieldNames[field] ?? field;
  }

  closeRegisterDialog(): void {
    this.showRegisterDialog = false;
    this.cdr.detectChanges();
  }

  closeRegisterDialogOnBackdrop(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.closeRegisterDialog();
    }
  }
}