// Global variables
let currentUser = null;
let currentPage = 1;
let totalPages = 1;

// Initialize application
console.log('Script loaded');

// Utility functions
function openModal(modalId) {
    console.log('Opening modal:', modalId);
    const modal = $('#' + modalId);
    console.log('Modal element found:', modal.length > 0);
    
    if (modal.length) {
        modal.addClass('active');
        $('body').addClass('modal-open');
        
        // Reinitialize Lucide icons in the modal
        setTimeout(() => {
            lucide.createIcons();
            modal.find('input:first').focus();
        }, 100);
        
        console.log('Modal opened successfully');
    } else {
        console.error('Modal not found:', modalId);
    }
}

function closeModal(modalId) {
    console.log('Closing modal:', modalId);
    const modal = $('#' + modalId);
    if (modal.length) {
        modal.removeClass('active');
        $('body').removeClass('modal-open');
        console.log('Modal closed successfully');
    }
}

// Initialize dropdowns - SIMPLIFIED VERSION
function initializeDropdowns() {
    console.log('Simple dropdown initialization (legacy function - not used)');
    // This function is kept for compatibility but not used
    // The real dropdown initialization happens in $(document).ready()
}

// Initialize modals
function initializeModals() {
    $(document).on('click', '.modal', function(e) {
        if (e.target === this) {
            closeModal($(this).attr('id'));
        }
    });
    
    $(document).on('click', '[data-dismiss="modal"]', function() {
        const modal = $(this).closest('.modal');
        closeModal(modal.attr('id'));
    });
    
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('.modal.show').each(function() {
                closeModal($(this).attr('id'));
            });
        }
    });
}

function initializeLucideIcons() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Initialize notifications
function initializeNotifications() {
    if (!$('#toast-container').length) {
        $('body').append('<div id="toast-container" class="toast-container"></div>');
    }
}

// Authentication functions
function initializeAuth() {
    console.log('Initializing auth...');
    
    // Login form handler
    $('#loginFormElement').on('submit', function(e) {
        e.preventDefault();
        
        const username = $('#loginIdentifier').val().trim();
        const password = $('#loginPassword').val();
        
        if (!username || !password) {
            showNotification('Por favor completa todos los campos', 'warning');
            return;
        }
        
        login(username, password);
    });
    
    // Register form handler
    $('#registerFormElement').on('submit', function(e) {
        e.preventDefault();
        
        const username = $('#registerUsername').val().trim();
        const email = $('#registerEmail').val().trim();
        const password = $('#registerPassword').val();
        const confirmPassword = $('#confirmPassword').val();
        
        if (!username || !email || !password || !confirmPassword) {
            showNotification('Por favor completa todos los campos', 'warning');
            return;
        }
        
        if (password !== confirmPassword) {
            showNotification('Las contraseñas no coinciden', 'warning');
            return;
        }
        
        register(username, email, password);
    });
    
    // Switch between forms
    $('#switchToRegister').on('click', function() {
        $('#loginForm').addClass('hidden');
        $('#registerForm').removeClass('hidden');
    });
    
    $('#switchToLogin').on('click', function() {
        $('#registerForm').addClass('hidden');
        $('#loginForm').removeClass('hidden');
    });
    
    $(document).on('click', '#logoutBtn', logout);
    
    console.log('Auth initialized');
}

