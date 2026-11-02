import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

export interface UserProfile {
  user_id: number;
  email: str;
  full_name: string;
  role: 'ADMIN' | 'EMPLOYEE' | 'CUSTOMER';
  status: string;
  access_token?: string;
}

type str = string;

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000/api/v1';
  
  // Reactive signals
  currentUser = signal<UserProfile | null>(this.getStoredUser());
  isLoggedIn = computed(() => !!this.currentUser());
  userRole = computed(() => this.currentUser()?.role || null);

  constructor(private http: HttpClient, private router: Router) {}

  private getStoredUser(): UserProfile | null {
    const data = localStorage.getItem('bank_user');
    if (!data) return null;
    try {
      return JSON.parse(data);
    } catch {
      return null;
    }
  }

  getToken(): string | null {
    const user = this.currentUser();
    return user?.access_token || localStorage.getItem('bank_token') || null;
  }

  getAuthHeaders(): { [header: string]: string } {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  login(credentials: { email: str; password: str }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/login`, credentials).pipe(
      tap((res) => {
        const profile: UserProfile = {
          user_id: res.user_id,
          email: res.email,
          full_name: res.full_name,
          role: res.role,
          status: res.status,
          access_token: res.access_token
        };
        localStorage.setItem('bank_token', res.access_token);
        localStorage.setItem('bank_user', JSON.stringify(profile));
        this.currentUser.set(profile);
      })
    );
  }

  registerCustomer(data: { email: str; password: str; full_name: string; phone_number?: string }): Observable<any> {
    // Strictly registers customer - no role param
    return this.http.post<any>(`${this.apiUrl}/auth/register`, data);
  }

  logout(): void {
    localStorage.removeItem('bank_token');
    localStorage.removeItem('bank_user');
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  navigateByRole(): void {
    const role = this.userRole();
    if (role === 'ADMIN') {
      this.router.navigate(['/admin']);
    } else if (role === 'EMPLOYEE') {
      this.router.navigate(['/staff']);
    } else {
      this.router.navigate(['/customer']);
    }
  }
}
