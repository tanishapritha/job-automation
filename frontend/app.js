document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('searchBtn');
    const resultsGrid = document.getElementById('resultsGrid');
    const loader = document.getElementById('loader');
    const salaryRange = document.getElementById('salaryRange');
    const salaryDisplay = document.getElementById('salaryDisplay');
    const expButtons = document.querySelectorAll('.exp-btn');
    
    let selectedExperience = 'mid';

    // UI: Salary Display Update
    salaryRange.addEventListener('input', (e) => {
        salaryDisplay.innerText = `₹${e.target.value}L`;
    });

    // UI: Experience Toggles
    expButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            expButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedExperience = btn.dataset.level;
        });
    });

    // --- Search Execution ---
    searchBtn.addEventListener('click', async () => {
        const domains = document.getElementById('domains').value;
        const locations = [
            document.getElementById('loc1').value,
            document.getElementById('loc2').value,
            document.getElementById('loc3').value
        ].filter(l => l.trim() !== "").join(", ");

        const isRemote = document.getElementById('remoteCheck').checked;
        const minSalary = parseInt(salaryRange.value) * 100000; // Convert L to actual

        // UI Reset
        resultsGrid.innerHTML = '';
        loader.style.display = 'block';

        const payload = {
            query: domains.split(';').join(', '),
            location: locations,
            results: 15,
            experience_level: selectedExperience,
            job_type: "full_time",
            remote_preference: isRemote ? "remote" : "onsite",
            salary_min: minSalary
        };

        try {
            const response = await fetch('http://localhost:8000/jobs/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Search failed');

            const jobs = await response.json();
            renderJobs(jobs);
        } catch (error) {
            console.error(error);
            resultsGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--danger);">Error connecting to API. Ensure FastAPI is running.</p>`;
        } finally {
            loader.style.display = 'none';
        }
    });

    function renderJobs(jobs) {
        if (jobs.length === 0) {
            resultsGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No jobs found in the last 48 hours. Try broadening your domain list.</p>`;
            return;
        }

        jobs.forEach(job => {
            const card = document.createElement('div');
            card.className = 'job-card';
            
            const platformClass = job.source.toLowerCase();
            const platformName = job.source.charAt(0).toUpperCase() + job.source.slice(1);

            card.innerHTML = `
                <div class="platform-badge ${platformClass}">${platformName}</div>
                <div class="job-title">${job.title}</div>
                <div class="company-name">${job.company}</div>
                
                <div class="job-meta">
                    <span><i class="fas fa-map-marker-alt"></i> ${job.location}</span>
                    ${job.salary ? `<span><i class="fas fa-coins"></i> ${job.salary}</span>` : ''}
                </div>

                <a href="${job.apply_url}" target="_blank" class="apply-btn">View Opportunity</a>
            `;
            resultsGrid.appendChild(card);
        });
    }

    console.log("Global Job Lab Initialized 🚀");
});
