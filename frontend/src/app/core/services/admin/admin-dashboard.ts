import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AdminDashboardResponse } from '../../../features/admin/admin-dashboard/admin-dashboard';

@Injectable({
  providedIn: 'root'
})
export class AdminDashboardService {
  private readonly API_URL = 'http://localhost:8000/api/v1/admin/dashboard';
  private readonly http = inject(HttpClient);

  getDashboard(): Observable<AdminDashboardResponse> {
    return this.http.get<AdminDashboardResponse>(this.API_URL);
  }
}