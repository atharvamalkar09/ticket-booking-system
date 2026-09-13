import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { jwtDecode } from 'jwt-decode';

export interface RegisterRequest {
  username: string;
  email: string;
  phone_no: string;
  address?: string;
  city: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface TokenPayload {
  sub: string;
  role: 'USER' | 'ADMIN';
  exp: number;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private readonly API_URL = 'http://localhost:8000/api/v1/auth';
  private readonly TOKEN_KEY = 'access_token';
  private readonly http = inject(HttpClient);

  get_token(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  register(data: RegisterRequest): Observable<any> {
    return this.http.post(
      `${this.API_URL}/register`,
      data
    ).pipe(
      tap({
        next: (response) => {
          console.log('REGISTER SUCCESS:', response);
        },
        error: (error) => {
          console.log('REGISTER SERVICE ERROR:', error);
        }
      })
    );
  }

  login(data: LoginRequest): Observable<AuthResponse> {
    const body = new HttpParams()
      .set('username', data.email)
      .set('password', data.password);

    return this.http.post<AuthResponse>(
      `${this.API_URL}/login`,
      body.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    ).pipe(
      tap((res) => {
        localStorage.setItem(
          this.TOKEN_KEY,
          res.access_token
        );
      })
    );
  }

  logout(): Observable<any> {
    return this.http.post(
      `${this.API_URL}/logout`,
      {}
    ).pipe(
      tap(() => {
        localStorage.removeItem(this.TOKEN_KEY);
      })
    );
  }

  isAdmin(): boolean {
    const token = this.get_token();

    if (!token) {
      return false;
    }

    try {
      const payload = jwtDecode<TokenPayload>(token);

      return payload.role === 'ADMIN';
    } catch {
      return false;
    }
  }

  isLoggedIn(): boolean {
    return this.get_token() !== null;
  }

  clearToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
  }
}