// Show notifications
function showNotification(message, type = 'info') {
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div class="toast toast-${type}" id="${toastId}">
            <div class="toast-body">
                <i data-lucide="${getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button type="button" class="toast-close" onclick="closeNotification('${toastId}')">
                    <i data-lucide="x"></i>
                </button>
            </div>
        </div>
    `;
    
    $('#toast-container').append(toastHtml);
    lucide.createIcons();
    
    // Show toast
    setTimeout(() => {
        $('#' + toastId).addClass('show');
    }, 100);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        closeNotification(toastId);
    }, 5000);
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'x-circle';
        case 'warning': return 'alert-triangle';
        default: return 'info';
    }
}

function closeNotification(toastId) {
    const toast = $('#' + toastId);
    toast.removeClass('show');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

// Check authentication
function checkAuthStatus() {
    console.log('=== Checking authentication status ===');
    
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.log('No token found, showing login');
        showUnauthenticatedView();
        return;
    }
    
    console.log('Token found, verifying with server...');
    
    // Verify token with server
    $.ajax({
        url: '/api/users/verify-token',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            console.log('Token valid, user authenticated:', response);
            currentUser = response.data;
            showAuthenticatedView();
            loadStores();
        },
        error: function(xhr) {
            console.log('Token invalid, removing and showing login');
            console.error('Token verification error:', xhr);
            localStorage.removeItem('token');
            currentUser = null;
            showUnauthenticatedView();
        }
    });
}

// Login
function login(username, password) {
    console.log('Attempting login...');
    $.ajax({
        url: '/api/users/login',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            identifier: username,
            password: password
        }),
        success: function(response) {
            console.log('Login successful:', response);
            localStorage.setItem('token', response.data.access_token);
            currentUser = response.data;
            
            showNotification('¡Bienvenido de vuelta!', 'success');
            showAuthenticatedView();
            loadStores();
        },
        error: function(xhr) {
            const message = xhr.responseJSON?.message || 'Error al iniciar sesión';
            showNotification(message, 'error');
        }
    });
}

// Register
function register(username, email, password) {
    $.ajax({
        url: '/api/users/register',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            email: email,
            password: password
        }),
        success: function(response) {
            showNotification('Cuenta creada exitosamente. Por favor inicia sesión.', 'success');
            $('#registerForm').addClass('hidden');
            $('#loginForm').removeClass('hidden');
        },
        error: function(xhr) {
            const message = xhr.responseJSON?.message || 'Error al registrar usuario';
            showNotification(message, 'error');
        }
    });
}

// Logout
function logout() {
    console.log('Logout function called');
    localStorage.removeItem('token');
    currentUser = null;
    showNotification('Sesión cerrada', 'info');
    showUnauthenticatedView();
}

// Show authenticated view
function showAuthenticatedView() {
    console.log('=== Showing authenticated view ===');
    console.log('Current user:', currentUser);
    
    // Hide auth panel, show main panel
    $('#authPanel').addClass('hidden').hide();
    $('#mainPanel').removeClass('hidden').show();
    
    // Hide guest navigation (login/register buttons)
    $('#guestNav').addClass('hidden').hide();
    
    if (currentUser) {
        // Update user info in navigation
        $('#welcomeUser').text(`Bienvenido, ${currentUser.username}`);
        $('#userRole').text(currentUser.role.toUpperCase()).removeClass('hidden');
        
        // Show navigation bar
        console.log('Showing user navigation bar');
        $('#userNav').removeClass('hidden').show();
        
        // Ensure logout button is visible and working
        $('#logoutBtn').show();
        
        // Show admin-only elements based on role
        if (currentUser.role === 'admin') {
            console.log('Showing admin elements');
            $('.admin-only').removeClass('hidden').show();
        } else {
            console.log('Hiding admin elements');
            $('.admin-only').addClass('hidden').hide();
        }
        
        // Initialize tab navigation
        console.log('Initializing tab navigation...');
        initializeTabNavigation();
        
        // Navigate to stores tab by default
        navigateToTab('stores');
        
        // Initialize event handlers after DOM changes
        console.log('Re-initializing event handlers...');
        initializePostLoginHandlers();
        
        // Refresh Lucide icons for the new navigation
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } else {
        console.error('No current user found');
    }
}

// Initialize handlers after login
function initializePostLoginHandlers() {
    console.log('Initializing post-login handlers...');
    
    // Store form handlers
    $('#showStoreFormBtn').off('click').on('click', function() {
        console.log('=== Show store form button clicked ===');
        console.log('Current user:', currentUser);
        console.log('Token exists:', !!localStorage.getItem('token'));
        
        // Reset form
        $('#storeForm')[0].reset();
        
        // Show the store form
        $('#storeFormContainer').removeClass('hidden');
        $('#storesPanel').addClass('hidden');
        
        console.log('Store form should now be visible');
    });
    
    // Cancel store form button
    $('#cancelBtn').off('click').on('click', function() {
        console.log('Cancel button clicked');
        $('#storeFormContainer').addClass('hidden');
        $('#storesPanel').removeClass('hidden');
        $('#storeForm')[0].reset();
    });
    
    // Store form submission
    $('#storeForm').off('submit').on('submit', function(e) {
        e.preventDefault();
        console.log('Store form submitted');
        
        const storeArea = parseFloat($('#storeArea').val());
        const itemsAvailable = parseInt($('#itemsAvailable').val());
        const dailyCustomers = parseInt($('#dailyCustomerCount').val());
        const storeSales = parseFloat($('#storeSales').val());
        
        // Validate data
        if (isNaN(storeArea) || isNaN(itemsAvailable) || isNaN(dailyCustomers) || isNaN(storeSales)) {
            showNotification('Por favor completa todos los campos con valores válidos', 'warning');
            return;
        }
        
        if (storeArea <= 0 || itemsAvailable < 0 || dailyCustomers < 0 || storeSales < 0) {
            showNotification('Los valores deben ser positivos', 'warning');
            return;
        }
        
        const token = localStorage.getItem('token');
        const storeData = {
            store_area: storeArea,
            items_available: itemsAvailable,
            daily_customer_count: dailyCustomers,
            store_sales: storeSales
        };
        
        console.log('Creating store with data:', storeData);
        
        $.ajax({
            url: '/api/stores',
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(storeData),
            success: function(response) {
                console.log('Store created successfully:', response);
                showNotification('Tienda creada exitosamente', 'success');
                $('#storeFormContainer').addClass('hidden');
                $('#storesPanel').removeClass('hidden');
                $('#storeForm')[0].reset();
                // Reload stores to show the new one
                loadStores(currentPage);
            },
            error: function(xhr) {
                console.error('Error creating store:', xhr);
                const message = xhr.responseJSON?.message || 'Error al crear la tienda';
                showNotification(message, 'error');
            }
        });
    });
    
    // User form handlers  
    $('#showUserFormBtn').off('click').on('click', function() {
        console.log('Show user form button clicked');
        $('#userFormContainer').toggleClass('hidden');
        if (!$('#userFormContainer').hasClass('hidden')) {
            $('#newUsername').focus();
        }
    });
    
    // Pagination handlers
    $('#firstPageBtn').off('click').on('click', function() {
        console.log('First page button clicked');
        if (currentPage > 1) {
            loadStores(1);
        }
    });
    
    $('#prevPageBtn').off('click').on('click', function() {
        console.log('Previous page button clicked');
        if (currentPage > 1) {
            loadStores(currentPage - 1);
        }
    });
    
    $('#nextPageBtn').off('click').on('click', function() {
        console.log('Next page button clicked');
        if (currentPage < totalPages) {
            loadStores(currentPage + 1);
        }
    });
    
    $('#lastPageBtn').off('click').on('click', function() {
        console.log('Last page button clicked');
        if (currentPage < totalPages) {
            loadStores(totalPages);
        }
    });
    
    // Search and filter handlers with debounce
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    const debouncedSearch = debounce(performSearch, 300);
    
    $('#storeSearchInput').off('input').on('input', function() {
        console.log('Search input changed:', $(this).val());
        const query = $(this).val().trim();
        debouncedSearch(query);
    });
    
    $('#clearSearchBtn').off('click').on('click', function() {
        console.log('Clear search button clicked');
        $('#storeSearchInput').val('');
        performSearch('');
    });
    
    $('#sortFilter').off('change').on('change', function() {
        console.log('Sort filter changed:', $(this).val());
        loadStores(1);
    });
    
    $('#resetFiltersBtn').off('click').on('click', function() {
        console.log('Reset filters button clicked');
        $('#storeSearchInput').val('');
        $('#sortFilter').val('store_id_asc');
        loadStores(1);
    });
    
    $('#fetchStoresBtn').off('click').on('click', function() {
        console.log('Fetch stores button clicked');
        loadStores(currentPage);
    });
    
    $('#exportCSVBtn').off('click').on('click', function() {
        console.log('Export CSV button clicked');
        exportStoresToCSV();
    });
    
    $('#perPageSelect').off('change').on('change', function() {
        console.log('Per page select changed:', $(this).val());
        loadStores(1);
    });
    
    console.log('Post-login handlers initialized');
}

// Show unauthenticated view
function showUnauthenticatedView() {
    console.log('=== Showing unauthenticated view ===');
    
    // Show login panel, hide main panel
    $('#authPanel').removeClass('hidden').show();
    $('#mainPanel').addClass('hidden').hide();
    
    // Show guest navigation (login/register buttons)
    $('#guestNav').removeClass('hidden').show();
    
    // Hide user navigation completely
    $('#userNav').addClass('hidden').hide();
    $('#logoutBtn').hide();
    
    // Clear content
    $('#storeList').empty();
    $('.admin-only').hide();
    
    // Reset forms
    $('#loginFormElement')[0]?.reset();
    $('#registerFormElement')[0]?.reset();
    
    // Ensure login form is visible (not register)
    $('#loginForm').removeClass('hidden');
    $('#registerForm').addClass('hidden');
    
    console.log('Login view ready');
}

// Load stores
function loadStores(page = 1, perPage = null) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        showUnauthenticatedView();
        return;
    }
    
    // Use the selected value from perPageSelect if not provided
    if (perPage === null) {
        perPage = parseInt($('#perPageSelect').val()) || 10;
    }
    
    // Get search query
    const searchQuery = $('#storeSearchInput').val().trim();
    
    // Get sort parameters
    const sortValue = $('#sortFilter').val() || 'store_id_asc';
    const [sortBy, sortOrder] = sortValue.split('_').reduce((acc, part, idx, arr) => {
        if (idx === arr.length - 1) {
            acc[1] = part; // last part is order (asc/desc)
        } else {
            acc[0] = acc[0] ? `${acc[0]}_${part}` : part; // build field name
        }
        return acc;
    }, ['', 'asc']);
    
    $('#storeList').html(`
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p>Cargando tiendas...</p>
        </div>
    `);
    
    const params = {
        page: page,
        per_page: perPage
    };
    
    if (searchQuery) {
        params.search = searchQuery;
    }
    
    if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
    }
    
    $.ajax({
        url: '/api/stores',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        data: params,
        success: function(response) {
            console.log('Stores loaded:', response);
            
            // El backend devuelve stores en response.stores
            const stores = response.stores || response.data || [];
            currentPage = response.pagination?.page || page;
            totalPages = response.pagination?.total_pages || Math.ceil((response.pagination?.total || 0) / perPage);
            
            renderStores(stores);
            updatePaginationInfo(response);
        },
        error: function(xhr) {
            console.error('Error loading stores:', xhr);
            if (xhr.status === 401) {
                console.log('Authentication error, redirecting to login');
                localStorage.removeItem('token');
                currentUser = null;
                showUnauthenticatedView();
                showNotification('Sesión expirada. Por favor inicia sesión nuevamente.', 'warning');
            } else {
                console.log('Non-auth error, keeping session');
                showNotification('Error al cargar las tiendas', 'error');
            }
        }
    });
}

// Render stores
function renderStores(stores) {
    if (!stores || stores.length === 0) {
        $('#storeList').html(`
            <div class="empty-state">
                <i data-lucide="store"></i>
                <h3>No hay tiendas disponibles</h3>
                <p>No se encontraron tiendas para mostrar</p>
            </div>
        `);
        lucide.createIcons();
        return;
    }
    
    const storeCards = stores.map(store => createStoreCard(store)).join('');
    $('#storeList').html(storeCards);
    lucide.createIcons();
    
    // Initialize dropdowns for store cards
    console.log('Initializing store card dropdowns...');
    $('.store-card .dropdown-toggle').off('click').on('click', function(e) {
        console.log('Store card dropdown clicked');
        e.preventDefault();
        e.stopPropagation();
        
        const dropdown = $(this).closest('.dropdown');
        const isOpen = dropdown.hasClass('active');
        
        // Close all dropdowns
        $('.store-card .dropdown').removeClass('active');
        
        // Toggle this one
        if (!isOpen) {
            dropdown.addClass('active');
        }
    });
    
    // Close store card dropdowns when clicking outside
    $(document).off('click.storecards').on('click.storecards', function(e) {
        if (!$(e.target).closest('.store-card .dropdown').length) {
            $('.store-card .dropdown').removeClass('active');
        }
    });
}

// Create store card
function createStoreCard(store) {
    const isAdmin = currentUser && currentUser.role === 'admin';
    
    return `
        <div class="store-card" data-store-id="${store.store_id}">
            <div class="store-card-header">
                <h3 class="store-title">Tienda #${store.store_id}</h3>
                <span class="store-area">Área: ${store.store_area} m²</span>
                ${isAdmin ? `
                    <div class="store-actions">
                        <div class="dropdown">
                            <button class="btn btn-icon dropdown-toggle" type="button">
                                <i data-lucide="more-vertical"></i>
                            </button>
                            <div class="dropdown-menu">
                                <button class="dropdown-item" onclick="editStore(${store.store_id})">
                                    <i data-lucide="edit"></i>
                                    Editar
                                </button>
                                <button class="dropdown-item text-danger" onclick="deleteStore(${store.store_id})">
                                    <i data-lucide="trash-2"></i>
                                    Eliminar
                                </button>
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
            
            <div class="store-card-body">
                <div class="store-stats">
                    <div class="stat">
                        <i data-lucide="package"></i>
                        <span class="stat-label">Items Disponibles</span>
                        <span class="stat-value">${store.items_available || 0}</span>
                    </div>
                    <div class="stat">
                        <i data-lucide="users"></i>
                        <span class="stat-label">Clientes Diarios</span>
                        <span class="stat-value">${store.daily_customer_count || 0}</span>
                    </div>
                    <div class="stat">
                        <i data-lucide="dollar-sign"></i>
                        <span class="stat-label">Ventas</span>
                        <span class="stat-value">$${(store.store_sales || 0).toFixed(2)}</span>
                    </div>
                </div>
                
                <div class="store-card-footer">
                    <span class="store-id">ID: ${store.store_id}</span>
                    <button class="btn btn-outline btn-sm" onclick="showStoreDetails(${store.store_id})">
                        <i data-lucide="eye"></i>
                        Ver detalles
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Edit store
function editStore(storeId) {
    console.log('=== editStore called with ID:', storeId);
    const token = localStorage.getItem('token');
    
    if (!currentUser || !currentUser.role || currentUser.role !== 'admin') {
        showNotification('Solo los administradores pueden editar tiendas', 'warning');
        return;
    }
    
    // First, get current store data
    $.ajax({
        url: `/api/stores/${storeId}`,
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            console.log('Store data received:', response);
            showEditStoreModal(response.data || response);
        },
        error: function(xhr) {
            const message = xhr.responseJSON?.message || 'Error al cargar datos de la tienda';
            showNotification(message, 'error');
            console.error('Error loading store data:', xhr);
        }
    });
}

// Show edit store modal
function showEditStoreModal(store) {
    console.log('=== showEditStoreModal called ===');
    console.log('Showing edit modal for store:', store);
    
    // Populate form with current store data
    $('#editStoreId').val(store.store_id);
    $('#editStoreArea').val(store.store_area || '');
    $('#editItemsAvailable').val(store.items_available || '');
    $('#editDailyCustomers').val(store.daily_customer_count || '');
    $('#editStoreSales').val(store.store_sales || '');
    
    // Show modal
    openModal('editStoreModal');
    
    // Ensure save button handler is attached
    $('#saveStoreBtn').off('click').on('click', function(e) {
        console.log('💾 Save store button clicked from modal');
        e.preventDefault();
        e.stopPropagation();
        saveStoreChanges();
    });
    
    // Debug: Check if button exists
    console.log('Save button exists:', $('#saveStoreBtn').length > 0);
    console.log('Save button visible:', $('#saveStoreBtn').is(':visible'));
}

// Save store changes
function saveStoreChanges() {
    console.log('=== saveStoreChanges called ===');
    
    const storeId = $('#editStoreId').val();
    const storeArea = parseFloat($('#editStoreArea').val());
    const itemsAvailable = parseInt($('#editItemsAvailable').val());
    const dailyCustomers = parseInt($('#editDailyCustomers').val());
    const storeSales = parseFloat($('#editStoreSales').val());
    
    // Validate data
    if (!storeId || isNaN(storeArea) || isNaN(itemsAvailable) || isNaN(dailyCustomers) || isNaN(storeSales)) {
        showNotification('Por favor completa todos los campos con valores válidos', 'warning');
        return;
    }
    
    if (storeArea <= 0 || itemsAvailable < 0 || dailyCustomers < 0 || storeSales < 0) {
        showNotification('Los valores deben ser positivos', 'warning');
        return;
    }
    
    const token = localStorage.getItem('token');
    const updateData = {
        store_area: storeArea,
        items_available: itemsAvailable,
        daily_customer_count: dailyCustomers,
        store_sales: storeSales
    };
    
    console.log('Sending update data:', updateData);
    
    $.ajax({
        url: `/api/stores/${storeId}`,
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(updateData),
        success: function(response) {
            console.log('Store updated successfully:', response);
            showNotification('Tienda actualizada exitosamente', 'success');
            closeModal('editStoreModal');
            // Reload stores to show updated data
            loadStores(currentPage);
        },
        error: function(xhr) {
            console.error('Error updating store:', xhr);
            const message = xhr.responseJSON?.message || 'Error al actualizar la tienda';
            showNotification(message, 'error');
        }
    });
}

// Make functions globally available
window.editStore = editStore;
window.deleteStore = deleteStore;
window.showStoreDetails = showStoreDetails;

// Performance search with filters
function performSearch(query = '') {
    console.log('Performing search with query:', query);
    
    // Reset to page 1 and load stores with search parameter
    currentPage = 1;
    loadStores(1);
}

function loadStoresWithParams(queryString) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        showUnauthenticatedView();
        return;
    }
    
    $.ajax({
        url: '/api/stores?' + queryString,
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            console.log('Stores loaded with params:', response);
            
            // El backend devuelve stores en response.stores
            const stores = response.stores || response.data || [];
            renderStores(stores);
            updatePaginationInfo(response);
        },
        error: function(xhr) {
            const message = xhr.responseJSON?.message || 'Error al cargar las tiendas';
            showNotification(message, 'error');
        }
    });
}

// Update pagination info
function updatePaginationInfo(response) {
    console.log('Updating pagination with response:', response);
    
    // El backend devuelve la paginación en response.pagination
    const pagination = response.pagination || {};
    const total = pagination.total || 0;
    const page = pagination.page || currentPage;
    const perPage = pagination.per_page || 10;
    const totalPages = pagination.total_pages || Math.ceil(total / perPage);
    
    currentPage = page;
    totalPages = totalPages;
    
    console.log(`Pagination: page=${page}, totalPages=${totalPages}, total=${total}`);
    
    $('#currentPageBtn').text(`Página ${page}`);
    $('#paginationInfo').text(`Mostrando ${Math.min(perPage, total)} de ${total} tiendas`);
    
    // Update button states - Solo deshabilitar si realmente es la primera/última página
    const isFirstPage = page <= 1;
    const isLastPage = page >= totalPages || totalPages <= 1;
    
    console.log(`Button states: isFirstPage=${isFirstPage}, isLastPage=${isLastPage}`);
    
    $('#firstPageBtn, #prevPageBtn').prop('disabled', isFirstPage);
    $('#nextPageBtn, #lastPageBtn').prop('disabled', isLastPage);
}

// Placeholder functions for other features
function deleteStore(storeId) {
    console.log('=== deleteStore called with ID:', storeId);
    const token = localStorage.getItem('token');
    
    if (!currentUser || !currentUser.role || currentUser.role !== 'admin') {
        showNotification('Solo los administradores pueden eliminar tiendas', 'warning');
        return;
    }
    
    // Cerrar dropdown si está abierto
    $('.store-card .dropdown').removeClass('active');
    
    // Mostrar modal de confirmación
    $('#deleteStoreId').text(storeId);
    $('#deleteStoreModal').addClass('active');
    
    // Remover event listeners previos para evitar duplicados
    $('#confirmDeleteBtn').off('click');
    
    // Event listener para confirmar eliminación
    $('#confirmDeleteBtn').on('click', function() {
        console.log('Confirming deletion of store:', storeId);
        
        // Desactivar botón mientras se procesa
        $(this).prop('disabled', true).html('<div class="loading-spinner small"></div> Eliminando...');
        
        $.ajax({
            url: `/api/stores/${storeId}`,
            method: 'DELETE',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                console.log('Store deleted successfully:', response);
                $('#deleteStoreModal').removeClass('active');
                showNotification('Tienda eliminada exitosamente', 'success');
                
                // Recargar la lista de tiendas
                currentPage = 1;
                loadStores(currentPage);
                
                // Restaurar botón
                $('#confirmDeleteBtn').prop('disabled', false).html('<i data-lucide="trash-2"></i> <span>Eliminar</span>');
                lucide.createIcons();
            },
            error: function(xhr) {
                console.error('Error deleting store:', xhr);
                const message = xhr.responseJSON?.message || 'Error al eliminar la tienda';
                showNotification(message, 'error');
                
                // Restaurar botón
                $('#confirmDeleteBtn').prop('disabled', false).html('<i data-lucide="trash-2"></i> <span>Eliminar</span>');
                lucide.createIcons();
            }
        });
    });
    
    // Inicializar iconos de Lucide en el modal
    lucide.createIcons();
}

function showStoreDetails(storeId) {
    console.log('showStoreDetails called with ID:', storeId);
    // Implementation here
}

function loadUsers() {
    console.log('=== Loading users ===');
    const token = localStorage.getItem('token');
    
    if (!token) {
        showUnauthenticatedView();
        return;
    }
    
    $.ajax({
        url: '/api/users/',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            console.log('Users loaded:', response);
            renderUsers(response.data || response.users || []);
        },
        error: function(xhr) {
            console.error('Error loading users:', xhr);
            const message = xhr.responseJSON?.message || 'Error al cargar usuarios';
            showNotification(message, 'error');
        }
    });
}

// Render users table
function renderUsers(users) {
    console.log('Rendering users:', users);
    
    if (!users || users.length === 0) {
        $('#usersList').html(`
            <div class="empty-state">
                <i data-lucide="users"></i>
                <h3>No hay usuarios</h3>
                <p>No se encontraron usuarios en el sistema</p>
            </div>
        `);
        lucide.createIcons();
        return;
    }
    
    const usersTable = `
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Usuario</th>
                        <th>Email</th>
                        <th>Rol</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.id}</td>
                            <td>
                                <div class="user-cell">
                                    <i data-lucide="user"></i>
                                    <span>${user.username}</span>
                                </div>
                            </td>
                            <td>${user.email}</td>
                            <td>
                                <span class="badge ${user.role === 'admin' ? 'badge-primary' : 'badge-secondary'}">
                                    ${user.role === 'admin' ? 'Administrador' : 'Usuario'}
                                </span>
                            </td>
                            <td>
                                <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                                    ${user.is_active ? 'Activo' : 'Inactivo'}
                                </span>
                            </td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn btn-sm btn-outline" onclick="toggleUserStatus(${user.id}, ${user.is_active})" title="${user.is_active ? 'Desactivar' : 'Activar'}">
                                        <i data-lucide="${user.is_active ? 'user-x' : 'user-check'}"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline" onclick="changeUserRole(${user.id}, '${user.role}')" title="Cambiar rol">
                                        <i data-lucide="shield"></i>
                                    </button>
                                    ${user.id !== currentUser.id ? `
                                        <button class="btn btn-sm btn-destructive" onclick="deleteUser(${user.id})" title="Eliminar">
                                            <i data-lucide="trash-2"></i>
                                        </button>
                                    ` : ''}
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    $('#usersList').html(usersTable);
    lucide.createIcons();
}

