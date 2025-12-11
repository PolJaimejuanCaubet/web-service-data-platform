// src/app/pages/dashboard-admin/dashboard-admin.component.ts

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth';
import { UserResponse, UserUpdate } from '../../models/user.models';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './dashboard-admin.html',
  styleUrl: './dashboard-admin.css'
})
export class DashboardAdminComponent implements OnInit {
  // Estado del componente
  currentAdmin: UserResponse | null = null;
  allUsers: UserResponse[] = [];
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  // Vista activa
  activeView: 'overview' | 'users' | 'edit' = 'overview';

  // Usuario seleccionado para editar/ver
  selectedUser: UserResponse | null = null;

  // Formulario de edición
  editForm: FormGroup;

  // Estadísticas
  stats = {
    totalUsers: 0,
    adminUsers: 0,
    standardUsers: 0
  };

  private apiUrl = 'http://localhost:8000';

  constructor(
    private authService: AuthService,
    private router: Router,
    private fb: FormBuilder,
    private http: HttpClient
  ) {
    // Inicializar formulario de edición
    this.editForm = this.fb.group({
      full_name: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]]
    });
  }

  ngOnInit(): void {
    console.log('🔵 Admin Dashboard initialized');

    // Obtener admin actual
    this.currentAdmin = this.authService.getCurrentUser();
    console.log('🔵 Current admin:', this.currentAdmin);

    // Verificar que es admin
    if (this.currentAdmin?.role !== 'admin') {
      console.warn('⚠️ User is not admin, redirecting...');
      this.router.navigate(['/dashboard']);
      return;
    }

    // Cargar todos los usuarios
    this.loadAllUsers();
  }

  /**
   * Carga todos los usuarios desde el backend
   */
  loadAllUsers(): void {
    this.isLoading = true;
    this.errorMessage = '';

    console.log('🔵 Loading all users...');

    this.http.get<any>(`${this.apiUrl}/users`).subscribe({
      next: (response) => {
        console.log('✅ Raw response from backend:', response);

        let users: any[] = [];

        // Verificar diferentes formatos de respuesta
        if (Array.isArray(response)) {
          users = response;
        } else if (response && Array.isArray(response.list_of_users)) {
          users = response.list_of_users;
        } else if (response && Array.isArray(response.users)) {
          users = response.users;
        } else if (response && typeof response === 'object') {
          users = Object.values(response);
        }

        // Filtrar usuarios válidos y agregar valores por defecto
        this.allUsers = users
          .filter(u => u && (u.username || u.email))
          .map(u => ({
            ...u,
            username: u.username || 'unknown',
            email: u.email || 'no-email',
            full_name: u.full_name || u.fullname || '',
            role: u.role || 'standard_user',
            id: u.id || u._id
          }));

        console.log('✅ Users loaded:', this.allUsers);
        this.calculateStats();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('❌ Failed to load users:', error);
        this.errorMessage = 'Failed to load users. Please try again.';
        this.allUsers = [];
        this.isLoading = false;
      }
    });
  }

  /**
   * Calcula estadísticas de usuarios
   */
  calculateStats(): void {
    this.stats.totalUsers = this.allUsers.length;
    this.stats.adminUsers = this.allUsers.filter(u => u.role === 'admin').length;
    this.stats.standardUsers = this.allUsers.filter(u => u.role === 'standard_user').length;
  }

  /**
   * Cambia la vista activa
   */
  switchView(view: 'overview' | 'users' | 'edit'): void {
    this.activeView = view;
    this.clearMessages();
  }

  /**
   * Selecciona un usuario para ver/editar
   */
  selectUser(user: UserResponse): void {
    this.selectedUser = user;
    this.activeView = 'edit';

    // Llenar el formulario con los datos del usuario
    this.editForm.patchValue({
      full_name: user.full_name,
      email: user.email
    });

    this.clearMessages();
  }

  /**
   * Guarda los cambios del usuario editado
   */
  saveUserChanges(): void {
    if (this.editForm.invalid || !this.selectedUser?.id) {
      this.editForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.clearMessages();

    const updateData: UserUpdate = {
      full_name: this.editForm.value.full_name,
      email: this.editForm.value.email
    };

    console.log('🔵 Updating user:', this.selectedUser.id);

    this.authService.updateUser(this.selectedUser.id, updateData).subscribe({
      next: (response) => {
        console.log('✅ User updated:', response);
        this.successMessage = 'User updated successfully!';

        // Recargar lista de usuarios
        this.loadAllUsers();

        // Volver a la vista de usuarios después de 1.5s
        setTimeout(() => {
          this.activeView = 'users';
          this.selectedUser = null;
          this.clearMessages();
        }, 1500);

        this.isLoading = false;
      },
      error: (error) => {
        console.error('❌ Failed to update user:', error);
        this.errorMessage = error.message || 'Failed to update user.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Promueve un usuario a administrador
   */
  promoteToAdmin(user: UserResponse): void {
    const confirmed = confirm(
      `Are you sure you want to promote "${user.username}" to Administrator?\n\nThis will grant them full admin privileges.`
    );

    if (!confirmed) return;

    this.isLoading = true;
    this.clearMessages();

    console.log('🔵 Promoting user to admin:', user.id);

    this.http.put<any>(`${this.apiUrl}/users/${user.id}/role`, {}).subscribe({
      next: (response) => {
        console.log('✅ User promoted to admin:', response);
        this.successMessage = `User "${user.username}" promoted to Administrator successfully!`;

        // Recargar lista de usuarios
        this.loadAllUsers();

        if (this.selectedUser && this.selectedUser.id === user.id) {
          this.selectedUser.role = 'admin';  // ✅ TypeScript sabe que selectedUser no es null
        }

        // Limpiar mensaje después de 3s
        setTimeout(() => this.clearMessages(), 3000);

        this.isLoading = false;
      },
      error: (error) => {
        console.error('❌ Failed to promote user:', error);
        this.errorMessage = error.error?.detail || 'Failed to promote user to admin.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Elimina un usuario (con confirmación)
   */
  deleteUser(user: UserResponse): void {
    // Prevenir que el admin se elimine a sí mismo
    if (user.id === this.currentAdmin?.id) {
      this.errorMessage = 'You cannot delete your own account!';
      return;
    }

    const confirmed = confirm(
      `Are you sure you want to delete user "${user.username}"?\n\nThis action cannot be undone.`
    );

    if (!confirmed) return;

    this.isLoading = true;
    this.clearMessages();

    console.log('🔵 Deleting user:', user.id);

    this.authService.deleteUser(user.id!).subscribe({
      next: (response) => {
        console.log('✅ User deleted:', response);
        this.successMessage = `User "${user.username}" deleted successfully.`;

        // Recargar lista de usuarios
        this.loadAllUsers();

        // Si estamos en la vista de edición de este usuario, volver a users
        if (this.selectedUser?.id === user.id) {
          this.activeView = 'users';
          this.selectedUser = null;
        }

        // Limpiar mensaje después de 3s
        setTimeout(() => this.clearMessages(), 3000);

        this.isLoading = false;
      },
      error: (error) => {
        console.error('❌ Failed to delete user:', error);
        this.errorMessage = error.message || 'Failed to delete user.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Cancela la edición y vuelve a la lista
   */
  cancelEdit(): void {
    this.selectedUser = null;
    this.activeView = 'users';
    this.editForm.reset();
    this.clearMessages();
  }

  /**
   * Limpia mensajes de error y éxito
   */
  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }

  /**
   * Cierra sesión del admin
   */
  logout(): void {
    console.log('🔵 Admin logging out');
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  /**
   * Getter para acceder a los controles del formulario
   */
  get f() {
    return this.editForm.controls;
  }
}