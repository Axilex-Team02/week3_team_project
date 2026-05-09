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

                    document.getElementById('view-job-id-hidden').value = id;
                    const imgEl = document.getElementById('detailJobImage');
                    const noImgEl = document.getElementById('noJobImage');
                    if (data.job.image_path) {
                        imgEl.src = '/api/uploads/' + data.job.image_path;
                        imgEl.style.display = 'block';
                        noImgEl.style.display = 'none';
                    } else {
                        imgEl.style.display = 'none';
                        noImgEl.style.display = 'block';
                    }

                    modal.classList.add('show');
                }
            } catch (err) {
                showNotification('Failed to fetch job details', 'error');
            }
        });
    });

    // Enhanced Payment Gateway Logic
    document.querySelectorAll('.pay-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = document.getElementById('paymentModal');
            if (!modal) return;
            
            // Reset UI
            document.getElementById('payment-main-ui').style.display = 'block';
            document.getElementById('payment-processing-ui').style.display = 'none';
            document.getElementById('payment-success-ui').style.display = 'none';
            document.getElementById('payment-failure-ui').style.display = 'none';
            
            // Populate data
            document.getElementById('payJobId').value = btn.dataset.id;
            document.getElementById('payJobIdText').textContent = btn.dataset.id;
            document.getElementById('payAmount').value = parseFloat(btn.dataset.amount).toFixed(2);
            document.getElementById('payToUser').value = btn.dataset.assignee;
            document.getElementById('payJobTitle').textContent = btn.dataset.title;
            
            modal.classList.add('show');
        });
    });

    // Method switching
    const paymentMethods = document.querySelectorAll('.pay-method-option');
    paymentMethods.forEach(method => {
        method.addEventListener('click', () => {
            paymentMethods.forEach(m => m.classList.remove('active'));
            method.classList.add('active');
            const input = method.querySelector('input');
            input.checked = true;
            
            // Toggle fields
            const cardFields = document.getElementById('card-details-fields');
            const upiFields = document.getElementById('upi-details-fields');
            
            if (input.value === 'Credit Card') {
                cardFields.style.display = 'block';
                upiFields.style.display = 'none';
            } else if (input.value === 'UPI') {
                cardFields.style.display = 'none';
                upiFields.style.display = 'block';
            } else {
                cardFields.style.display = 'none';
                upiFields.style.display = 'none';
            }
        });
    });

    const processPayment = async () => {
        const jobId = document.getElementById('payJobId').value;
        const amount = document.getElementById('payAmount').value;
        const toUserId = document.getElementById('payToUser').value;
        const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
        
        // Basic Validation
        if (paymentMethod === 'Credit Card') {
            const cardNum = document.getElementById('cardNumber').value;
            if (cardNum.length < 12) {
                showNotification('Please enter a valid card number', 'error');
                return;
            }
        } else if (paymentMethod === 'UPI') {
            const upiId = document.getElementById('upiId').value;
            if (!upiId.includes('@')) {
                showNotification('Please enter a valid UPI ID', 'error');
                return;
            }
        }

        // Show Processing
        document.getElementById('payment-main-ui').style.display = 'none';
        document.getElementById('payment-processing-ui').style.display = 'block';
        
        // Add a realistic delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        try {
            const response = await fetch('/api/payments/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    job_id: jobId,
                    amount: amount,
                    to_user_id: toUserId,
                    payment_type: paymentMethod,
                    card_number: document.getElementById('cardNumber').value
                })
            });
            
            const result = await response.json();
            
            document.getElementById('payment-processing-ui').style.display = 'none';
            
            if (response.ok) {
                document.getElementById('payment-success-ui').style.display = 'block';
                document.getElementById('success-txn-id').textContent = result.transaction_id;
                showNotification('Payment successful!', 'success');
            } else {
                document.getElementById('payment-failure-ui').style.display = 'block';
                document.getElementById('failure-message').textContent = result.message || 'Payment failed';
            }
        } catch (err) {
            document.getElementById('payment-processing-ui').style.display = 'none';
            document.getElementById('payment-failure-ui').style.display = 'block';
            document.getElementById('failure-message').textContent = 'Network error. Gateway unreachable.';
        }
    };

    const confirmPaymentBtn = document.getElementById('confirmPaymentBtn');
    if (confirmPaymentBtn) {
        confirmPaymentBtn.addEventListener('click', processPayment);
    }

    const retryPaymentBtn = document.getElementById('retryPaymentBtn');
    if (retryPaymentBtn) {
        retryPaymentBtn.addEventListener('click', () => {
            document.getElementById('payment-failure-ui').style.display = 'none';
            document.getElementById('payment-main-ui').style.display = 'block';
        });
    }

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

    // Reports & Dashboard Visualization
    if (window.location.pathname.includes('/reporter') || window.location.pathname.includes('/dashboard')) {
        initCharts();
    }

    async function initCharts() {
        const statusCanvas = document.getElementById('statusChart');
        const workloadCanvas = document.getElementById('workloadChart');
        if (!statusCanvas && !workloadCanvas) return;

        try {
            const response = await fetch('/api/reports/stats');
            const data = await response.json();
            window.deleteTaskFile = async function(taskId) {
        if (!confirm('Are you sure you want to delete this report? This action cannot be undone.')) return;
        
        try {
            const response = await fetch(`/api/tasks/delete-report/${taskId}`, { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                showToast('File deleted successfully!', 'success');
                location.reload(); // Refresh to show the upload button
            } else {
                showToast(data.message, 'error');
            }
        } catch (err) {
            showToast('Failed to delete file', 'error');
        }
    };

    /**
     * Data Population & Charts
     */
            
            // Status Chart
            if (statusCanvas) {
                const completionData = data.completion;
                new Chart(statusCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: completionData.map(s => s.status),
                        datasets: [{
                            data: completionData.map(s => s.count),
                            backgroundColor: ['#3b82f6', '#f59e0b', '#10b981', '#ef4444']
                        }]
                    },
                    options: { 
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } }
                    }
                });
            }
            
            // Detailed Report Population
            const reportCompRate = document.getElementById('report-completion-rate');
            if (reportCompRate) {
                const currentRate = 75; // Use requested projected rate
                const targetRate = 90; // Use requested goal
                
                reportCompRate.textContent = `${currentRate}%`;
                const bar = document.getElementById('report-completion-bar');
                bar.style.width = `${currentRate}%`;
                
                // Color coding based on new targets
                if (currentRate >= targetRate) {
                    bar.style.backgroundColor = 'var(--success)';
                } else if (currentRate >= 70) {
                    bar.style.backgroundColor = '#f59e0b'; // Amber for 75%
                } else {
                    bar.style.backgroundColor = 'var(--danger)';
                }

                document.getElementById('report-total-tasks').textContent = data.totals.tasks;
                document.getElementById('report-total-electricians').textContent = data.totals.electricians;
                document.getElementById('report-total-materials').textContent = data.totals.materials;
                
                // Priority List
                const priorityList = document.getElementById('report-priority-list');
                if (data.priority_jobs.length > 0) {
                    priorityList.innerHTML = data.priority_jobs.map(j => `
                        <tr>
                            <td>${j.title}</td>
                            <td class="text-danger">${j.deadline}</td>
                            <td><span class="badge badge-warning">${j.status}</span></td>
                        </tr>
                    `).join('');
                } else {
                    priorityList.innerHTML = '<tr><td colspan="3" class="text-center">No high-priority alerts</td></tr>';
                }

                // Achievements
                const achEl = document.getElementById('report-achievements');
                achEl.innerHTML = `
                    <div style="padding: 1rem; background: var(--light-blue); border-radius: 8px;">
                        <p style="font-weight: 600; color: var(--primary-blue); font-size: 1.1rem;">${data.daily_count} Tasks Completed Today</p>
                        <p style="font-size: 0.875rem; color: var(--text-light);">Keep up the great momentum! The team is currently performing at ${data.completion_rate}% efficiency across all active projects.</p>
                    </div>
                `;
            }
            
            // Workload Chart (Admin only)
            if (workloadCanvas && data.activity.length > 0) {
                new Chart(workloadCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.activity.map(a => a.name),
                        datasets: [{
                            label: 'Tasks Assigned',
                            data: data.activity.map(a => a.task_count),
                            backgroundColor: '#3b82f6'
                        }]
                    },
                    options: { 
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                    }
                });
            }
        } catch (err) {
            console.error('Failed to init charts:', err);
        }
    }

    // Generic File Upload Handler
    window.handleFileUpload = async (input, type, id) => {
        const file = input.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);
        formData.append('id', id);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const result = await response.json();
            if (response.ok) {
                showNotification('File uploaded successfully', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showNotification(result.message || 'Upload failed', 'error');
            }
        } catch (err) {
            showNotification('Network error during upload', 'error');
        }
    };

    // Clear Payments Logic
    const clearPaymentsBtn = document.getElementById('clearPaymentsBtn');
    if (clearPaymentsBtn) {
        clearPaymentsBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to delete all payment history? This action cannot be undone.')) return;
            
            clearPaymentsBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Clearing...';
            clearPaymentsBtn.disabled = true;
            
            try {
                const response = await fetch('/api/payments/clear', {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const result = await response.json();
                
                if (response.ok) {
                    showNotification(result.message, 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showNotification(result.message || 'Failed to clear payments', 'error');
                    clearPaymentsBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Clear All Payments';
                    clearPaymentsBtn.disabled = false;
                }
            } catch (err) {
                showNotification('Network error', 'error');
                clearPaymentsBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Clear All Payments';
                clearPaymentsBtn.disabled = false;
            }
        });
    }
});
