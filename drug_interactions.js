document.addEventListener('DOMContentLoaded', function() {
    const drugForm = document.getElementById('drug-interaction-form');
    const drug1Input = document.getElementById('drug1');
    const drug2Input = document.getElementById('drug2');
    const resultContainer = document.getElementById('interaction-result');
    const drugChips = document.querySelectorAll('.drug-chip');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    // Example drug click handler
    if (drugChips) {
        drugChips.forEach(chip => {
            chip.addEventListener('click', function() {
                const drugName = this.textContent.trim();
                
                // If drug1 is empty, fill it, otherwise fill drug2
                if (!drug1Input.value) {
                    drug1Input.value = drugName;
                } else if (!drug2Input.value) {
                    drug2Input.value = drugName;
                } else {
                    // If both are filled, replace drug2
                    drug2Input.value = drugName;
                }
            });
        });
    }
    
    // Form submission handler
    if (drugForm) {
        drugForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const drug1 = drug1Input.value.trim();
            const drug2 = drug2Input.value.trim();
            
            if (!drug1 || !drug2) {
                showNotification('Please enter both drugs', 'warning');
                return;
            }
            
            // Show loading spinner
            if (loadingSpinner) {
                loadingSpinner.classList.remove('hidden');
            }
            if (resultContainer) {
                resultContainer.innerHTML = '';
            }
            
            // Create form data
            const formData = new FormData();
            formData.append('drug1', drug1);
            formData.append('drug2', drug2);
            
            // Send request to check interactions
            fetch('/check_interaction', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (loadingSpinner) {
                    loadingSpinner.classList.add('hidden');
                }
                
                displayInteractionResult(data);
            })
            .catch(error => {
                console.error('Error checking drug interaction:', error);
                if (loadingSpinner) {
                    loadingSpinner.classList.add('hidden');
                }
                showNotification('An error occurred while checking drug interactions', 'danger');
            });
        });
    }
    
    // Function to display interaction results
    function displayInteractionResult(data) {
        if (!resultContainer) return;
        
        resultContainer.innerHTML = '';
        resultContainer.classList.add('slide-in-right');
        
        if (data.error) {
            resultContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> ${data.error}
                </div>
            `;
            return;
        }
        
        if (data.interaction) {
            const severityClass = getSeverityClass(data.severity);
            
            resultContainer.innerHTML = `
                <h3 class="mb-2">Interaction Found</h3>
                <div class="alert ${severityClass} mb-2">
                    <strong>Severity:</strong> ${data.severity || 'Unknown'}
                </div>
                <div class="mb-2">
                    <strong>Drug A:</strong> ${data.drug1}
                </div>
                <div class="mb-2">
                    <strong>Drug B:</strong> ${data.drug2}
                </div>
                <div class="mb-2">
                    <strong>Description:</strong>
                    <p>${data.description || 'No detailed description available.'}</p>
                </div>
                <div>
                    <strong>Recommendation:</strong>
                    <p>${getRecommendationByInteraction(data.severity) || 'Consult your healthcare provider for guidance.'}</p>
                </div>
            `;
        } else {
            resultContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> No known interaction found between ${data.drug1} and ${data.drug2}.
                </div>
                <p class="mt-2">Always consult with a healthcare professional about all medications you are taking.</p>
            `;
        }
    }
    
    // Helper function to get severity class
    function getSeverityClass(severity) {
        if (!severity) return 'alert-warning';
        
        severity = severity.toLowerCase();
        if (severity.includes('major') || severity.includes('severe')) {
            return 'alert-danger';
        } else if (severity.includes('moderate')) {
            return 'alert-warning';
        } else if (severity.includes('minor') || severity.includes('mild')) {
            return 'alert-success';
        } else {
            return 'alert-warning';
        }
    }
    
    // Helper function to get recommendation based on interaction severity
    function getRecommendationByInteraction(severity) {
        if (!severity) return null;
        
        severity = severity.toLowerCase();
        if (severity.includes('major') || severity.includes('severe')) {
            return 'Avoid using these medications together. Consult your healthcare provider immediately.';
        } else if (severity.includes('moderate')) {
            return 'Use these medications together with caution. Monitor for side effects and consult your healthcare provider.';
        } else if (severity.includes('minor') || severity.includes('mild')) {
            return 'The benefits of using these medications together may outweigh the risks. Monitor for any unusual symptoms.';
        } else {
            return 'Consult your healthcare provider for guidance regarding these medications.';
        }
    }
});
