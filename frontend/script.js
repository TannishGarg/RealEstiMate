// Use the API_BASE_URL from window or auth.js if available, otherwise define it
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';
window.API_BASE_URL = API_BASE_URL;

// Initialize on page load (only if not already initialized)
let initialized = false;

function initializePrediction() {
    if (initialized) {
        console.log('Prediction already initialized');
        return;
    }
    initialized = true;
    
    console.log('Initializing prediction form...');
    
    const stateSelect = document.getElementById('State');
    const citySelect = document.getElementById('City');
    const localitySelect = document.getElementById('Locality');
    const form = document.getElementById('predictionForm');
    
    if (!stateSelect) {
        console.error('State select not found');
        return;
    }
    if (!citySelect) {
        console.error('City select not found');
        return;
    }
    if (!localitySelect) {
        console.error('Locality select not found');
        return;
    }
    if (!form) {
        console.error('Prediction form not found');
        return;
    }
    
    console.log('All form elements found, loading states...');
    loadStates();
    setupEventListeners();
    console.log('Prediction form initialized successfully');
}

// Make functions globally available
window.initializePrediction = initializePrediction;
window.loadStates = loadStates;
window.setupEventListeners = setupEventListeners;
window.predictPrice = predictPrice;

// Initialize on page load (but allow manual initialization too)
document.addEventListener('DOMContentLoaded', function() {
    // Only auto-initialize if we're on prediction page
    if (window.location.pathname.includes('prediction')) {
        // Wait a bit for auth check to complete
        setTimeout(initializePrediction, 300);
    }
});

// Load states from API
async function loadStates() {
    try {
        console.log('Loading states from API...');
        const response = await fetch(`${API_BASE_URL}/locations`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('States loaded:', data.states?.length || 0);
        
        const stateSelect = document.getElementById('State');
        if (!stateSelect) {
            console.error('State select element not found');
            return;
        }
        
        stateSelect.innerHTML = '<option value="">Select State</option>';
        
        if (data.states && data.states.length > 0) {
            data.states.forEach(state => {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                stateSelect.appendChild(option);
            });
            console.log('States dropdown populated successfully');
        } else {
            console.warn('No states returned from API');
        }
    } catch (error) {
        console.error('Error loading states:', error);
        const errorMsg = 'Failed to load states. Please refresh the page.';
        if (typeof showError === 'function') {
            showError(errorMsg);
        } else {
            alert(errorMsg);
        }
    }
}

// Setup event listeners
function setupEventListeners() {
    const stateSelect = document.getElementById('State');
    const citySelect = document.getElementById('City');
    const localitySelect = document.getElementById('Locality');
    const form = document.getElementById('predictionForm');
    
    // State change handler
    stateSelect.addEventListener('change', async function() {
        const state = this.value;
        
        // Reset city and locality
        citySelect.innerHTML = '<option value="">Select City</option>';
        citySelect.disabled = !state;
        localitySelect.innerHTML = '<option value="">Select Locality</option>';
        localitySelect.disabled = true;
        
        if (state) {
            await loadCities(state);
        }
    });
    
    // City change handler
    citySelect.addEventListener('change', async function() {
        const city = this.value;
        
        // Reset locality
        localitySelect.innerHTML = '<option value="">Select Locality</option>';
        localitySelect.disabled = !city;
        
        if (city) {
            await loadLocalities(city);
        }
    });
    
    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await predictPrice();
    });
}

// Load cities for selected state
async function loadCities(state) {
    try {
        const response = await fetch(`${API_BASE_URL}/locations?state=${encodeURIComponent(state)}`);
        const data = await response.json();
        
        const citySelect = document.getElementById('City');
        citySelect.innerHTML = '<option value="">Select City</option>';
        
        if (data.cities && data.cities.length > 0) {
            data.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);
            });
            citySelect.disabled = false;
        }
    } catch (error) {
        console.error('Error loading cities:', error);
        showError('Failed to load cities. Please try again.');
    }
}

