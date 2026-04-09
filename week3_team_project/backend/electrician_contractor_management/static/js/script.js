document.addEventListener('DOMContentLoaded', () => {
    // Mobile sidebar toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const sidebar = document.querySelector('.sidebar');

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.add('active');
        });
    }

    if (closeSidebarBtn && sidebar) {
        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.remove('active');
        });
    }
    // Modal logic
    function setupModal(modalId, btnId, formId, onSubmit) {
        const modal = document.getElementById(modalId);
        const btn = document.getElementById(btnId);
        const form = document.getElementById(formId);
        
        if (!modal || !btn) return;
        
        const closeBtns = modal.querySelectorAll('.close-modal');
        
        btn.addEventListener('click', () => {
            modal.classList.add('show');
        });
        
        closeBtns.forEach(c => c.addEventListener('click', () => {
            modal.classList.remove('show');
        }));
        
        window.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('show');
        });
        
        if (form && !form.getAttribute('action')) {
            form.onsubmit = (e) => {
                e.preventDefault();
                onSubmit(form, modal);
            };
        }
    }

    // Modal close listeners (generic for dynamically opened modals)
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) modal.classList.remove('show');
        });
    });

    // Helper for AJAX form submission
    const handleFormSubmit = async (e) => {
        const form = e.target;
        if (!form.id || !form.closest('.modal')) return;

        e.preventDefault();
        const formData = new FormData(form);
        const modal = form.closest('.modal');

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const result = await response.json();
                modal.classList.remove('show');
                form.reset();
                showNotification(result.message || 'Success!', 'success');
                
                // Refresh data if on dashboard or management pages
                const managementPages = ['dashboard', 'electricians', 'jobs', 'tasks', 'materials'];
                const currentPage = window.location.pathname;
                if (managementPages.some(page => currentPage.includes(page))) {
                    setTimeout(() => window.location.reload(), 1500);
                }
            } else {
                showNotification('Something went wrong. Please try again.', 'error');
            }
        } catch (err) {
            console.error('Submission error:', err);
            showNotification('Network error. Please check your connection.', 'error');
        }
    };

    const showNotification = (message, type) => {
        let toast = document.getElementById('toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast';
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        setTimeout(() => toast.className = toast.className.replace('show', ''), 3000);
    };

    // Attach AJAX handler and setup modals
    const dashboardModals = [
        { id: 'addElectricianModal', btn: 'addElectricianBtn', form: 'addElectricianForm' },
        { id: 'createJobModal', btn: 'createJobBtn', form: 'createJobForm' },
        { id: 'addTaskModal', btn: 'addTaskBtn', form: 'addTaskForm' },
        { id: 'addMaterialModal', btn: 'addMaterialBtn', form: 'addMaterialForm' }
    ];

    dashboardModals.forEach(cfg => {
        setupModal(cfg.id, cfg.btn, cfg.form, null);
        const m = document.getElementById(cfg.id);
        if (m) {
            const f = m.querySelector('form');
            if (f) f.addEventListener('submit', handleFormSubmit);
        }
    });

    // Electrician Edit/Delete Logic
    document.querySelectorAll('.edit-el-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = document.getElementById('editElectricianModal');
            const form = document.getElementById('editElectricianForm');
            if (!modal || !form) return;
            
            const id = btn.dataset.id;
            form.action = `/electricians/update/${id}`;
            document.getElementById('editElName').value = btn.dataset.name;
            document.getElementById('editElEmail').value = btn.dataset.email;
            document.getElementById('editElPhone').value = btn.dataset.phone;
            document.getElementById('editElStatus').value = btn.dataset.status;
            
            modal.classList.add('show');
            form.onsubmit = handleFormSubmit;
        });
    });

    document.querySelectorAll('.delete-el-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to delete this electrician?')) return;
            const id = btn.dataset.id;
            const response = await fetch(`/electricians/delete/${id}`, { 
                method: 'POST', 
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (response.ok) {
                showNotification('Electrician deleted', 'success');
                setTimeout(() => window.location.reload(), 1000);
            }
        });
    });

    // Task Status Update Logic
    document.querySelectorAll('.status-update-btn').forEach(select => {
        select.addEventListener('change', async () => {
            const id = select.dataset.id;
            const status = select.value;
            const formData = new FormData();
            formData.append('status', status);
            
            const response = await fetch(`/tasks/update_status/${id}`, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (response.ok) {
                showNotification('Status updated', 'success');
                setTimeout(() => window.location.reload(), 1000);
            }
        });
    });

    // Material Usage Logic
    document.querySelectorAll('.use-material-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = document.getElementById('logUsageModal');
            const form = document.getElementById('logUsageForm');
            if (!modal || !form) return;
            
            const id = btn.dataset.id;
            form.action = `/materials/update_usage/${id}`;
            document.getElementById('usageText').textContent = `How many ${btn.dataset.unit} of ${btn.dataset.name} did you use? (Available: ${btn.dataset.qty})`;
            document.getElementById('usageQty').max = btn.dataset.qty;
            
            modal.classList.add('show');
            form.onsubmit = handleFormSubmit;
        });
    });

    // Generate PDF Logic
    const pdfBtns = document.querySelectorAll('.generate-pdf-btn');
    pdfBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            window.print();
        });
    });

    // Profile Logic
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Profile changes saved successfully!');
        });
    }

    const currentPath = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.sidebar-link');   
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '' && href === 'dashboard.html')) {
            link.classList.add('active');
        }
    });
});
