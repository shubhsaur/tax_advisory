document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const stepUpload = document.getElementById('step-upload');
    const stepReview = document.getElementById('step-review');
    const uploadForm = document.getElementById('upload-form');
    const reviewForm = document.getElementById('review-form');
    const reviewFields = document.getElementById('review-fields');
    const backBtn = document.getElementById('back-btn');
    const toast = document.getElementById('toast');
    const spinner = document.getElementById('spinner-overlay');
    const regimeBtn = document.getElementById('regime-btn');
    const stepRegime = document.getElementById('step-regime');
    const regimeOptions = document.getElementById('regime-options');
    const regimeResults = document.getElementById('regime-results');
    const regimeBackBtn = document.getElementById('regime-back-btn');
    let lastReviewedData = {};

    // Hide stepper initially, show on Start
    document.getElementById('stepper').style.display = 'none';
    startBtn.addEventListener('click', function() {
        startBtn.style.display = 'none';
        document.getElementById('stepper').style.display = 'block';
        stepUpload.style.display = 'block';
        stepReview.style.display = 'none';
    });

    // Show toast notification
    function showToast(msg, type = 'error') {
        toast.textContent = msg;
        toast.className = 'toast ' + (type === 'success' ? 'toast-success' : 'toast-error');
        toast.style.display = 'block';
        setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }

    // Handle PDF upload
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const fileInput = document.getElementById('pdf-input');
        if (!fileInput.files.length) {
            showToast('Please select a PDF file.');
            return;
        }
        spinner.style.display = 'flex';
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        try {
            const res = await fetch('/api/upload-pdf', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            spinner.style.display = 'none';
            if (!res.ok) {
                showToast(data.error || 'Extraction failed.', 'error');
                return;
            }
            // Group fields for UI
            const fields = data.fields;
            let salaryHtml = '<div class="review-section"><div class="review-section-title">Salary Details</div>';
            ["gross_salary","basic_salary","hra_received"].forEach(key => {
                salaryHtml += `<label for="${key}">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>`;
                salaryHtml += `<input type="text" id="${key}" name="${key}" value="${fields[key] || ''}" />`;
            });
            salaryHtml += '</div>';
            let deductionHtml = '<div class="review-section"><div class="review-section-title">Deductions & Other</div>';
            ["rent_paid","deduction_80c","deduction_80d","standard_deduction","professional_tax","tds"].forEach(key => {
                deductionHtml += `<label for="${key}">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>`;
                if (key === 'standard_deduction') {
                    deductionHtml += `<input type="text" id="${key}" name="${key}" value="50000" readonly style="background:#e5e7eb; color:#888; cursor:not-allowed;" />`;
                } else {
                    deductionHtml += `<input type="text" id="${key}" name="${key}" value="${fields[key] || ''}" />`;
                }
            });
            deductionHtml += '</div>';
            reviewFields.innerHTML = salaryHtml + deductionHtml;
            stepUpload.style.display = 'none';
            stepReview.style.display = 'block';
        } catch (err) {
            spinner.style.display = 'none';
            showToast('Upload failed.', 'error');
        }
    });

    // Handle back button
    backBtn.addEventListener('click', function() {
        stepReview.style.display = 'none';
        stepUpload.style.display = 'block';
    });

    // Update reviewForm submit handler to POST data
    reviewForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        spinner.style.display = 'flex';
        const formData = new FormData(reviewForm);
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        lastReviewedData = { ...data };
        try {
            const res = await fetch('/api/save-financials', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await res.json();
            spinner.style.display = 'none';
            if (res.ok) {
                showToast('Data saved successfully!', 'success');
            } else {
                showToast(result.error || 'Save failed.', 'error');
            }
        } catch (err) {
            spinner.style.display = 'none';
            showToast('Save failed.', 'error');
        }
    });

    // Show regime step on button click
    regimeBtn.addEventListener('click', function() {
        if (!lastReviewedData || Object.keys(lastReviewedData).length === 0) {
            showToast('Please save your data before selecting a regime.', 'error');
            return;
        }
        stepReview.style.display = 'none';
        stepRegime.style.display = 'block';
        renderRegimeOptions();
    });

    // Render regime cards
    function renderRegimeOptions() {
        regimeOptions.innerHTML = '';
        const regimes = [
            { key: 'old', label: 'Old Regime', icon: '🏛️' },
            { key: 'new', label: 'New Regime', icon: '✨' }
        ];
        regimes.forEach(regime => {
            const div = document.createElement('div');
            div.className = 'regime-card';
            div.innerHTML = `<div class='regime-icon'>${regime.icon}</div><div>${regime.label}</div><div class='regime-result' id='${regime.key}-result'></div>`;
            div.dataset.key = regime.key;
            div.onclick = async function() {
                document.querySelectorAll('.regime-card').forEach(card => card.classList.remove('selected'));
                div.classList.add('selected');
                await showRegimeResults(regime.key);
            };
            regimeOptions.appendChild(div);
        });
        regimeResults.innerHTML = '';
    }

    async function showRegimeResults(selectedRegime) {
        if (!lastReviewedData || Object.keys(lastReviewedData).length === 0) return;
        // Call backend for calculation
        const res = await fetch('/api/calculate-tax', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(lastReviewedData)
        });
        const result = await res.json();
        ['old', 'new'].forEach(key => {
            const el = document.getElementById(`${key}-result`);
            if (el && result[key]) {
                el.innerHTML = `<div><strong>${key === 'old' ? 'Old Regime' : 'New Regime'}:</strong><br>Taxable Income: <span style='color:#2563eb;font-weight:700;'>₹ ${result[key].taxable_income.toLocaleString('en-IN')}</span><br>Tax Payable: <span style='color:#2563eb;font-weight:700;'>₹ ${result[key].tax.toLocaleString('en-IN')}</span></div>`;
            }
        });
    }

    // Back to review step
    regimeBackBtn.addEventListener('click', function() {
        stepRegime.style.display = 'none';
        stepReview.style.display = 'block';
    });

    // Custom file input label logic
    const fileInput = document.getElementById('pdf-input');
    const fileLabel = document.querySelector('.file-label');
    const fileChosen = document.getElementById('file-chosen');
    fileLabel.addEventListener('click', function() {
        fileInput.click();
    });
    fileInput.addEventListener('change', function() {
        fileChosen.textContent = fileInput.files.length ? fileInput.files[0].name : 'No file chosen';
    });
}); 