/**
 * Sistema de Gestión de Tiendas con Autenticación
 * 
 * Este archivo contiene toda la lógica del frontend:
 * - Gestión de autenticación (login/registro/logout)
 * - Manejo de tokens JWT
 * - Control de acceso por roles
 * - CRUD de tiendas con protección
 * - Gestión de usuarios (solo admins)
 */

// ============================================================================
// VARIABLES GLOBALES Y CONFIGURACIÓN
// ============================================================================

// Estado de la aplicación
let app = {
    user: null,
    token: null,
    isAuthenticated: false,
    isAdmin: false,
    currentPage: 1,
    totalPages: 1,
    currentPerPage: 10,
    currentAction: null
};

// URLs de la API
const API = {
    base: window.location.origin + '/api',
    users: {
        register: '/users/register',
        login: '/users/login',
        profile: '/users/profile',
        list: '/users/',
        verify: '/users/verify-token'
    },
    stores: {
        list: '/stores',
        create: '/stores',
        update: (id) => `/stores/${id}`,
        delete: (id) => `/stores/${id}`,
        stats: '/stores/stats'
    }
};

// ============================================================================
// UTILIDADES GENERALES
// ============================================================================

/**
 * Mostrar/ocultar overlay de carga
 */
function showLoading(show = true) {
    if (show) {
        $('#loadingOverlay').removeClass('hidden');
    } else {
        $('#loadingOverlay').addClass('hidden');
    }
}

