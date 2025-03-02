// JavaScript لشاشة إدارة العقارات

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos DOM
    const addPropertyBtn = document.getElementById('add-property-btn');
    const addPropertyModal = document.getElementById('add-property-modal');
    const closeAddPropertyModal = document.getElementById('close-add-property');
    const statusModal = document.getElementById('status-modal');
    const closeStatusModal = document.getElementById('close-status-modal');
    const deleteModal = document.getElementById('delete-modal');
    const closeDeleteModal = document.getElementById('close-delete-modal');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const statusSelect = document.getElementById('status-select');
    const confirmStatusBtn = document.getElementById('confirm-status-btn');
    const cancelStatusBtn = document.getElementById('cancel-status-btn');
    const filterSelect = document.getElementById('filter-select');
    const searchInput = document.getElementById('search-input');
    const propertyTable = document.querySelector('.property-table');
    
    let currentPropertyId = null;
    
    // Función para mostrar notificación
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="close-notification">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Mostrar la notificación con animación
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Configurar el cierre de la notificación
        const closeBtn = notification.querySelector('.close-notification');
        closeBtn.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        
        // Cerrar automáticamente después de 5 segundos
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
    
    // Manejadores para el modal de agregar propiedad
    if (addPropertyBtn) {
        addPropertyBtn.addEventListener('click', function() {
            addPropertyModal.classList.add('show');
        });
    }
    
    if (closeAddPropertyModal) {
        closeAddPropertyModal.addEventListener('click', function() {
            addPropertyModal.classList.remove('show');
        });
    }
    
    // Manejadores para el modal de cambio de estado
    if (closeStatusModal) {
        closeStatusModal.addEventListener('click', function() {
            statusModal.classList.remove('show');
        });
    }
    
    if (cancelStatusBtn) {
        cancelStatusBtn.addEventListener('click', function() {
            statusModal.classList.remove('show');
        });
    }
    
    if (confirmStatusBtn) {
        confirmStatusBtn.addEventListener('click', function() {
            const newStatus = statusSelect.value;
            
            // Aquí se enviaría una solicitud al servidor para actualizar el estado
            // Por ahora, simulamos la actualización en el frontend
            const propertyRow = document.querySelector(`tr[data-id="${currentPropertyId}"]`);
            if (propertyRow) {
                const statusCell = propertyRow.querySelector('.property-status');
                statusCell.className = `property-status status-${newStatus}`;
                
                let statusText = '';
                switch (newStatus) {
                    case 'active':
                        statusText = 'نشط';
                        break;
                    case 'pending':
                        statusText = 'قيد المراجعة';
                        break;
                    case 'sold':
                        statusText = 'تم البيع';
                        break;
                    case 'inactive':
                        statusText = 'غير نشط';
                        break;
                    default:
                        statusText = newStatus;
                }
                
                statusCell.textContent = statusText;
                
                // Actualizar las estadísticas si el estado cambió a/desde activo
                // Esto requeriría una recarga de la página o una actualización de las estadísticas mediante AJAX
                
                showNotification('تم تغيير حالة العقار بنجاح');
            }
            
            statusModal.classList.remove('show');
        });
    }
    
    // Manejadores para el modal de eliminación
    if (closeDeleteModal) {
        closeDeleteModal.addEventListener('click', function() {
            deleteModal.classList.remove('show');
        });
    }
    
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', function() {
            deleteModal.classList.remove('show');
        });
    }
    
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            // Aquí se enviaría una solicitud al servidor para eliminar la propiedad
            // Por ahora, simulamos la eliminación en el frontend
            const propertyRow = document.querySelector(`tr[data-id="${currentPropertyId}"]`);
            if (propertyRow) {
                propertyRow.classList.add('fade-out');
                
                setTimeout(() => {
                    propertyRow.remove();
                    
                    // Verificar si no hay más propiedades para mostrar el estado vacío
                    const rows = document.querySelectorAll('tbody tr');
                    if (rows.length === 0) {
                        const emptyRow = document.createElement('tr');
                        emptyRow.innerHTML = `
                            <td colspan="6" class="text-center">
                                <div class="empty-state">
                                    <i class="fas fa-building empty-icon"></i>
                                    <h3>لا توجد عقارات</h3>
                                    <p>لم تقم بإضافة أي عقارات بعد. انقر على زر "إضافة عقار جديد" لإضافة أول عقار.</p>
                                </div>
                            </td>
                        `;
                        document.querySelector('tbody').appendChild(emptyRow);
                    }
                    
                    // Actualizar las estadísticas
                    // Esto requeriría una recarga de la página o una actualización de las estadísticas mediante AJAX
                    
                    showNotification('تم حذف العقار بنجاح');
                }, 300);
            }
            
            deleteModal.classList.remove('show');
        });
    }
    
    // Delegación de eventos para los botones de acción en la tabla
    if (propertyTable) {
        propertyTable.addEventListener('click', function(e) {
            // Buscar el botón más cercano si se hizo clic en un ícono dentro del botón
            const button = e.target.closest('button');
            if (!button) return;
            
            // Obtener la fila de la propiedad y su ID
            const propertyRow = button.closest('tr');
            if (!propertyRow) return;
            
            currentPropertyId = propertyRow.dataset.id;
            
            // Manejar los diferentes botones de acción
            if (button.classList.contains('edit-btn')) {
                // Redirigir a la página de edición o abrir un modal de edición
                window.location.href = `/edit-property/${currentPropertyId}`;
            } else if (button.classList.contains('status-btn')) {
                // Obtener el estado actual para seleccionarlo en el dropdown
                const statusCell = propertyRow.querySelector('.property-status');
                const currentStatus = statusCell.className.replace('property-status status-', '');
                
                // Seleccionar el estado actual en el dropdown
                if (statusSelect) {
                    statusSelect.value = currentStatus;
                }
                
                // Mostrar el modal de cambio de estado
                statusModal.classList.add('show');
            } else if (button.classList.contains('delete-btn')) {
                // Mostrar el modal de confirmación de eliminación
                deleteModal.classList.add('show');
            }
        });
    }
    
    // Filtrado de propiedades
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            filterProperties();
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterProperties();
        });
    }
    
    function filterProperties() {
        const filterValue = filterSelect ? filterSelect.value : 'all';
        const searchValue = searchInput ? searchInput.value.toLowerCase() : '';
        
        const rows = document.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            // Ignorar la fila de estado vacío
            if (row.querySelector('.empty-state')) return;
            
            let showByFilter = filterValue === 'all';
            let showBySearch = true;
            
            // Filtrar por estado
            if (!showByFilter) {
                const statusCell = row.querySelector('.property-status');
                if (statusCell && statusCell.classList.contains(`status-${filterValue}`)) {
                    showByFilter = true;
                }
            }
            
            // Filtrar por texto de búsqueda
            if (searchValue) {
                const titleElement = row.querySelector('.property-title');
                const locationElement = row.querySelector('.property-location');
                
                const title = titleElement ? titleElement.textContent.toLowerCase() : '';
                const location = locationElement ? locationElement.textContent.toLowerCase() : '';
                
                showBySearch = title.includes(searchValue) || location.includes(searchValue);
            }
            
            // Mostrar u ocultar la fila según los filtros
            if (showByFilter && showBySearch) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        // Mostrar mensaje de "no se encontraron resultados" si no hay propiedades visibles
        let emptyRow = document.querySelector('.no-results-row');
        
        if (visibleCount === 0 && rows.length > 0) {
            if (!emptyRow) {
                emptyRow = document.createElement('tr');
                emptyRow.className = 'no-results-row';
                emptyRow.innerHTML = `
                    <td colspan="6" class="text-center">
                        <div class="empty-state">
                            <i class="fas fa-search empty-icon"></i>
                            <h3>لا توجد نتائج</h3>
                            <p>لم يتم العثور على عقارات تطابق معايير البحث الخاصة بك.</p>
                        </div>
                    </td>
                `;
                document.querySelector('tbody').appendChild(emptyRow);
            } else {
                emptyRow.style.display = '';
            }
        } else if (emptyRow) {
            emptyRow.style.display = 'none';
        }
    }
});
