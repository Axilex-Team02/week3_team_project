document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    if (closeSidebarBtn && sidebar) {
        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
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
        
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                onSubmit(form, modal);
            });
        }
    }

    // Add Electrician Logic
    setupModal('addElectricianModal', 'addElectricianBtn', 'addElectricianForm', (form, modal) => {
        const name = document.getElementById('elName').value;
        const email = document.getElementById('elEmail').value;
        const phone = document.getElementById('elPhone').value;
        
        const tbody = document.querySelector('table tbody');
        if (tbody) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div class="flex items-center gap-1">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random" style="width: 32px; height: 32px; border-radius: 50%;">
                        <span style="font-weight: 500;">${name}</span>
                    </div>
                </td>
                <td style="color: var(--text-light);">${email}</td>
                <td style="color: var(--text-light);">${phone}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"><i class="fa-solid fa-trash"></i></button>
                </td>
            `;
            tbody.insertAdjacentElement('afterbegin', tr);
        }
        form.reset();
        modal.classList.remove('show');
    });

    // Create Job Logic
    setupModal('createJobModal', 'createJobBtn', 'createJobForm', (form, modal) => {
        const title = document.getElementById('jobTitle').value;
        const location = document.getElementById('jobLocation').value;
        const assignee = document.getElementById('jobAssignee').value;
        let dateVal = document.getElementById('jobDeadline').value;
        
        const d = new Date(dateVal);
        const options = { month: 'short', day: 'numeric', year: 'numeric' };
        if(isNaN(d)) dateVal = "TBD";
        else dateVal = d.toLocaleDateString('en-US', options);

        const tbody = document.querySelector('table tbody');
        if (tbody) {
            let assigneeHtml = '';
            if (assignee === 'Unassigned') {
                 assigneeHtml = `<span style="font-size: 0.875rem; color: var(--text-light); font-style: italic;">Unassigned</span>`;
            } else {
                 assigneeHtml = `
                    <div class="flex items-center gap-1">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(assignee)}&background=random" style="width: 24px; height: 24px; border-radius: 50%;">
                        <span style="font-size: 0.875rem;">${assignee}</span>
                    </div>
                 `;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-weight: 500;">${title}</td>
                <td style="color: var(--text-light);">${location}</td>
                <td>${assigneeHtml}</td>
                <td>${dateVal}</td>
                <td><span class="badge badge-warning">In Progress</span></td>
                <td>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">View</button>
                </td>
            `;
            tbody.insertAdjacentElement('afterbegin', tr);
        }
        form.reset();
        modal.classList.remove('show');
    });

    // Add Task Logic
    setupModal('addTaskModal', 'addTaskBtn', 'addTaskForm', (form, modal) => {
        const taskName = document.getElementById('taskName').value;
        const taskJob = document.getElementById('taskJob').value;
        const taskAssignee = document.getElementById('taskAssignee').value;
        
        const tbody = document.querySelector('table tbody');
        if (tbody) {
            let assigneeHtml = '';
            if (taskAssignee.toLowerCase() === 'unassigned' || !taskAssignee) {
                 assigneeHtml = `<span style="font-size: 0.875rem; color: var(--text-light); font-style: italic;">Unassigned</span>`;
            } else {
                 assigneeHtml = `
                    <div class="flex items-center gap-1">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(taskAssignee)}&background=random" style="width: 24px; height: 24px; border-radius: 50%;">
                        <span style="font-size: 0.875rem;">${taskAssignee}</span>
                    </div>
                 `;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-weight: 500;">${taskName}</td>
                <td style="color: var(--text-light);">${taskJob}</td>
                <td>${assigneeHtml}</td>
                <td>
                    <div style="background-color: var(--mid-grey); height: 8px; border-radius: 4px; overflow: hidden; width: 100px; display: inline-block; vertical-align: middle; margin-right: 0.5rem;">
                        <div style="background-color: var(--danger); height: 100%; width: 0%;"></div>
                    </div>
                    <span style="font-size: 0.75rem; color: var(--text-light);">0%</span>
                </td>
                <td>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">Update</button>
                </td>
            `;
            tbody.insertAdjacentElement('afterbegin', tr);
        }
        form.reset();
        modal.classList.remove('show');
    });

    // Add Material Logic
    setupModal('addMaterialModal', 'addMaterialBtn', 'addMaterialForm', (form, modal) => {
        const matName = document.getElementById('matName').value;
        const matQty = document.getElementById('matQty').value;
        const matUnit = document.getElementById('matUnit').value;
        
        const tbody = document.querySelector('table tbody');
        if (tbody) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-weight: 500;">${matName}</td>
                <td><span class="badge badge-success">${matQty}</span></td>
                <td style="color: var(--text-light);">${matUnit}</td>
                <td style="color: var(--text-light); font-size: 0.875rem;">No recent usage</td>
                <td>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">Log Usage</button>
                </td>
            `;
            tbody.insertAdjacentElement('afterbegin', tr);
        }
        form.reset();
        modal.classList.remove('show');
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
