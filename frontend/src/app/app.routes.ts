import { Routes } from '@angular/router';

import { Register } from './features/auth/register/register/register';
import { Login } from './features/auth/login/login/login';
import { SeatSelection } from './features/seats/seat-selection/seat-selection';

import { authGuard } from './core/guards/auth/auth-guard';
import { adminGuard } from './core/guards/admin/admin-guard';
import { AdminDashboard } from './features/admin/admin-dashboard/admin-dashboard';
import { Event } from './features/events/event-list/events';
import { EventDetails } from './features/events/event-details/event-details';
import { VenueSelection } from './features/venues/venue-selection/venue-selection';
import { Booking } from './features/bookings/booking/booking';
import { MyBookings } from './features/bookings/my-bookings/my-bookings';
import { AdminEvents } from './features/admin/admin-events/admin-events';
import { AdminCreateEvent } from './features/admin/admin-create-event/admin-create-event';
import { AdminEventDetails } from './features/admin/admin-event-details/admin-event-details';
import { AdminEventEdit } from './features/admin/admin-event-edit/admin-event-edit';
import { AdminVenues } from './features/admin/admin-venues/admin-venues';
import { AdminVenueCreate } from './features/admin/admin-venue-create/admin-venue-create';
import { AdminVenueDetails } from './features/admin/admin-venue-details/admin-venue-details';
import { AdminVenueEdit } from './features/admin/admin-venue-edit/admin-venue-edit';
import { AdminBookings } from './features/admin/bookings/admin-bookings/admin-bookings';
import { AdminUsers } from './features/admin/users/user/user';
import { Profile } from './features/profile/profile';
import { Landing } from './features/landing/landing';


export const routes: Routes = [

  {
    path: 'register',
    component: Register
  },

  {
    path: 'login',
    component: Login
  },

  {
    path: 'events',
    // canActivate: [authGuard],
    component: Event
  },

  {
    path: 'events/:eventId',
    // canActivate: [authGuard],
    component: EventDetails
  },
  // {
  //   path: 'events/:eventId/venue/:venueId',
  //   canActivate: [authGuard],
  //   // component: SeatSelection
  //   component:VenueSelection
  // },
  {
  path: 'events/:eventId/venue',
  // canActivate: [authGuard],
  component: VenueSelection
  },
  {
    path: 'events/:eventId/venue/:venueId/seats',
    // canActivate: [authGuard],
    component: SeatSelection
  },
  // {
  // path: ':eventId/venue/:venueId/booking',
  // component: Booking
  // },

  {
  path: 'events/:eventId/venue/:venueId/booking',
  canActivate: [authGuard],
  component: Booking
  },
  {
  path: 'bookings',
  canActivate: [authGuard],
  component: MyBookings
  },
  {
  path: 'profile',
  canActivate: [authGuard],
  component: Profile
  },

  {
    path: 'admin',
    canActivate: [adminGuard],
    children: [
      {
        path: 'dashboard',
        component: AdminDashboard
      },
      { path: 'events', component: AdminEvents },
      { path: 'events/create', component: AdminCreateEvent },
      { path: 'events/:eventId/edit', component: AdminEventEdit },
      { path: 'events/:eventId', component: AdminEventDetails },
      { path: 'venues', component: AdminVenues },
      { path: 'venues/create', component: AdminVenueCreate },
      { path: 'venues/:venueId/edit',component: AdminVenueEdit},
      { path: 'venues/:venueId', component: AdminVenueDetails },
      { path: 'bookings', component: AdminBookings},
      { path: 'users', component: AdminUsers }
    ]
  },

  // {
  //   path: '',
  //   redirectTo: '/events',
  //   pathMatch: 'full'
  // },

  {
  path: '',
  component: Landing
  },

  // {
  //   path: '**',
  //   redirectTo: '/events'
  // }

  {
  path: '**',
  redirectTo: '/'
  }
];