import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.isLoggedIn()) {
    router.navigate(['/login']);
    return false;
  }

  const expectedRole = route.data?.['role'];
  const userRole = auth.userRole();

  if (expectedRole && userRole !== expectedRole) {
    // If not authorized for this specific dashboard, redirect to their role's page
    auth.navigateByRole();
    return false;
  }

  return true;
};
