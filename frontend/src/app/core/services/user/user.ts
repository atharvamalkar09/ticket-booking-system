import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  phone_no: string;
  address?: string;
  city: string;
  role: 'USER' | 'ADMIN';
  is_active: boolean;
  created_at: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  phone_no?: string;
  address?: string;
  city?: string;
  password?: string;
}

export interface UserStatusUpdate {
  is_active: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private readonly API_URL =
    'http://localhost:8000/api/v1/users';

  private readonly http = inject(HttpClient);

  getAllUsers(): Observable<UserResponse[]> {
    return this.http.get<UserResponse[]>(
      this.API_URL
    );
  }

  getMyProfile(): Observable<UserResponse> {
    return this.http.get<UserResponse>(
      `${this.API_URL}/me`
    );
  }

  getUser(
    userId: number
  ): Observable<UserResponse> {
    return this.http.get<UserResponse>(
      `${this.API_URL}/${userId}`
    );
  }

  updateUserStatus(
    userId: number,
    isActive: boolean
  ): Observable<UserResponse> {
    const status: UserStatusUpdate = {
      is_active: isActive,
    };

    return this.http.patch<UserResponse>(
      `${this.API_URL}/${userId}/status`,
      status
    );
  }

  updateMyProfile(
    data: UserUpdate
  ): Observable<UserResponse> {
    return this.http.patch<UserResponse>(
      `${this.API_URL}/me`,
      data
    );
  }

  deleteMyAccount(
    userId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.API_URL}/${userId}`
    );
  }
}