/**
 * Mostrar notificación toast
 */
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' :
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 70px; right: 20px; z-index: 10000; min-width: 300px;">
            <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `);
    
    $('body').append(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        notification.alert('close');
    }, 5000);
}

/**
 * Realizar petición AJAX con autenticación
 */
function apiRequest(options) {
    const defaults = {
        dataType: 'json',
        contentType: 'application/json',
        beforeSend: function(xhr) {
            if (app.token) {
                xhr.setRequestHeader('Authorization', `Bearer ${app.token}`);
            }
        },
        error: function(xhr, status, error) {
            console.error('API Error:', xhr.responseJSON || error);
            
            if (xhr.status === 401) {
                showNotification('Sesión expirada. Por favor, inicia sesión nuevamente.', 'error');
                logout();
            } else if (xhr.responseJSON && xhr.responseJSON.message) {
                showNotification(xhr.responseJSON.message, 'error');
            } else {
                showNotification('Error en la petición: ' + error, 'error');
            }
        }
    };
    
    return $.ajax($.extend(defaults, options));
}

// ============================================================================
// GESTIÓN DE AUTENTICACIÓN
// ============================================================================

/**
 * Verificar si hay token almacenado y validarlo
 */
function checkAuthentication() {
    const token = localStorage.getItem('auth_token');
    const userData = localStorage.getItem('user_data');
    
    if (token && userData) {
        try {
            app.token = token;
            app.user = JSON.parse(userData);
            
            // Verificar que el token siga siendo válido
            apiRequest({
                url: API.base + API.users.verify,
                method: 'GET',
                success: function(response) {
                    if (response.success) {
                        app.isAuthenticated = true;
                        app.isAdmin = response.data.role === 'admin';
                        updateUIForAuthentication();
                        loadStores();
                    } else {
                        logout();
                    }
                },
                error: function() {
                    logout();
                }
            });
        } catch (e) {
            logout();
        }
    } else {
        showGuestView();
    }
}

/**
 * Realizar login
 */
function login(identifier, password) {
    showLoading();
    
    apiRequest({
        url: API.base + API.users.login,
        method: 'POST',
        data: JSON.stringify({
            identifier: identifier,
            password: password
        }),
        success: function(response) {
            if (response.success) {
                // Guardar datos de autenticación
                app.token = response.data.access_token;
                app.user = response.data;
                app.isAuthenticated = true;
                app.isAdmin = response.data.role === 'admin';
                
                localStorage.setItem('auth_token', app.token);
                localStorage.setItem('user_data', JSON.stringify(app.user));
                
                showNotification('¡Bienvenido! Sesión iniciada correctamente.', 'success');
                updateUIForAuthentication();
                loadStores();
            }
        },
        error: function(xhr) {
            const message = xhr.responseJSON?.message || 'Error al iniciar sesión';
            showNotification(message, 'error');
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Realizar registro
 */
function register(username, email, password) {
    showLoading();
    
    apiRequest({
        url: API.base + API.users.register,
        method: 'POST',
        data: JSON.stringify({
            username: username,
            email: email,
            password: password
        }),
        success: function(response) {
            if (response.success) {
                showNotification('¡Registro exitoso! Ya puedes iniciar sesión.', 'success');
                switchToLogin();
            }
        },
        error: function(xhr) {
            const message = xhr.responseJSON?.message || 'Error al registrarse';
            showNotification(message, 'error');
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Cerrar sesión
 */
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    
    app.token = null;
    app.user = null;
    app.isAuthenticated = false;
    app.isAdmin = false;
    
    showGuestView();
    showNotification('Sesión cerrada correctamente.', 'info');
}

// ============================================================================
// GESTIÓN DE INTERFAZ DE USUARIO
// ============================================================================

/**
 * Mostrar vista para usuarios no autenticados
 */
function showGuestView() {
    $('#guestNav').removeClass('hidden');
    $('#userNav').addClass('hidden');
    $('#authPanel').removeClass('hidden');
    $('#mainPanel').addClass('hidden');
    $('.admin-only').addClass('hidden');
    
    // Mostrar formulario de login por defecto
    switchToLogin();
}

/**
 * Actualizar UI para usuario autenticado
 */
function updateUIForAuthentication() {
    $('#guestNav').addClass('hidden');
    $('#userNav').removeClass('hidden');
    $('#authPanel').addClass('hidden');
    $('#mainPanel').removeClass('hidden');
    
    // Actualizar información del usuario
    $('#welcomeUser').text(app.user.username);
    $('#userRole').text(app.user.role.toUpperCase());
    
    $('#userInfoName').text(app.user.username);
    $('#userInfoEmail').text(app.user.email);
    $('#userInfoRole').text(app.user.role.toUpperCase());
    
    // Mostrar elementos de admin si corresponde
    if (app.isAdmin) {
        $('.admin-only').removeClass('hidden');
    } else {
        $('.admin-only').addClass('hidden');
    }
}

/**
 * Cambiar entre formularios de login y registro
 */
function switchToLogin() {
    $('#loginForm').removeClass('hidden');
    $('#registerForm').addClass('hidden');
    $('#loginFormElement')[0].reset();
}

function switchToRegister() {
    $('#loginForm').addClass('hidden');
    $('#registerForm').removeClass('hidden');
    $('#registerFormElement')[0].reset();
}

/**
 * Mostrar panel específico
 */
function showPanel(panelName) {
    // Ocultar todos los paneles
    $('#storesPanel, #usersPanel, #statsPanel').addClass('hidden');
    
    // Mostrar el panel solicitado
    $(`#${panelName}Panel`).removeClass('hidden');
    
    // Cargar datos específicos del panel
    switch(panelName) {
        case 'stores':
            loadStores();
            break;
        case 'users':
            if (app.isAdmin) loadUsers();
            break;
        case 'stats':
            if (app.isAdmin) loadStats();
            break;
    }
}

// ============================================================================
// GESTIÓN DE TIENDAS
// ============================================================================

/**
 * Cargar lista de tiendas con paginación
 */
