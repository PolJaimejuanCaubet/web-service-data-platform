// src/app/pages/register/register.component.ts

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { UserCreate } from '../../models/user.models';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class RegisterComponent {
  registerForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    // Inicializar formulario con los campos que requiere UserCreate
    this.registerForm = this.fb.group({
      // full_name: requerido por tu backend
      full_name: ['', [
        Validators.required,
        Validators.minLength(3)
      ]],
      
      // username: requerido y único
      username: ['', [
        Validators.required,
        Validators.minLength(3),
        Validators.pattern(/^[a-zA-Z0-9_]+$/)  // Solo letras, números y guión bajo
      ]],
      
      // email: validación de formato email
      email: ['', [
        Validators.required,
        Validators.email
      ]],
      
      // password: mínimo 6 caracteres según tu lógica
      password: ['', [
        Validators.required,
        Validators.minLength(6)
      ]],
      
      // confirmPassword: para verificar que el usuario escribió bien
      confirmPassword: ['', Validators.required]
    }, {
      // Validador personalizado a nivel de formulario
      validators: this.passwordMatchValidator
    });
  }

  /**
   * Validador personalizado para verificar que las contraseñas coincidan
   */
  private passwordMatchValidator(group: FormGroup): {[key: string]: boolean} | null {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    
    // Si no coinciden, devolver objeto de error
    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  /**
   * Getter para acceder fácilmente a los controles del formulario
   * Uso: f['full_name'].invalid
   */
  get f() {
    return this.registerForm.controls;
  }

  /**
   * Método ejecutado al enviar el formulario
   */
  onSubmit(): void {
    // Si el formulario es inválido, marcar todos los campos como touched
    // para mostrar los mensajes de error
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    // Mostrar estado de carga
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    // Extraer valores del formulario
    const { full_name, username, email, password } = this.registerForm.value;

    // Crear objeto UserCreate que coincide con el modelo de Pydantic
    const userData: UserCreate = {
      full_name,
      username,
      email,
      password
      // role no se envía, el backend lo asigna como "standard_user"
    };

    // Llamar al servicio de autenticación
    this.authService.register(userData).subscribe({
      // Caso de éxito
      next: (response) => {
        console.log('Registration successful:', response);
        
        // Mostrar mensaje de éxito
        this.successMessage = `${response.message}! Redirecting to login...`;
        
        // Esperar 1.5 segundos y redirigir al login
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 1500);
      },
      
      // Caso de error
      error: (error) => {
        console.error('Registration failed:', error);
        
        // Extraer mensaje de error
        // El servicio ya procesó el error, solo obtenemos el message
        this.errorMessage = error.message || 'Registration failed. Please try again.';
        
        this.isLoading = false;
      },
      
      // Ejecutado al completar (éxito o error)
      complete: () => {
        // Solo detener loading si no hubo éxito
        // (si hubo éxito, ya redirigimos)
        if (!this.successMessage) {
          this.isLoading = false;
        }
      }
    });
  }

  /**
   * Método para limpiar mensajes de error cuando el usuario empieza a escribir
   */
  onInputChange(): void {
    if (this.errorMessage) {
      this.errorMessage = '';
    }
  }
}