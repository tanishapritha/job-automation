document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const startSearch = document.getElementById('startSearch');
    const jobFeed = document.getElementById('jobFeed');
    const loading = document.getElementById('loading');

    // ── Theme Engine (Light Default) ──────────────────────────────────────────
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        
        themeIcon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        themeText.innerText = isDark ? 'Light Mode' : 'Dark Mode';
    });

    // ── Search Logic ──────────────────────────────────────────────────────────
    startSearch.addEventListener('click', async () => {
        const domains = document.getElementById('domains').value;
        const loc1 = document.getElementById('loc1').value;
        const loc2 = document.getElementById('loc2').value;
        const remoteOnly = document.getElementById('remoteFilter').checked;
        const expLevel = document.getElementById('expLevel').value;
        const salary = document.getElementById('minSalary').value;

        // Visual Feedback
        jobFeed.innerHTML = '';
        loading.style.display = 'block';

        const payload = {
            query: domains.split(';').join(', '),
            location: `${loc1}, ${loc2}`,
            results: 10,
            experience_level: expLevel,
            remote_preference: remoteOnly ? "remote" : "onsite",
            salary_min: parseInt(salary)
        };

        try {
            const response = await fetch('http://localhost:8000/jobs/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Backend unavailable');

            const jobs = await response.json();
            renderJobs(jobs);
        } catch (error) {
            jobFeed.innerHTML = `<p style="grid-column: 1/-1; color: #ef4444; text-align: center;">Connection Failure. Ensure FastAPI is active on :8000.</p>`;
        } finally {
            loading.style.display = 'none';
        }
    });

    function renderJobs(jobs) {
        if (jobs.length === 0) {
            jobFeed.innerHTML = `<p style="grid-column: 1/-1; text-align: center;">No matching vacancies found today.</p>`;
            return;
        }

        jobs.forEach(job => {
            const card = document.createElement('div');
            card.className = 'job-card';
            
            const pClass = job.source.toLowerCase();
            const pName = job.source.charAt(0).toUpperCase() + job.source.slice(1);

            card.innerHTML = `
                <div class="source-badge ${pClass}">
                    <i class="fas fa-rss"></i> ${pName}
                </div>
                <h3 class="job-title">${job.title}</h3>
                <div class="job-company"><i class="fas fa-building"></i> ${job.company}</div>
                
                <div class="job-details">
                    <div><i class="fas fa-location-dot"></i> ${job.location}</div>
                    ${job.salary ? `<div><i class="fas fa-credit-card"></i> ${job.salary}</div>` : ''}
                    <div><i class="fas fa-calendar-day"></i> Last 48 hrs</div>
                </div>

                <a href="${job.apply_url}" target="_blank" class="apply-link">
                    Open Position
                </a>
            `;
            jobFeed.appendChild(card);
        });
    }

    console.log("Classic Minimalist Dashboard Active 🚀");
});