function loadStores(page = 1, perPage = app.currentPerPage) {
    showLoading();
    
    apiRequest({
        url: `${API.base}${API.stores.list}?page=${page}&per_page=${perPage}`,
        method: 'GET',
        success: function(response) {
            if (response.success || response.stores) {
                renderStores(response.stores || response.data);
                updatePagination(response.pagination);
                app.currentPage = page;
                app.currentPerPage = perPage;
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Renderizar lista de tiendas
 */
function renderStores(stores) {
    const $storeList = $('#storeList');
    $storeList.empty();
    
    if (stores && stores.length > 0) {
        stores.forEach(store => {
            const storeCard = $(`
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card store-item h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0"><i class="fas fa-store"></i> Tienda #${store.store_id}</h6>
                            <div class="admin-only">
                                <button class="btn btn-sm btn-outline-primary edit-store-btn" data-id="${store.store_id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger delete-store-btn" data-id="${store.store_id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-6">
                                    <p class="mb-2">
                                        <i class="fas fa-expand-arrows-alt text-primary"></i>
                                        <strong>Área:</strong><br>
                                        <span class="ml-3">${store.store_area} m²</span>
                                    </p>
                                    <p class="mb-2">
                                        <i class="fas fa-users text-info"></i>
                                        <strong>Clientes diarios:</strong><br>
                                        <span class="ml-3">${store.daily_customer_count.toLocaleString()}</span>
                                    </p>
                                </div>
                                <div class="col-6">
                                    <p class="mb-2">
                                        <i class="fas fa-boxes text-warning"></i>
                                        <strong>Artículos:</strong><br>
                                        <span class="ml-3">${store.items_available.toLocaleString()}</span>
                                    </p>
                                    <p class="mb-2">
                                        <i class="fas fa-dollar-sign text-success"></i>
                                        <strong>Ventas:</strong><br>
                                        <span class="ml-3">$${parseFloat(store.store_sales).toLocaleString()}</span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
            
            $storeList.append(storeCard);
        });
        
        // Actualizar visibilidad de elementos admin
        if (app.isAdmin) {
            $('.admin-only').removeClass('hidden');
        } else {
            $('.admin-only').addClass('hidden');
        }
    } else {
        $storeList.html(`
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-store fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">No se encontraron tiendas</h4>
                    <p class="text-muted">No hay tiendas disponibles en este momento.</p>
                </div>
            </div>
        `);
    }
}

/**
 * Actualizar controles de paginación
 */
function updatePagination(pagination) {
    if (!pagination) return;
    
    const info = `Mostrando ${pagination.page === 1 ? 1 : ((pagination.page - 1) * pagination.per_page) + 1} - 
                 ${Math.min(pagination.page * pagination.per_page, pagination.total)} de ${pagination.total} tiendas`;
    $('#paginationInfo').html(info);
    
    $('#currentPageBtn').text(`Página ${pagination.page} de ${pagination.total_pages}`);
    
    // Actualizar estado de botones
    $('#firstPageItem, #prevPageItem').toggleClass('disabled', !pagination.has_prev);
    $('#nextPageItem, #lastPageItem').toggleClass('disabled', !pagination.has_next);
    
    app.currentPage = pagination.page;
    app.totalPages = pagination.total_pages;
}

/**
 * Crear o actualizar tienda
 */
function saveStore(storeData, storeId = null) {
    showLoading();
    
    const url = storeId ? 
        API.base + API.stores.update(storeId) : 
        API.base + API.stores.create;
    
    const method = storeId ? 'PUT' : 'POST';
    
    apiRequest({
        url: url,
        method: method,
        data: JSON.stringify(storeData),
        success: function(response) {
            if (response.success) {
                const message = storeId ? 'Tienda actualizada correctamente' : 'Tienda creada correctamente';
                showNotification(message, 'success');
                hideStoreForm();
                loadStores(app.currentPage, app.currentPerPage);
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Eliminar tienda
 */
function deleteStore(storeId) {
    showLoading();
    
    apiRequest({
        url: API.base + API.stores.delete(storeId),
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                showNotification('Tienda eliminada correctamente', 'success');
                loadStores(app.currentPage, app.currentPerPage);
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Mostrar/ocultar formulario de tienda
 */
function showStoreForm(storeData = null) {
    const isEdit = !!storeData;
    
    $('#storeFormTitle').html(isEdit ? 
        '<i class="fas fa-edit"></i> Editar Tienda' : 
        '<i class="fas fa-plus"></i> Nueva Tienda'
    );
    
    $('#submitBtn').html(isEdit ? 
        '<i class="fas fa-save"></i> Actualizar' : 
        '<i class="fas fa-save"></i> Guardar'
    );
    
    if (isEdit) {
        $('#storeArea').val(storeData.store_area);
        $('#itemsAvailable').val(storeData.items_available);
        $('#dailyCustomerCount').val(storeData.daily_customer_count);
        $('#storeSales').val(storeData.store_sales);
        $('#storeForm').data('store-id', storeData.store_id);
    } else {
        $('#storeForm')[0].reset();
        $('#storeForm').removeData('store-id');
    }
    
    $('#storeFormContainer').removeClass('hidden');
    
    // Scroll hacia el formulario
    $('html, body').animate({
        scrollTop: $('#storeFormContainer').offset().top - 100
    }, 500);
}

function hideStoreForm() {
    $('#storeFormContainer').addClass('hidden');
    $('#storeForm')[0].reset();
    $('#storeForm').removeData('store-id');
}

// ============================================================================
// GESTIÓN DE USUARIOS (SOLO ADMINS)
// ============================================================================

/**
 * Cargar lista de usuarios
 */
function loadUsers() {
    if (!app.isAdmin) return;
    
    showLoading();
    
    apiRequest({
        url: API.base + API.users.list,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                renderUsers(response.data);
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Renderizar lista de usuarios
 */
function renderUsers(users) {
    const $usersList = $('#usersList');
    $usersList.empty();
    
    if (users && users.length > 0) {
        users.forEach(user => {
            const isCurrentUser = user.user_id === app.user.user_id;
            const statusBadge = user.is_active ? 
                '<span class="badge badge-success">Activo</span>' : 
                '<span class="badge badge-danger">Inactivo</span>';
            
            const roleBadge = user.role === 'admin' ? 
                '<span class="badge badge-primary">Admin</span>' : 
                '<span class="badge badge-secondary">Usuario</span>';
            
            const userRow = $(`
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-6">
                                <h6><i class="fas fa-user"></i> ${user.username}</h6>
                                <p class="mb-1 text-muted">${user.email}</p>
                                <small class="text-muted">ID: ${user.user_id} • Creado: ${new Date(user.created_at).toLocaleDateString()}</small>
                            </div>
                            <div class="col-md-3">
                                ${roleBadge} ${statusBadge}
                            </div>
                            <div class="col-md-3">
                                ${!isCurrentUser ? `
                                    <button class="btn btn-sm btn-outline-secondary edit-user-btn" 
                                            data-id="${user.user_id}" data-username="${user.username}" 
                                            data-email="${user.email}" data-role="${user.role}">
                                        <i class="fas fa-edit"></i>
                                        Editar
                                    </button>
                                    <button class="btn btn-sm btn-outline-primary toggle-user-status" 
                                            data-id="${user.user_id}" data-status="${user.is_active}">
                                        <i class="fas fa-${user.is_active ? 'ban' : 'check'}"></i>
                                        ${user.is_active ? 'Desactivar' : 'Activar'}
                                    </button>
                                    <button class="btn btn-sm btn-outline-warning toggle-user-role" 
                                            data-id="${user.user_id}" data-role="${user.role}">
                                        <i class="fas fa-user-cog"></i>
                                        ${user.role === 'admin' ? 'Hacer Usuario' : 'Hacer Admin'}
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger delete-user-btn" 
                                            data-id="${user.user_id}" data-username="${user.username}">
                                        <i class="fas fa-trash"></i>
                                        Eliminar
                                    </button>
                                ` : '<small class="text-muted">Tu cuenta</small>'}
                            </div>
                        </div>
                    </div>
                </div>
            `);
            
            $usersList.append(userRow);
        });
    } else {
        $usersList.html(`
            <div class="text-center py-4">
                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                <h4 class="text-muted">No se encontraron usuarios</h4>
            </div>
        `);
    }
}

/**
 * Editar usuario existente (solo admin)
 */
function editUser(userId, username, email, role) {
    if (!app.isAdmin) return;
    
    // Mostrar formulario con datos pre-cargados
    $('#editUserFormContainer').removeClass('hidden');
    $('#editUserId').val(userId);
    $('#editUsername').val(username);
    $('#editUserEmail').val(email);
    $('#editUserRole').val(role);
    $('#editUserPassword').val(''); // Contraseña vacía
    
    // Scroll hacia el formulario
    $('html, body').animate({
        scrollTop: $('#editUserFormContainer').offset().top - 100
    }, 500);
}

/**
 * Actualizar usuario existente (solo admin)
 */
function updateUser(userId, userData) {
    if (!app.isAdmin) return;
    
    showLoading();
    
    apiRequest({
        url: `${API.base}/users/${userId}`,
        method: 'PUT',
        data: JSON.stringify(userData),
        success: function(response) {
            if (response.success) {
                showNotification('Usuario actualizado exitosamente', 'success');
                hideEditUserForm();
                loadUsers();
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Eliminar usuario (solo admin)
 */
function deleteUser(userId, username) {
    if (!app.isAdmin) return;
    
    showLoading();
    
    apiRequest({
        url: `${API.base}/users/${userId}`,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                showNotification(`Usuario ${username} eliminado exitosamente`, 'success');
                loadUsers();
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Mostrar/ocultar formulario de editar usuario
 */
function showEditUserForm() {
    $('#editUserFormContainer').removeClass('hidden');
    
    // Scroll hacia el formulario
    $('html, body').animate({
        scrollTop: $('#editUserFormContainer').offset().top - 100
    }, 500);
}

function hideEditUserForm() {
    $('#editUserFormContainer').addClass('hidden');
    $('#editUserForm')[0].reset();
}

/**
 * Crear nuevo usuario (solo admin)
 */
function createUser(username, email, password, role = 'user') {
    if (!app.isAdmin) return;
    
    showLoading();
    
    apiRequest({
        url: `${API.base}/users/create`,
        method: 'POST',
        data: JSON.stringify({
            username: username,
            email: email,
            password: password,
            role: role
        }),
        success: function(response) {
            if (response.success) {
                showNotification(`Usuario ${role} creado exitosamente`, 'success');
                hideUserForm();
                loadUsers();
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Mostrar/ocultar formulario de usuario
 */
function showUserForm() {
    $('#userFormContainer').removeClass('hidden');
    $('#userForm')[0].reset();
    
    // Scroll hacia el formulario
    $('html, body').animate({
        scrollTop: $('#userFormContainer').offset().top - 100
    }, 500);
}

function hideUserForm() {
    $('#userFormContainer').addClass('hidden');
    $('#userForm')[0].reset();
}

/**
 * Cambiar estado de usuario (activo/inactivo)
 */
function toggleUserStatus(userId) {
    if (!app.isAdmin) return;
    
    showLoading();
    
    apiRequest({
        url: `${API.base}/users/${userId}/toggle-status`,
        method: 'PUT',
        success: function(response) {
            if (response.success) {
                showNotification('Estado de usuario actualizado', 'success');
                loadUsers();
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Cambiar rol de usuario
 */
function toggleUserRole(userId, currentRole) {
    if (!app.isAdmin) return;
    
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    
    showLoading();
    
    apiRequest({
        url: `${API.base}/users/${userId}/role`,
        method: 'PUT',
        data: JSON.stringify({ role: newRole }),
        success: function(response) {
            if (response.success) {
                showNotification('Rol de usuario actualizado', 'success');
                loadUsers();
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

// ============================================================================
// ESTADÍSTICAS (SOLO ADMINS)
// ============================================================================

/**
 * Cargar estadísticas
 */
function loadStats() {
    if (!app.isAdmin) return;
    
    showLoading();
    
    apiRequest({
        url: API.base + API.stores.stats,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                renderStats(response.data);
            }
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Renderizar estadísticas
 */
function renderStats(stats) {
    const $statsContent = $('#statsContent');
    $statsContent.html(`
        <div class="col-md-3">
            <div class="text-center">
                <h3 class="mb-0">${stats.total_stores}</h3>
                <p class="mb-0">Total Tiendas</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="text-center">
                <h3 class="mb-0">$${stats.sales.total.toLocaleString()}</h3>
                <p class="mb-0">Ventas Totales</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="text-center">
                <h3 class="mb-0">$${stats.sales.average.toLocaleString()}</h3>
                <p class="mb-0">Promedio por Tienda</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="text-center">
                <h3 class="mb-0">${stats.averages.daily_customers.toLocaleString()}</h3>
                <p class="mb-0">Clientes Promedio</p>
            </div>
        </div>
    `);
}

// ============================================================================
// MODAL DE CONFIRMACIÓN
// ============================================================================

/**
 * Mostrar modal de confirmación
 */
function showConfirmModal(message, onConfirm) {
    $('#confirmModalBody').text(message);
    $('#confirmActionBtn').off('click').on('click', function() {
        $('#confirmModal').modal('hide');
        onConfirm();
    });
    $('#confirmModal').modal('show');
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

$(document).ready(function() {
    // Inicializar aplicación
    checkAuthentication();
    
    // === AUTENTICACIÓN ===
    
    // Mostrar formularios de autenticación
    $('#showLoginBtn').on('click', switchToLogin);
    $('#showRegisterBtn').on('click', switchToRegister);
    $('#switchToLogin').on('click', switchToLogin);
    $('#switchToRegister').on('click', switchToRegister);
    
    // Formulario de login
    $('#loginFormElement').on('submit', function(e) {
        e.preventDefault();
        const identifier = $('#loginIdentifier').val().trim();
        const password = $('#loginPassword').val();
        
        if (identifier && password) {
            login(identifier, password);
        }
    });
    
    // Formulario de registro
    $('#registerFormElement').on('submit', function(e) {
        e.preventDefault();
        const username = $('#registerUsername').val().trim();
        const email = $('#registerEmail').val().trim();
        const password = $('#registerPassword').val();
        const confirmPassword = $('#confirmPassword').val();
        
        if (password !== confirmPassword) {
            showNotification('Las contraseñas no coinciden', 'error');
            return;
        }
        
        if (username && email && password) {
            register(username, email, password);
        }
    });
    
    // Logout
    $('#logoutBtn').on('click', logout);
    
    // === NAVEGACIÓN ===
    
    // Navegación entre paneles
    $('#profileBtn').on('click', () => showPanel('stores'));
    $('#usersManagementBtn').on('click', () => showPanel('users'));
    $('#statsBtn').on('click', () => showPanel('stats'));
    
    // Ocultar información de usuario
    $('#hideUserInfo').on('click', function() {
        $('#userInfo').addClass('hidden');
    });
    
    // === TIENDAS ===
    
    // Paginación
    $('#firstPageBtn').on('click', function(e) {
        e.preventDefault();
        if (app.currentPage > 1) {
            loadStores(1, app.currentPerPage);
        }
    });
    
    $('#prevPageBtn').on('click', function(e) {
        e.preventDefault();
        if (app.currentPage > 1) {
            loadStores(app.currentPage - 1, app.currentPerPage);
        }
    });
    
    $('#nextPageBtn').on('click', function(e) {
        e.preventDefault();
        if (app.currentPage < app.totalPages) {
            loadStores(app.currentPage + 1, app.currentPerPage);
        }
    });
    
    $('#lastPageBtn').on('click', function(e) {
        e.preventDefault();
        if (app.currentPage < app.totalPages) {
            loadStores(app.totalPages, app.currentPerPage);
        }
    });
    
    // Cambio de elementos por página
    $('#perPageSelect').on('change', function() {
        app.currentPerPage = parseInt($(this).val());
        loadStores(1, app.currentPerPage);
    });
    
    // Actualizar tiendas
    $('#fetchStoresBtn').on('click', function() {
        loadStores(app.currentPage, app.currentPerPage);
    });
    
    // Mostrar formulario de nueva tienda
    $('#showStoreFormBtn').on('click', function() {
        showStoreForm();
    });
    
    // Formulario de tienda
    $('#storeForm').on('submit', function(e) {
        e.preventDefault();
        
        const storeData = {
            store_area: parseFloat($('#storeArea').val()),
            items_available: parseInt($('#itemsAvailable').val()),
            daily_customer_count: parseInt($('#dailyCustomerCount').val()),
            store_sales: parseFloat($('#storeSales').val())
        };
        
        const storeId = $(this).data('store-id');
        saveStore(storeData, storeId);
    });
    
    // Cancelar formulario
    $('#cancelBtn').on('click', hideStoreForm);
    
    // === EVENTOS DELEGADOS ===
    
    // Editar tienda
    $(document).on('click', '.edit-store-btn', function() {
        const storeId = $(this).data('id');
        
        apiRequest({
            url: `${API.base}/stores/${storeId}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    showStoreForm(response.data);
                } else if (response.store_area) {
                    // Respuesta directa del store
                    showStoreForm(response);
                }
            }
        });
    });
    
    // Eliminar tienda
    $(document).on('click', '.delete-store-btn', function() {
        const storeId = $(this).data('id');
        showConfirmModal(
            '¿Estás seguro de que deseas eliminar esta tienda? Esta acción no se puede deshacer.',
            () => deleteStore(storeId)
        );
    });
    
    // Editar usuario
    $(document).on('click', '.edit-user-btn', function() {
        const userId = $(this).data('id');
        const username = $(this).data('username');
        const email = $(this).data('email');
        const role = $(this).data('role');
        
        editUser(userId, username, email, role);
    });
    
    // Eliminar usuario
    $(document).on('click', '.delete-user-btn', function() {
        const userId = $(this).data('id');
        const username = $(this).data('username');
        
        showConfirmModal(
            `¿Estás seguro de que deseas eliminar el usuario "${username}"? Esta acción no se puede deshacer.`,
            () => deleteUser(userId, username)
        );
    });
    
    // Cambiar estado de usuario
    $(document).on('click', '.toggle-user-status', function() {
        const userId = $(this).data('id');
        const isActive = $(this).data('status');
        const action = isActive ? 'desactivar' : 'activar';
        
        showConfirmModal(
            `¿Estás seguro de que deseas ${action} este usuario?`,
            () => toggleUserStatus(userId)
        );
    });
    
    // Cambiar rol de usuario
    $(document).on('click', '.toggle-user-role', function() {
        const userId = $(this).data('id');
        const currentRole = $(this).data('role');
        const newRole = currentRole === 'admin' ? 'usuario normal' : 'administrador';
        
        showConfirmModal(
            `¿Estás seguro de que deseas cambiar este usuario a ${newRole}?`,
            () => toggleUserRole(userId, currentRole)
        );
    });
    
    // === GESTIÓN DE USUARIOS ===
    
    // Mostrar formulario de nuevo usuario
    $('#showUserFormBtn').on('click', function() {
        showUserForm();
    });
    
    // Formulario de usuario
    $('#userForm').on('submit', function(e) {
        e.preventDefault();
        
        const username = $('#newUsername').val().trim();
        const email = $('#newUserEmail').val().trim();
        const password = $('#newUserPassword').val();
        const role = $('#newUserRole').val();
        
        if (username && email && password && role) {
            createUser(username, email, password, role);
        }
    });
    
    // Formulario de edición de usuario
    $('#editUserForm').on('submit', function(e) {
        e.preventDefault();
        
        const userId = $('#editUserId').val();
        const username = $('#editUsername').val().trim();
        const email = $('#editUserEmail').val().trim();
        const password = $('#editUserPassword').val();
        const role = $('#editUserRole').val();
        
        if (username && email && role) {
            const userData = {
                username: username,
                email: email,
                role: role
            };
            
            // Solo incluir password si se proporcionó
            if (password && password.length >= 6) {
                userData.password = password;
            }
            
            updateUser(userId, userData);
        }
    });
    
    // Cancelar edición de usuario
    $('#cancelEditUserBtn').on('click', hideEditUserForm);
    
    // Cancelar formulario de usuario
    $('#cancelUserBtn').on('click', hideUserForm);
});

// ============================================================================
// FUNCIONES EXPUESTAS GLOBALMENTE (para depuración)
// ============================================================================

window.StoreApp = {
    getAppState: () => app,
    forceLogout: logout,
    reloadStores: () => loadStores(app.currentPage, app.currentPerPage),
    showNotification: showNotification
};