// Toggle user status
function toggleUserStatus(userId, currentStatus) {
    console.log('=== Toggling user status ===', userId, currentStatus);
    const token = localStorage.getItem('token');
    
    const action = currentStatus ? 'desactivar' : 'activar';
    if (!confirm(`¿Estás seguro de que quieres ${action} este usuario?`)) {
        return;
    }
    
    $.ajax({
        url: `/api/users/${userId}/toggle-status`,
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            console.log('User status toggled:', response);
            showNotification(`Usuario ${action}do exitosamente`, 'success');
            loadUsers(); // Reload users
        },
        error: function(xhr) {
            console.error('Error toggling user status:', xhr);
            const message = xhr.responseJSON?.message || 'Error al cambiar estado del usuario';
            showNotification(message, 'error');
        }
    });
}

// Load statistics
function loadStatistics() {
    console.log('=== Loading statistics ===');
    const token = localStorage.getItem('token');
    
    $('#statsContent').html(`
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p>Cargando estadísticas...</p>
        </div>
    `);
    
    $.ajax({
        url: '/api/stores/stats',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            console.log('Statistics loaded:', response);
            renderStatistics(response.data);
        },
        error: function(xhr) {
            console.error('Error loading statistics:', xhr);
            const message = xhr.responseJSON?.message || 'Error al cargar estadísticas';
            showNotification(message, 'error');
            $('#statsContent').html(`
                <div class="empty-state">
                    <i data-lucide="alert-circle"></i>
                    <h3>Error al cargar estadísticas</h3>
                    <p>${message}</p>
                </div>
            `);
            lucide.createIcons();
        }
    });
}

