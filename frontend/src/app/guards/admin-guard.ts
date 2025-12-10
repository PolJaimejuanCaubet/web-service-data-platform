// src/app/guards/admin.guard.ts

import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth';
import { map, take } from 'rxjs/operators';

/**
 * Guard para proteger rutas de administrador
 * Solo permite acceso si el usuario está autenticado Y es admin
 */
export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.currentUser$.pipe(
    take(1),
    map(user => {
      // Si no hay usuario o no es admin, redirigir
      if (!user || user.role !== 'admin') {
        console.warn('⚠️ Access denied: User is not admin');
        router.navigate(['/dashboard']);
        return false;
      }
      
      console.log('✅ Admin access granted');
      return true;
    })
  );
};