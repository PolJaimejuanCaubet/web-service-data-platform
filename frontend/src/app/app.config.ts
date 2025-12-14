// src/app/app.config.ts

import { ApplicationConfig, provideZoneChangeDetection, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { MarkdownModule } from 'ngx-markdown';

import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth-interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // Optimización de detección de cambios
    provideZoneChangeDetection({ eventCoalescing: true }),

    // Router
    provideRouter(routes),

    // HttpClient + interceptor
    provideHttpClient(
      withInterceptors([authInterceptor])
    ),

    // ✅ Markdown global
    importProvidersFrom(
      MarkdownModule.forRoot()
    )
  ]
};