// Render statistics
function renderStatistics(stats) {
    console.log('=== Rendering statistics ===', stats);
    
    if (!stats) {
        $('#statsContent').html(`
            <div class="empty-state">
                <i data-lucide="alert-circle"></i>
                <h3>No hay datos disponibles</h3>
                <p>No se pudieron cargar las estadísticas</p>
            </div>
        `);
        lucide.createIcons();
        return;
    }
    
    const statsHTML = `
        <div class="stats-cards">
            <div class="stat-card stat-card-primary">
                <div class="stat-icon">
                    <i data-lucide="store"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">${stats.total_stores || 0}</div>
                    <div class="stat-label">Total Tiendas</div>
                </div>
            </div>
            
            <div class="stat-card stat-card-success">
                <div class="stat-icon">
                    <i data-lucide="dollar-sign"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">$${(stats.sales?.total || 0).toLocaleString('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    <div class="stat-label">Ventas Totales</div>
                </div>
            </div>
            
            <div class="stat-card stat-card-info">
                <div class="stat-icon">
                    <i data-lucide="trending-up"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">$${(stats.sales?.average || 0).toLocaleString('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    <div class="stat-label">Promedio de Ventas</div>
                </div>
            </div>
            
            <div class="stat-card stat-card-warning">
                <div class="stat-icon">
                    <i data-lucide="users"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">${(stats.averages?.daily_customers || 0).toFixed(0)}</div>
                    <div class="stat-label">Promedio Clientes Diarios</div>
                </div>
            </div>
        </div>
        
        <div class="stats-details">
            <div class="stats-section">
                <h3 class="stats-section-title">
                    <i data-lucide="bar-chart"></i>
                    Promedios Generales
                </h3>
                <div class="stats-table">
                    <div class="stats-row">
                        <div class="stats-row-label">
                            <i data-lucide="maximize"></i>
                            Área Promedio
                        </div>
                        <div class="stats-row-value">${(stats.averages?.store_area || 0).toFixed(2)} m²</div>
                    </div>
                    <div class="stats-row">
                        <div class="stats-row-label">
                            <i data-lucide="package"></i>
                            Artículos Promedio
                        </div>
                        <div class="stats-row-value">${(stats.averages?.items_available || 0).toFixed(0)} items</div>
                    </div>
                    <div class="stats-row">
                        <div class="stats-row-label">
                            <i data-lucide="users"></i>
                            Clientes Promedio
                        </div>
                        <div class="stats-row-value">${(stats.averages?.daily_customers || 0).toFixed(0)} clientes/día</div>
                    </div>
                    <div class="stats-row">
                        <div class="stats-row-label">
                            <i data-lucide="dollar-sign"></i>
                            Ventas Promedio
                        </div>
                        <div class="stats-row-value">$${(stats.averages?.store_sales || 0).toLocaleString('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    </div>
                </div>
            </div>
            
            <div class="stats-section">
                <h3 class="stats-section-title">
                    <i data-lucide="trending-up"></i>
                    Análisis de Ventas
                </h3>
                <div class="stats-table">
                    <div class="stats-row stats-row-highlight">
                        <div class="stats-row-label">
                            <i data-lucide="arrow-up"></i>
                            Ventas Máximas
                        </div>
                        <div class="stats-row-value stats-value-success">$${(stats.sales?.maximum || 0).toLocaleString('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    </div>
                    <div class="stats-row">
                        <div class="stats-row-label">
                            <i data-lucide="arrow-down"></i>
                            Ventas Mínimas
                        </div>
                        <div class="stats-row-value stats-value-warning">$${(stats.sales?.minimum || 0).toLocaleString('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    </div>
                    <div class="stats-row">
                        <div class="stats-row-label">
                            <i data-lucide="activity"></i>
                            Rango de Ventas
                        </div>
                        <div class="stats-row-value">$${((stats.sales?.maximum || 0) - (stats.sales?.minimum || 0)).toLocaleString('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('#statsContent').html(statsHTML);
    lucide.createIcons();
    
    // Render charts after stats are loaded
    setTimeout(() => {
        renderSalesChart(stats);
        renderDistributionChart(stats);
        renderTrendsChart(stats);
    }, 100);
}

// Change user role
function changeUserRole(userId, currentRole) {
    console.log('=== Changing user role ===', userId, currentRole);
    const token = localStorage.getItem('token');
    
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    const roleText = newRole === 'admin' ? 'administrador' : 'usuario regular';
    
    if (!confirm(`¿Estás seguro de que quieres cambiar este usuario a ${roleText}?`)) {
        return;
    }
    
    $.ajax({
        url: `/api/users/${userId}/role`,
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({ role: newRole }),
        success: function(response) {
            console.log('User role changed:', response);
            showNotification('Rol de usuario actualizado exitosamente', 'success');
            loadUsers();
        },
        error: function(xhr) {
            console.error('Error changing user role:', xhr);
            const message = xhr.responseJSON?.message || 'Error al cambiar rol del usuario';
            showNotification(message, 'error');
        }
    });
}

// Delete user
function deleteUser(userId) {
    console.log('=== Deleting user ===', userId);
    const token = localStorage.getItem('token');
    
    if (!confirm('¿Estás seguro de que quieres eliminar este usuario? Esta acción no se puede deshacer.')) {
        return;
    }
    
    $.ajax({
        url: `/api/users/${userId}`,
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            console.log('User deleted:', response);
            showNotification('Usuario eliminado exitosamente', 'success');
            loadUsers();
        },
        error: function(xhr) {
            console.error('Error deleting user:', xhr);
            const message = xhr.responseJSON?.message || 'Error al eliminar usuario';
            showNotification(message, 'error');
        }
    });
}

// Make functions globally available
window.toggleUserStatus = toggleUserStatus;
window.changeUserRole = changeUserRole;
window.deleteUser = deleteUser;

// Initialize everything when document is ready
$(document).ready(function() {
    console.log('Document ready - initializing app...');
    console.log('jQuery version:', $.fn.jquery);
    
    // Test basic jQuery functionality
    console.log('Testing basic jQuery...');
    $('body').append('<div id="test-jquery" style="display:none;">jQuery works</div>');
    console.log('jQuery test element exists:', $('#test-jquery').length > 0);
    $('#test-jquery').remove();
    
    initializeAuth();
    initializeLucideIcons();
    initializeNotifications();
    initializeModals();
    checkAuthStatus();
    
    // Initialize dropdowns with a simple, direct approach
    setTimeout(() => {
        console.log('=== SETTING UP SIMPLE DROPDOWN ===');
        
        // Remove all existing handlers
        $('#userDropdown').off();
        $(document).off('click.simpledropdown');
        
        // Direct click handler for user dropdown
        $('#userDropdown').on('click', function(e) {
            console.log('🎯 USER DROPDOWN CLICKED - DIRECT HANDLER');
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = $('#dropdownMenu');
            const container = $('.dropdown');
            
            console.log('Dropdown menu found:', dropdown.length);
            console.log('Container found:', container.length);
            
            // Toggle active class on container
            if (container.hasClass('active')) {
                console.log('Closing dropdown');
                container.removeClass('active');
            } else {
                console.log('Opening dropdown');
                container.addClass('active');
            }
        });
        
        // Handlers for dropdown menu items
        $('#storesBtn').on('click', function(e) {
            console.log('🏪 Stores button clicked');
            e.preventDefault();
            $('.dropdown').removeClass('active');
            // Ya estamos en la vista de tiendas por defecto
            showNotification('Ya estás en la gestión de tiendas', 'info');
        });
        
        $('#usersManagementBtn').on('click', function(e) {
            console.log('👥 Users management button clicked');
            e.preventDefault();
            $('.dropdown').removeClass('active');
            if (currentUser && currentUser.role === 'admin') {
                // Show users panel and hide stores panel
                $('#storesPanel').addClass('hidden');
                $('#usersPanel').removeClass('hidden');
                loadUsers();
            } else {
                showNotification('No tienes permisos para gestionar usuarios', 'warning');
            }
        });
        
        $('#statsBtn').on('click', function(e) {
            console.log('📊 Stats button clicked');
            e.preventDefault();
            $('.dropdown').removeClass('active');
            if (currentUser && currentUser.role === 'admin') {
                // Show stats panel and hide other panels
                $('#storesPanel').addClass('hidden');
                $('#usersPanel').addClass('hidden');
                $('#statsPanel').removeClass('hidden');
                loadStatistics();
            } else {
                showNotification('No tienes permisos para ver estadísticas', 'warning');
            }
        });
        
        $('#logoutBtn').on('click', function(e) {
            console.log('🚪 Logout button clicked');
            e.preventDefault();
            $('.dropdown').removeClass('active');
            logout();
        });
        
        // Close dropdown when clicking outside
        $(document).on('click.simpledropdown', function(e) {
            if (!$(e.target).closest('.dropdown').length) {
                console.log('Clicked outside, closing dropdown');
                $('.dropdown').removeClass('active');
            }
        });
        
        // Save store button handler
        $('#saveStoreBtn').on('click', function(e) {
            console.log('💾 Save store button clicked');
            e.preventDefault();
            saveStoreChanges();
        });
        
        console.log('Simple dropdown setup complete');
        
        // Test the elements exist
        console.log('userDropdown element:', $('#userDropdown')[0]);
        console.log('dropdownMenu element:', $('#dropdownMenu')[0]);
        console.log('dropdown container:', $('.dropdown')[0]);
        
    }, 2000); // Wait 2 seconds to ensure DOM is fully loaded
});
// =============================================================================
// CHART.JS FUNCTIONS - Gr�ficos de Estad�sticas
// =============================================================================

// Variables para almacenar instancias de los gr�ficos
let salesChartInstance = null;
let distributionChartInstance = null;
let trendsChartInstance = null;

// Funci�n para renderizar gr�fico de barras de ventas
function renderSalesChart(stats) {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    
    // Destruir gr�fico anterior si existe
    if (salesChartInstance) {
        salesChartInstance.destroy();
    }
    
    // Crear rangos de ventas para el gr�fico
    const ranges = [
        { label: '0-10K', min: 0, max: 10000 },
        { label: '10K-25K', min: 10000, max: 25000 },
        { label: '25K-50K', min: 25000, max: 50000 },
        { label: '50K-100K', min: 50000, max: 100000 },
        { label: '100K+', min: 100000, max: Infinity }
    ];
    
    // Simular distribuci�n basada en estad�sticas
    const total = stats.total_stores || 0;
    const avgSales = stats.sales?.average || 0;
    
    const data = ranges.map((range, index) => {
        if (avgSales < range.max && avgSales >= range.min) {
            return Math.floor(total * 0.4);
        }
        return Math.floor(total * (0.15 / ranges.length));
    });
    
    salesChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ranges.map(r => r.label),
            datasets: [{
                label: 'N�mero de Tiendas',
                data: data,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(168, 85, 247, 0.8)'
                ],
                borderColor: [
                    'rgb(239, 68, 68)',
                    'rgb(245, 158, 11)',
                    'rgb(34, 197, 94)',
                    'rgb(59, 130, 246)',
                    'rgb(168, 85, 247)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + ' tiendas';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Funci�n para renderizar gr�fico de distribuci�n de tiendas
function renderDistributionChart(stats) {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    if (distributionChartInstance) {
        distributionChartInstance.destroy();
    }
    
    const avgArea = stats.averages?.store_area || 0;
    const total = stats.total_stores || 0;
    
    const categories = [
        { label: 'Peque�as (< 100m)', value: Math.floor(total * 0.25) },
        { label: 'Medianas (100-200m)', value: Math.floor(total * 0.45) },
        { label: 'Grandes (200-300m)', value: Math.floor(total * 0.20) },
        { label: 'Extra Grandes (> 300m)', value: Math.floor(total * 0.10) }
    ];
    
    distributionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories.map(c => c.label),
            datasets: [{
                data: categories.map(c => c.value),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(34, 197, 94)',
                    'rgb(245, 158, 11)',
                    'rgb(239, 68, 68)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' tiendas (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Funci�n para renderizar gr�fico de l�neas de tendencias
function renderTrendsChart(stats) {
    const ctx = document.getElementById('trendsChart');
    if (!ctx) return;
    
    if (trendsChartInstance) {
        trendsChartInstance.destroy();
    }
    
    const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    const avgSales = stats.sales?.average || 0;
    const avgCustomers = stats.averages?.daily_customers || 0;
    
    const salesData = months.map((_, i) => {
        const variation = (Math.random() - 0.5) * 0.3;
        return avgSales * (1 + variation);
    });
    
    const customersData = months.map((_, i) => {
        const variation = (Math.random() - 0.5) * 0.3;
        return avgCustomers * (1 + variation);
    });
    
    trendsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Ventas Promedio',
                    data: salesData,
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Clientes Promedio',
                    data: customersData,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 0) {
                                label += '$' + context.parsed.y.toFixed(2);
                            } else {
                                label += context.parsed.y.toFixed(0) + ' clientes';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Ventas ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Clientes'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

// =============================================================================
// EXPORT TO CSV FUNCTION
// =============================================================================

function exportStoresToCSV() {
    console.log('=== Exporting stores to CSV ===');
    const token = localStorage.getItem('token');
    
    if (!currentUser || !currentUser.role || currentUser.role !== 'admin') {
        showNotification('Solo los administradores pueden exportar datos', 'warning');
        return;
    }
    
    // Obtener filtros actuales
    const searchQuery = $('#storeSearchInput').val().trim();
    const minArea = $('#minAreaInput').val();
    const maxArea = $('#maxAreaInput').val();
    const minItems = $('#minItemsInput').val();
    const maxItems = $('#maxItemsInput').val();
    const minCustomers = $('#minCustomersInput').val();
    const maxCustomers = $('#maxCustomersInput').val();
    const minSales = $('#minSalesInput').val();
    const maxSales = $('#maxSalesInput').val();
    
    // Construir URL con par�metros
    let url = '/api/stores/export?';
    const params = [];
    
    if (searchQuery) params.push(`search=${encodeURIComponent(searchQuery)}`);
    if (minArea) params.push(`min_area=${minArea}`);
    if (maxArea) params.push(`max_area=${maxArea}`);
    if (minItems) params.push(`min_items=${minItems}`);
    if (maxItems) params.push(`max_items=${maxItems}`);
    if (minCustomers) params.push(`min_customers=${minCustomers}`);
    if (maxCustomers) params.push(`max_customers=${maxCustomers}`);
    if (minSales) params.push(`min_sales=${minSales}`);
    if (maxSales) params.push(`max_sales=${maxSales}`);
    
    url += params.join('&');
    
    console.log('Export URL:', url);
    
    // Deshabilitar bot�n durante la exportaci�n
    const $btn = $('#exportCSVBtn');
    const originalHTML = $btn.html();
    $btn.prop('disabled', true).html('<div class="loading-spinner small"></div> Exportando...');
    
    // Realizar petici�n para descargar el archivo
    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al exportar datos');
        }
        return response.blob();
    })
    .then(blob => {
        // Crear un enlace temporal para descargar el archivo
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `tiendas_${new Date().getTime()}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        showNotification('Archivo CSV descargado exitosamente', 'success');
        console.log('CSV export successful');
        
        // Restaurar bot�n
        $btn.prop('disabled', false).html(originalHTML);
        lucide.createIcons();
    })
    .catch(error => {
        console.error('Error exporting CSV:', error);
        showNotification('Error al exportar datos a CSV', 'error');
        
        // Restaurar bot�n
        $btn.prop('disabled', false).html(originalHTML);
        lucide.createIcons();
    });
}