// Load localities for selected city
async function loadLocalities(city) {
    try {
        const response = await fetch(`${API_BASE_URL}/locations?city=${encodeURIComponent(city)}`);
        const data = await response.json();
        
        const localitySelect = document.getElementById('Locality');
        localitySelect.innerHTML = '<option value="">Select Locality</option>';
        
        if (data.localities && data.localities.length > 0) {
            data.localities.forEach(locality => {
                const option = document.createElement('option');
                option.value = locality;
                option.textContent = locality;
                localitySelect.appendChild(option);
            });
            localitySelect.disabled = false;
        }
    } catch (error) {
        console.error('Error loading localities:', error);
        showError('Failed to load localities. Please try again.');
    }
}

// Predict price
async function predictPrice() {
    const form = document.getElementById('predictionForm');
    if (!form) {
        console.error('Prediction form not found');
        return;
    }
    
    const submitBtn = form.querySelector('button[type="submit"]') || form.querySelector('.btn-primary');
    const resultDiv = document.getElementById('result');
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Predicting...';
    }
    if (resultDiv) {
        resultDiv.classList.remove('show');
        resultDiv.innerHTML = '';
        
        // Show loading indicator
        setTimeout(() => {
            resultDiv.innerHTML = `
                <div class="prediction-result-card" style="background: linear-gradient(135deg, rgba(52, 152, 219, 0.08) 0%, rgba(41, 128, 185, 0.04) 100%); border: 1px solid rgba(52, 152, 219, 0.15);">
                    <div class="prediction-result-title" style="color: #2980b9;">Predicting Price</div>
                    <div class="prediction-result-value" style="color: #2980b9; font-size: 1.5rem;">
                        <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #2980b9; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    </div>
                    <div class="prediction-result-unit" style="color: #2980b9;">Analyzing property details...</div>
                </div>
            `;
            resultDiv.classList.add('show');
        }, 100);
    }
    
    // Collect form data
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Convert numeric fields
    const numericFields = ['BHK', 'Size_in_SqFt', 'Floor_No', 'Total_Floors', 
                          'Age_of_Property', 'Nearby_Schools', 'Nearby_Hospitals'];
    numericFields.forEach(field => {
        if (data[field]) {
            data[field] = parseInt(data[field]);
        }
    });
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(result);
        } else {
            showError(result.error || 'Prediction failed. Please check your inputs.');
        }
    } catch (error) {
        console.error('Error predicting price:', error);
        showError('Failed to connect to server. Please make sure the backend is running.');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Predict Price';
        }
    }
}

// Show success result
function showSuccess(result) {
    const resultDiv = document.getElementById('result');
    
    // Use 'prediction' from backend response
    const price = result.prediction || result.price || 0;
    
    // Format price for display (convert to Lakhs/Crores if needed)
    let formattedPrice = price;
    let unit = 'Lakhs';
    
    if (price >= 100) {
        formattedPrice = (price / 100).toFixed(2);
        unit = 'Crores';
    } else {
        formattedPrice = price.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
    
    resultDiv.innerHTML = `
        <div class="prediction-result-card">
            <div class="prediction-result-title">Estimated Price</div>
            <div class="prediction-result-value">₹${formattedPrice}</div>
            <div class="prediction-result-unit">${unit}</div>
        </div>
    `;
    
    // Show result with animation
    resultDiv.classList.add('show');
    
    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show error result
function showError(message) {
    const resultDiv = document.getElementById('result');
    
    resultDiv.innerHTML = `
        <div class="prediction-result-card" style="background: linear-gradient(135deg, rgba(231, 76, 60, 0.08) 0%, rgba(192, 57, 43, 0.04) 100%); border: 1px solid rgba(231, 76, 60, 0.15);">
            <div class="prediction-result-title" style="color: #c0392b;">Prediction Error</div>
            <div class="prediction-result-value" style="color: #c0392b; font-size: 1.5rem;">❌</div>
            <div class="prediction-result-unit" style="color: #c0392b;">${message}</div>
        </div>
    `;
    
    // Show result with animation
    resultDiv.classList.add('show');
    
    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

