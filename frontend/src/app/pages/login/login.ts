// src/app/pages/login/login.component.ts

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { UserLogin } from '../../models/user.models';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class LoginComponent {
  loginForm: FormGroup;
  isLoading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', [
        Validators.required,
        Validators.minLength(3)
      ]],
      password: ['', [
        Validators.required,
        Validators.minLength(6)
      ]]
    });
  }

  get f() {
    return this.loginForm.controls;
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const { username, password } = this.loginForm.value;
    const credentials: UserLogin = {
      username,
      password
    };

    console.log('🔵 Attempting login with:', { username });

    this.authService.login(credentials).subscribe({
      next: (response) => {
        console.log('✅ Login successful:', response);
        
        // DESPUÉS DEL LOGIN: Cargar datos completos del usuario
        this.authService.getUserById(response.user.id).subscribe({
          next: (userData) => {
            console.log('✅ User data loaded:', userData);
            
            // REDIRIGIR SEGÚN EL ROL
            if (userData.role === 'admin') {
              console.log('🛡️ Admin user, redirecting to admin dashboard');
              this.router.navigate(['/admin']);
            } else {
              console.log('👤 Standard user, redirecting to user dashboard');
              this.router.navigate(['/dashboard']);
            }
            
            this.isLoading = false;
          },
          error: (error) => {
            console.error('❌ Failed to load user data:', error);
            // Si falla cargar datos, redirigir al dashboard normal
            this.router.navigate(['/dashboard']);
            this.isLoading = false;
          }
        });
      },
      
      error: (error) => {
        console.error('❌ Login failed:', error);
        this.errorMessage = error.message || 'Login failed. Please check your credentials.';
        this.isLoading = false;
      }
    });
  }

  onInputChange(): void {
    if (this.errorMessage) {
      this.errorMessage = '';
    }
  }
}