import { Routes } from '@angular/router';
import { LoginComponent } from './components/auth/login.component';
import { CustomerComponent } from './components/customer/customer.component';
import { StaffComponent } from './components/staff/staff.component';
import { AdminComponent } from './components/admin/admin.component';
import { roleGuard } from './guards/role.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: 'customer',
    component: CustomerComponent,
    canActivate: [roleGuard],
    data: { role: 'CUSTOMER' }
  },
  {
    path: 'staff',
    component: StaffComponent,
    canActivate: [roleGuard],
    data: { role: 'EMPLOYEE' }
  },
  {
    path: 'admin',
    component: AdminComponent,
    canActivate: [roleGuard],
    data: { role: 'ADMIN' }
  },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: '**', redirectTo: 'login' }
];