// =============================================================================
// NAVEGACI�N POR TABS
// =============================================================================

function initializeTabNavigation() {
    console.log('=== Initializing tab navigation ===');
    
    // Event listeners para los botones del men�
    $('.nav-menu-item').on('click', function(e) {
        e.preventDefault();
        const tab = $(this).data('tab');
        console.log('Tab clicked:', tab);
        
        // Verificar permisos
        if ($(this).hasClass('admin-only') && (!currentUser || currentUser.role !== 'admin')) {
            showNotification('No tienes permisos para acceder a esta secci�n', 'warning');
            return;
        }
        
        // Actualizar estado activo de los tabs
        $('.nav-menu-item').removeClass('active');
        $(this).addClass('active');
        
        // Navegar a la secci�n correspondiente
        navigateToTab(tab);
    });
    
    console.log('Tab navigation initialized');
}

function navigateToTab(tab) {
    console.log('=== Navigating to tab:', tab, '===');
    
    // Actualizar estado activo de los tabs
    $('.nav-menu-item').removeClass('active');
    $(`.nav-menu-item[data-tab="${tab}"]`).addClass('active');
    
    // Ocultar todos los paneles
    $('#storesPanel').addClass('hidden');
    $('#usersPanel').addClass('hidden');
    $('#statsPanel').addClass('hidden');
    
    // Mostrar el panel correspondiente
    switch(tab) {
        case 'stores':
            $('#storesPanel').removeClass('hidden');
            loadStores(currentPage);
            break;
            
        case 'users':
            if (currentUser && currentUser.role === 'admin') {
                $('#usersPanel').removeClass('hidden');
                loadUsers();
            } else {
                showNotification('No tienes permisos para gestionar usuarios', 'warning');
                // Volver al tab de tiendas
                navigateToTab('stores');
                return;
            }
            break;
            
        case 'stats':
            if (currentUser && currentUser.role === 'admin') {
                $('#statsPanel').removeClass('hidden');
                loadStatistics();
            } else {
                showNotification('No tienes permisos para ver estadísticas', 'warning');
                // Volver al tab de tiendas
                navigateToTab('stores');
                return;
            }
            break;
            
        default:
            $('#storesPanel').removeClass('hidden');
            loadStores(currentPage);
    }
    
    // Actualizar iconos de Lucide
    lucide.createIcons();
}
