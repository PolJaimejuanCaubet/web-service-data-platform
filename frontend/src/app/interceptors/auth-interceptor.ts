// src/app/interceptors/auth.interceptor.ts

import { HttpInterceptorFn } from '@angular/common/http';

// Functional interceptor (new Angular 15+ style)
// HttpInterceptorFn: Type for interceptor functions
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Get token from localStorage
  const token = localStorage.getItem('access_token');
  
  // If token exists, clone the request and add Authorization header
  if (token) {
    // req.clone: HTTP requests are immutable, so we clone to modify
    const clonedRequest = req.clone({
      // setHeaders: Adds headers to the request
      setHeaders: {
        Authorization: `Bearer ${token}` // JWT token format
      }
    });
    
    // Pass the modified request to the next handler
    return next(clonedRequest);
  }
  
  // If no token, pass the original request
  return next(req);
};