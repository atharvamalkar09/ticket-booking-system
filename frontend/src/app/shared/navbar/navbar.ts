import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { Auth } from '../../core/services/auth/auth';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
})
export class Navbar {

  private readonly authService = inject(Auth);
  private readonly router = inject(Router);

  isMenuOpen = false;
  showLogoutDialog = false;


  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }
  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  closeMenu(): void {
    this.isMenuOpen = false;
  }
  onLogout(): void {
    this.closeMenu();
    this.showLogoutDialog = true;
  }

  cancelLogout(): void {
    this.showLogoutDialog = false;
  }

  confirmLogout(): void {

    this.showLogoutDialog = false;

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

  closeLogoutDialogOnBackdrop(event: MouseEvent): void {

    if (event.target === event.currentTarget) {
      this.cancelLogout();
    }

  }

}

