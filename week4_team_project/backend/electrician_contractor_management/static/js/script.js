document.addEventListener('DOMContentLoaded', () => {
    // Mobile sidebar toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const sidebar = document.querySelector('.sidebar');

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.add('open'); // Changed from 'active' to match CSS media queries if updated, or keeping 'active'
        });
    }

    if (closeSidebarBtn && sidebar) {
        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }

    // Close sidebar on link click (mobile)
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    });
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
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(profileForm);
            try {
                const response = await fetch(profileForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const result = await response.json();
                if (response.ok) {
                    showNotification(result.message, 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showNotification(result.message || 'Update failed', 'error');
                }
            } catch (err) {
                showNotification('Network error', 'error');
            }
        });
    }

    // Job View Logic
    document.querySelectorAll('.view-job-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const modal = document.getElementById('jobDetailsModal');
            if (!modal) return;

            try {
                const response = await fetch(`/api/jobs/${id}`);
                const data = await response.json();

                if (response.ok) {
                    document.getElementById('detailJobTitle').textContent = data.job.title;
                    document.getElementById('detailJobLocation').textContent = data.job.location || 'N/A';
                    document.getElementById('detailJobDeadline').textContent = data.job.deadline || 'N/A';
                    
                    const statusEl = document.getElementById('detailJobStatus');
                    statusEl.textContent = data.job.status;
                    statusEl.className = `badge badge-${data.job.status === 'Completed' ? 'success' : data.job.status === 'In Progress' ? 'warning' : 'danger'}`;

                    const taskList = document.getElementById('jobTasksList');
                    if (data.tasks.length > 0) {
                        taskList.innerHTML = data.tasks.map(t => `
                            <div class="flex justify-between p-1 bg-gray-50 rounded" style="font-size: 0.875rem;">
                                <span>${t.description}</span>
                                <span class="text-light">${t.status}</span>
                            </div>
                        `).join('');
                    } else {
                        taskList.innerHTML = '<p class="text-light" style="font-size: 0.875rem;">No tasks assigned yet.</p>';
                    }

                    modal.classList.add('show');
                }
            } catch (err) {
                showNotification('Failed to fetch job details', 'error');
            }
        });
    });

    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-link');   
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath === href || (currentPath === '/' && href === '/dashboard')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Notification Logic
    const notificationBtn = document.getElementById('notification-btn');
    const notificationDropdown = document.getElementById('notification-dropdown');
    
    if (notificationBtn && notificationDropdown) {
        notificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notificationDropdown.classList.toggle('show');
            if (notificationDropdown.classList.contains('show')) {
                markNotificationsRead();
            }
        });
        
        document.addEventListener('click', (e) => {
            if (!notificationDropdown.contains(e.target) && e.target !== notificationBtn) {
                notificationDropdown.classList.remove('show');
            }
        });
    }

    async function fetchNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (response.ok) {
                const data = await response.json();
                updateNotificationUI(data);
            }
        } catch (err) {
            console.error('Failed to fetch notifications');
        }
    }

    function updateNotificationUI(data) {
        const badge = document.getElementById('notification-count');
        const list = document.getElementById('notification-list');
        if (!badge || !list) return;
        
        badge.textContent = data.unread_count;
        badge.style.display = data.unread_count > 0 ? 'flex' : 'none';
        
        if (data.notifications.length === 0) {
            list.innerHTML = '<div class="notification-item"><p style="text-align:center;width:100%;color:var(--text-light)">No notifications</p></div>';
            return;
        }
        
        list.innerHTML = data.notifications.map(n => `
            <div class="notification-item ${n.is_read ? '' : 'unread'}">
                <i class="fa-solid ${getIconForType(n.type)} ${n.type}"></i>
                <div class="content">
                    <p>${n.message}</p>
                    <span>${n.created_at}</span>
                </div>
            </div>
        `).join('');
    }

    function getIconForType(type) {
        switch(type) {
            case 'success': return 'fa-circle-check';
            case 'warning': return 'fa-triangle-exclamation';
            case 'error': return 'fa-circle-xmark';
            default: return 'fa-circle-info';
        }
    }

    async function markNotificationsRead() {
        await fetch('/api/notifications/mark-read', { method: 'POST' });
        const badge = document.getElementById('notification-count');
        if (badge) badge.style.display = 'none';
    }

    // Poll for notifications every 30 seconds
    setInterval(fetchNotifications, 30000);
    fetchNotifications();

    // Reports Visualization
    if (window.location.pathname.includes('/reporter')) {
        initReports();
    }

    async function initReports() {
        try {
            const response = await fetch('/api/reports/stats');
            const data = await response.json();
            
            // Completion Chart
            const ctxComp = document.getElementById('completionChart');
            if (ctxComp) {
                new Chart(ctxComp, {
                    type: 'doughnut',
                    data: {
                        labels: data.completion.map(s => s.status),
                        datasets: [{
                            data: data.completion.map(s => s.count),
                            backgroundColor: ['#3b82f6', '#f59e0b', '#10b981', '#ef4444']
                        }]
                    },
                    options: { maintainAspectRatio: false }
                });
            }
            
            // Activity Chart
            const ctxAct = document.getElementById('activityChart');
            if (ctxAct) {
                new Chart(ctxAct, {
                    type: 'bar',
                    data: {
                        labels: data.activity.map(a => a.name),
                        datasets: [{
                            label: 'Tasks Assigned',
                            data: data.activity.map(a => a.task_count),
                            backgroundColor: '#3b82f6'
                        }]
                    },
                    options: { maintainAspectRatio: false }
                });
            }
            
            const dailyCountEl = document.getElementById('daily-completion-count');
            if (dailyCountEl) dailyCountEl.textContent = data.daily_count;
            
        } catch (err) {
            console.error('Failed to init reports:', err);
        }
    }
});
