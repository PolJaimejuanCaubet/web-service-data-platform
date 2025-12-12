// src/app/services/auth.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import {
  UserCreate,
  UserLogin,
  RegisterResponse,
  LoginResponse,
  UserResponse,
  FastAPIError,
  UserUpdate
} from '../models/user.models';

import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl

  // BehaviorSubject para mantener el estado de autenticación
  // Emite true si hay token, false si no hay
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  // BehaviorSubject para mantener los datos del usuario actual
  private currentUserSubject = new BehaviorSubject<UserResponse | null>(
    this.getUserFromStorage()
  );
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) { }

  /**
   * Verifica si existe un token en localStorage
   * @returns boolean - true si existe token
   */
  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  /**
   * Obtiene la información del usuario desde localStorage
   * @returns UserResponse | null
   */
  private getUserFromStorage(): UserResponse | null {
    const userJson = localStorage.getItem('current_user');
    return userJson ? JSON.parse(userJson) : null;
  }

  /**
   * REGISTER - Coincide con POST /auth/register
   * Envía: UserCreate (full_name, username, email, password)
   * Recibe: RegisterResponse (message, user_id, email, role)
   */
  register(userData: UserCreate): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(
      `${this.apiUrl}/auth/register`,
      userData  // FastAPI espera JSON, no FormData
    ).pipe(
      tap(response => {
        // El registro no devuelve token, solo confirma la creación
        console.log('User registered:', response);
        // Nota: Después del registro, típicamente redirigimos al login
        // o automáticamente hacemos login
      }),
      catchError(this.handleError)  // Manejo de errores
    );
  }

  /**
   * LOGIN - Coincide con POST /auth/login
   * FastAPI usa OAuth2PasswordRequestForm que espera:
   * - Content-Type: application/x-www-form-urlencoded
   * - Fields: username y password
   */
  login(credentials: UserLogin): Observable<LoginResponse> {
    // OAuth2PasswordRequestForm de FastAPI requiere FormData
    // no JSON, con campos 'username' y 'password'
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<LoginResponse>(
      `${this.apiUrl}/auth/login`,
      formData.toString(),  // Convertir a string
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    ).pipe(
      tap(response => {
        // Guardar token y datos de usuario
        this.storeAuthData(response);
        console.log('Login successful:', response);
      }),
      catchError(this.handleError)
    );
  }

  /**
   * Almacena el token y los datos del usuario en localStorage
   * y actualiza los BehaviorSubjects
   */
  private storeAuthData(response: LoginResponse): void {
    // Guardar token
    localStorage.setItem('access_token', response.access_token);

    // Guardar datos básicos del usuario
    const userData: UserResponse = {
      full_name: '',  // No viene en la respuesta de login
      username: response.user.username,
      email: '',      // No viene en la respuesta de login
      role: '',       // No viene en la respuesta de login
      id: response.user.id
    };

    localStorage.setItem('current_user', JSON.stringify(userData));

    // Notificar a los observadores
    this.isAuthenticatedSubject.next(true);
    this.currentUserSubject.next(userData);
  }

  /**
   * LOGOUT - Limpia los datos de autenticación
   * Nota: Tu backend aún no tiene endpoint de logout,
   * pero podemos hacerlo en el frontend
   */
  logout(): void {
    // Limpiar localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');

    // Notificar a los observadores
    this.isAuthenticatedSubject.next(false);
    this.currentUserSubject.next(null);
  }

  /**
   * Obtiene el token almacenado
   * @returns string | null
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Obtiene el usuario actual desde el BehaviorSubject
   * @returns UserResponse | null
   */
  getCurrentUser(): UserResponse | null {
    return this.currentUserSubject.value;
  }

  /**
   * GET /users/{user_id} - Obtiene información completa del usuario
   * Requiere autenticación (el interceptor añade el token)
   */
  getUserById(userId: string): Observable<UserResponse> {
    return this.http.get<UserResponse>(`${this.apiUrl}/users/${userId}`)
      .pipe(
        tap(user => {
          // Actualizar los datos del usuario en memoria
          localStorage.setItem('current_user', JSON.stringify(user));
          this.currentUserSubject.next(user);
        }),
        catchError(this.handleError)
      );
  }

  /**
   * PUT /users/{user_id} - Actualiza información del usuario
   */
  updateUser(userId: string, userData: UserUpdate): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/${userId}`, userData)
      .pipe(
        tap(response => {
          console.log('User updated:', response);
          // Recargar datos del usuario después de actualizar
          this.getUserById(userId).subscribe();
        }),
        catchError(this.handleError)
      );
  }

  /**
   * DELETE /users/{user_id} - Elimina el usuario
   */
  deleteUser(userId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/users/${userId}`)
      .pipe(
        tap(response => {
          console.log('User deleted:', response);
          // Si el usuario se elimina a sí mismo, hacer logout
          const currentUser = this.getCurrentUser();
          if (currentUser?.id === userId) {
            this.logout();
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Verifica si el usuario actual es admin
   * @returns boolean
   */
  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin';
  }

  /**
   * Manejo centralizado de errores HTTP
   * FastAPI devuelve errores en formato: { detail: "mensaje" }
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Error del lado del servidor (FastAPI)
      if (error.error?.detail) {
        // FastAPI devuelve el mensaje en 'detail'
        errorMessage = error.error.detail;
      } else if (typeof error.error === 'string') {
        errorMessage = error.error;
      } else {
        errorMessage = `Server Error: ${error.status} - ${error.message}`;
      }
    }

    console.error('HTTP Error:', errorMessage);

    // Devolver un Observable que emite el error
    return throwError(() => new Error(errorMessage));
  }
}