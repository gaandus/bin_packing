document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const form = document.getElementById('binPackingForm');
    const saveConfigBtn = document.getElementById('saveConfig');
    const loadConfigBtn = document.getElementById('loadConfig');
    const configsModal = new bootstrap.Modal(document.getElementById('configsModal'));
    const configsList = document.getElementById('configsList');
    const darkModeToggle = document.getElementById('darkModeToggle');
    const randomWeightsBtn = document.getElementById('randomWeights');
    const randomWeightOptions = document.getElementById('randomWeightOptions');
    const generateWeightsBtn = document.getElementById('generateWeights');
    const includeLabelsCheckbox = document.getElementById('includeLabels');
    const compareButton = document.getElementById('compareButton');
    const closeComparisonBtn = document.getElementById('closeComparison');
    const balanceBinsRadio = document.getElementById('balanceBins');
    const binCountContainer = document.getElementById('binCountContainer');
    const backToTopBtn = document.getElementById('backToTop');
    
    // Back to top button handler
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) { // Show button after scrolling down 300px
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });
    
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Show/hide bin count input based on balance_bins objective
    document.querySelectorAll('input[name="objective"]').forEach(radio => {
        radio.addEventListener('change', function() {
            binCountContainer.style.display = this.value === 'balance_bins' ? 'block' : 'none';
        });
    });
    
    // Toggle dark mode
    darkModeToggle.addEventListener('click', function() {
        const htmlElement = document.documentElement;
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        htmlElement.setAttribute('data-bs-theme', newTheme);
        
        // Update button icon
        const iconElement = darkModeToggle.querySelector('i');
        if (newTheme === 'dark') {
            iconElement.classList.remove('bi-moon-fill');
            iconElement.classList.add('bi-sun-fill');
            darkModeToggle.setAttribute('title', 'Switch to Light Mode');
        } else {
            iconElement.classList.remove('bi-sun-fill');
            iconElement.classList.add('bi-moon-fill');
            darkModeToggle.setAttribute('title', 'Switch to Dark Mode');
        }
        
        // Save preference to localStorage
        localStorage.setItem('theme', newTheme);
    });
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        
        // Update button icon based on saved theme
        const iconElement = darkModeToggle.querySelector('i');
        if (savedTheme === 'dark') {
            iconElement.classList.remove('bi-moon-fill');
            iconElement.classList.add('bi-sun-fill');
            darkModeToggle.setAttribute('title', 'Switch to Light Mode');
        } else {
            darkModeToggle.setAttribute('title', 'Switch to Dark Mode');
        }
    } else {
        darkModeToggle.setAttribute('title', 'Switch to Dark Mode');
    }
    
    // Toggle random weight options
    randomWeightsBtn.addEventListener('click', function() {
        if (randomWeightOptions.style.display === 'none') {
            randomWeightOptions.style.display = 'block';
        } else {
            randomWeightOptions.style.display = 'none';
        }
    });
    
    // Generate random weights
    generateWeightsBtn.addEventListener('click', function() {
        const count = parseInt(document.getElementById('randomWeightCount').value) || 10;
        const min = parseInt(document.getElementById('randomWeightMin').value) || 1;
        const max = parseInt(document.getElementById('randomWeightMax').value) || 20;
        const includeLabels = document.getElementById('includeLabels').checked;
        
        if (count > 100) {
            alert('Maximum 100 weights allowed');
            return;
        }
        
        if (min >= max) {
            alert('Min value must be less than max value');
            return;
        }
        
        // Generate random weights
        const weights = [];
        for (let i = 0; i < count; i++) {
            weights.push(Math.floor(Math.random() * (max - min + 1)) + min);
        }
        
        // Set weights in form
        document.getElementById('weights').value = weights.join(', ');
        
        // Generate labels if requested
        if (includeLabels) {
            const labels = [];
            for (let i = 0; i < count; i++) {
                labels.push(`Item ${i+1}`);
            }
            document.getElementById('itemLabels').value = labels.join(', ');
        }
        
        // Hide options
        randomWeightOptions.style.display = 'none';
    });
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Hide comparison results if they're showing
        document.getElementById('comparisonCard').style.display = 'none';
        
        // Parse input values
        const data = getFormData();
        
        // Solve bin packing problem
        solveBinPacking(data);
    });
    
    // Compare strategies
    compareButton.addEventListener('click', function() {
        // Parse input values
        const data = getFormData();
        
        // Compare strategies
        compareStrategies(data);
    });
    
    // Close comparison view
    closeComparisonBtn.addEventListener('click', function() {
        document.getElementById('comparisonCard').style.display = 'none';
        document.getElementById('resultsCard').style.display = 'block';
    });
    
    // Helper function to get form data
    function getFormData() {
        const weightsStr = document.getElementById('weights').value;
        const weights = weightsStr.split(',').map(w => parseInt(w.trim())).filter(w => !isNaN(w));
        
        // Parse item labels if provided
        const labelsStr = document.getElementById('itemLabels').value;
        let labels = [];
        if (labelsStr.trim()) {
            labels = labelsStr.split(',').map(l => l.trim());
            // Pad with empty labels if needed
            while (labels.length < weights.length) {
                labels.push(`Item ${labels.length + 1}`);
            }
        }
        
        const binCapacity = parseInt(document.getElementById('binCapacity').value);
        const objective = document.querySelector('input[name="objective"]:checked').value;
        const minItems = parseInt(document.getElementById('minItems').value);
        const sortMethod = document.getElementById('sortItems').value;
        const binCount = parseInt(document.getElementById('binCount').value);
        
        // Prepare data
        return {
            weights: weights,
            item_labels: labels,
            bin_capacity: binCapacity,
            objective: objective,
            min_items_per_bin: minItems,
            sort_method: sortMethod,
            bin_count: binCount
        };
    }
    
    // Save configuration
    saveConfigBtn.addEventListener('click', function() {
        // Get form data
        const data = getFormData();
        saveConfiguration(data);
    });
    
    // Load configurations
    loadConfigBtn.addEventListener('click', function() {
        loadConfigurations();
    });
});

// Solve bin packing problem
function solveBinPacking(data) {
    // Call API
    fetch('/api/solve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            alert(result.error);
            return;
        }
        
        // Display results
        displayResults(result, data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while solving the problem.');
    });
}

// Compare different strategies
function compareStrategies(data) {
    // Hide regular results
    document.getElementById('resultsCard').style.display = 'none';
    
    // Show loading indicator
    document.getElementById('comparisonCard').style.display = 'block';
    document.getElementById('comparisonResults').innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Comparing strategies...</p></div>';
    
    // Call API
    fetch('/api/compare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            alert(result.error);
            document.getElementById('comparisonCard').style.display = 'none';
            return;
        }
        
        // Display comparison results
        displayComparison(result, data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while comparing strategies.');
        document.getElementById('comparisonCard').style.display = 'none';
    });
}

// Display comparison results
function displayComparison(result, data) {
    const comparisonResults = document.getElementById('comparisonResults');
    comparisonResults.innerHTML = '';
    
    // Get strategy names and results
    const strategies = Object.keys(result.results);
    const results = result.results;
    
    // Create comparison table
    const table = document.createElement('table');
    table.className = 'table table-bordered table-striped table-hover';
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    // Add header cells
    headerRow.innerHTML = `
        <th>Strategy</th>
        <th>Bins Used</th>
        <th>Avg Fill %</th>
        <th>Status</th>
        <th>Actions</th>
    `;
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    // Map strategy codes to display names
    const strategyNames = {
        'min_bins': 'Minimize Bins',
        'max_weight': 'Maximize Weight',
        'max_items': 'Maximize Items',
        'balance_bins': 'Balance Weight'
    };
    
    // Add rows for each strategy
    strategies.forEach(strategy => {
        const strategyResult = results[strategy];
        const row = document.createElement('tr');
        
        if (strategyResult.success) {
            // Strategy succeeded
            row.innerHTML = `
                <td>${strategyNames[strategy]}</td>
                <td>${strategyResult.bin_count}</td>
                <td>${(strategyResult.avg_fill_ratio * 100).toFixed(1)}%</td>
                <td>${strategyResult.warning ? `<span class="text-warning"><i class="bi bi-exclamation-triangle"></i> ${strategyResult.warning}</span>` : '<span class="text-success"><i class="bi bi-check-circle"></i> Optimal</span>'}</td>
                <td><button class="btn btn-sm btn-outline-primary view-solution" data-strategy="${strategy}">View</button></td>
            `;
        } else {
            // Strategy failed
            row.innerHTML = `
                <td>${strategyNames[strategy]}</td>
                <td>-</td>
                <td>-</td>
                <td><span class="text-danger"><i class="bi bi-x-circle"></i> ${strategyResult.error}</span></td>
                <td>-</td>
            `;
        }
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    comparisonResults.appendChild(table);
    
    // Add "View Solution" button functionality
    document.querySelectorAll('.view-solution').forEach(button => {
        button.addEventListener('click', function() {
            const strategy = this.getAttribute('data-strategy');
            const strategyResult = results[strategy];
            
            // Hide comparison card and show results
            document.getElementById('comparisonCard').style.display = 'none';
            
            // Use the existing display function with the strategy's results
            const resultObject = {
                bins: strategyResult.bins,
                bin_count: strategyResult.bin_count,
                total_weight: strategyResult.total_weight,
                warning: strategyResult.warning
            };
            
            displayResults(resultObject, {...data, objective: strategy});
        });
    });
    
    // Add visualization of all strategies
    const visualizationContainer = document.createElement('div');
    visualizationContainer.className = 'mt-4';
    
    // Create accordion for visualizations
    const accordion = document.createElement('div');
    accordion.className = 'accordion';
    accordion.id = 'strategiesAccordion';
    
    // Add a section for each successful strategy
    strategies.forEach((strategy, index) => {
        const strategyResult = results[strategy];
        if (!strategyResult.success) return;
        
        const strategyCard = document.createElement('div');
        strategyCard.className = 'accordion-item';
        
        const strategyHeader = document.createElement('h2');
        strategyHeader.className = 'accordion-header';
        strategyHeader.innerHTML = `
            <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#strategy${index}">
                ${strategyNames[strategy]} (${strategyResult.bin_count} bins, ${(strategyResult.avg_fill_ratio * 100).toFixed(1)}% fill)
            </button>
        `;
        
        const strategyBody = document.createElement('div');
        strategyBody.id = `strategy${index}`;
        strategyBody.className = `accordion-collapse collapse ${index === 0 ? 'show' : ''}`;
        strategyBody.setAttribute('data-bs-parent', '#strategiesAccordion');
        
        const strategyContent = document.createElement('div');
        strategyContent.className = 'accordion-body';
        
        // Add visualization using a grid layout
        const vizContainer = document.createElement('div');
        vizContainer.className = 'strategy-visualization';
        
        // Determine bins per row
        const screenWidth = window.innerWidth;
        const binsPerRow = screenWidth < 576 ? 3 : 
                          screenWidth < 768 ? 4 : 
                          screenWidth < 992 ? 5 : 6;
        
        // Create a grid of rows and columns
        let currentRow = null;
        let binsInCurrentRow = 0;
        
        strategyResult.bins.forEach((bin, index) => {
            // Create a new row if needed
            if (index % binsPerRow === 0) {
                currentRow = document.createElement('div');
                currentRow.className = 'row justify-content-center mb-3';
                vizContainer.appendChild(currentRow);
                binsInCurrentRow = 0;
            }
            
            // Create a column for this bin
            const binColumn = document.createElement('div');
            const colWidth = Math.max(12 / binsPerRow, 3); // At least col-3
            binColumn.className = `col-${colWidth} col-sm-${colWidth} text-center`;
            
            // Create bin visualization
            const binContainer = createBinVisualization(bin, data);
            
            binColumn.appendChild(binContainer);
            currentRow.appendChild(binColumn);
            binsInCurrentRow++;
            
            // If we're at the last bin, add spacer columns if needed
            if (index === strategyResult.bins.length - 1 && binsInCurrentRow < binsPerRow) {
                const remainingCols = binsPerRow - binsInCurrentRow;
                for (let i = 0; i < remainingCols; i++) {
                    const spacerCol = document.createElement('div');
                    spacerCol.className = `col-${colWidth} col-sm-${colWidth}`;
                    currentRow.appendChild(spacerCol);
                }
            }
        });
        
        strategyContent.appendChild(vizContainer);
        strategyBody.appendChild(strategyContent);
        
        strategyCard.appendChild(strategyHeader);
        strategyCard.appendChild(strategyBody);
        accordion.appendChild(strategyCard);
    });
    
    visualizationContainer.appendChild(accordion);
    comparisonResults.appendChild(visualizationContainer);
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Display results
function displayResults(result, data) {
    const resultsSummary = document.getElementById('resultsSummary');
    const visualization = document.getElementById('visualization');
    const detailedResults = document.getElementById('detailedResults');
    
    // Show results card
    document.getElementById('resultsCard').style.display = 'block';
    
    // Display summary
    resultsSummary.innerHTML = `
        <p><strong>Number of Bins:</strong> ${result.bin_count}</p>
        <p><strong>Total Weight:</strong> ${result.total_weight}</p>
        <p><strong>Average Fill Rate:</strong> ${calculateAverageFillRate(result.bins).toFixed(2)}%</p>
    `;
    
    // Display sorting method if used
    if (data.sort_method && data.sort_method !== 'none') {
        const sortingText = {
            'desc': 'Sorted by weight (descending)',
            'asc': 'Sorted by weight (ascending)',
            'random': 'Randomly shuffled'
        }[data.sort_method];
        
        const sortInfoDiv = document.createElement('div');
        sortInfoDiv.className = 'alert alert-info mt-2 small';
        sortInfoDiv.innerHTML = `<i class="bi bi-info-circle"></i> ${sortingText}`;
        resultsSummary.appendChild(sortInfoDiv);
    }
    
    // Display warning if present
    if (result.warning) {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'alert alert-warning mt-2';
        warningDiv.innerHTML = `<strong>Note:</strong> ${result.warning}`;
        resultsSummary.appendChild(warningDiv);
    }
    
    // Display visualization - create a grid layout of bins
    visualization.innerHTML = '';
    
    // Responsive design - adjust item display based on screen size
    const isMobile = window.innerWidth < 576;
    
    // Determine how many bins to display per row based on screen width
    const screenWidth = window.innerWidth;
    const binsPerRow = screenWidth < 576 ? 3 : 
                       screenWidth < 768 ? 4 : 
                       screenWidth < 992 ? 5 : 6;
    
    // Create a container for each row
    let currentRow = null;
    let binsInCurrentRow = 0;
    
    result.bins.forEach((bin, index) => {
        // Create a new row if needed
        if (index % binsPerRow === 0) {
            currentRow = document.createElement('div');
            currentRow.className = 'row justify-content-center mb-3';
            visualization.appendChild(currentRow);
            binsInCurrentRow = 0;
        }
        
        // Create a column for this bin
        const binColumn = document.createElement('div');
        const colWidth = Math.max(12 / binsPerRow, 3); // Ensure column is at least col-3
        binColumn.className = `col-${colWidth} col-sm-${colWidth} text-center`;
        
        // Create bin container
        const binContainer = document.createElement('div');
        binContainer.className = 'bin-container';
        
        const binLabel = document.createElement('div');
        binLabel.className = 'bin-label';
        binLabel.textContent = `Bin ${bin.bin_id + 1}`;
        
        const binDiv = document.createElement('div');
        binDiv.className = 'bin';
        
        // Add items to bin
        let currentHeight = 0;
        bin.items.forEach((item, index) => {
            const itemWeight = bin.item_weights[index];
            const itemHeight = (itemWeight / bin.capacity) * 100; // As percentage of bin height
            
            const itemDiv = document.createElement('div');
            itemDiv.className = 'item';
            // Position from bottom of container
            itemDiv.style.height = `${itemHeight}%`;
            itemDiv.style.bottom = `${currentHeight}%`;
            itemDiv.style.backgroundColor = getRandomColor(item);
            
            // Display label or weight
            let itemText = itemWeight;
            if (bin.item_labels && bin.item_labels[index]) {
                // If we have labels, use them for tooltips
                itemDiv.setAttribute('data-bs-toggle', 'tooltip');
                itemDiv.setAttribute('data-bs-placement', 'top');
                itemDiv.setAttribute('title', `${bin.item_labels[index]}: ${itemWeight}`);
                
                // On mobile or for small items, still just show weight
                if (!isMobile && itemHeight > 15) {
                    itemText = bin.item_labels[index];
                }
            }
            
            // On mobile, only show text for larger items
            if (!isMobile || itemHeight > 10) {
                itemDiv.textContent = itemText;
            }
            
            binDiv.appendChild(itemDiv);
            currentHeight += itemHeight;
        });
        
        // Add fill rate label
        const fillRateDiv = document.createElement('div');
        fillRateDiv.className = 'fill-info';
        const fillRate = (bin.total_weight / bin.capacity) * 100;
        fillRateDiv.textContent = `${fillRate.toFixed(0)}% full`;
        
        binContainer.appendChild(binLabel);
        binContainer.appendChild(binDiv);
        binContainer.appendChild(fillRateDiv);
        
        binColumn.appendChild(binContainer);
        currentRow.appendChild(binColumn);
        binsInCurrentRow++;
        
        // If we have empty columns in the last row, add spacer columns
        if (index === result.bins.length - 1 && binsInCurrentRow < binsPerRow) {
            const remainingCols = binsPerRow - binsInCurrentRow;
            for (let i = 0; i < remainingCols; i++) {
                const spacerCol = document.createElement('div');
                spacerCol.className = `col-${colWidth} col-sm-${colWidth}`;
                currentRow.appendChild(spacerCol);
            }
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Scroll to results on mobile
    if (isMobile) {
        document.getElementById('resultsCard').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
    
    // Display detailed results
    displayDetailedResults(result.bins, detailedResults);
}

// Display detailed results in table format
function displayDetailedResults(bins, container) {
    container.innerHTML = '';
    
    bins.forEach(bin => {
        const binHeader = document.createElement('h6');
        binHeader.className = 'mt-3';
        binHeader.textContent = `Bin ${bin.bin_id + 1}`;
        
        const table = document.createElement('table');
        table.className = 'table table-sm table-striped';
        
        const tableHead = document.createElement('thead');
        tableHead.innerHTML = `
            <tr>
                <th>Item</th>
                <th>Weight</th>
            </tr>
        `;
        
        const tableBody = document.createElement('tbody');
        
        bin.items.forEach((item, index) => {
            const row = document.createElement('tr');
            
            // Use label if available, otherwise use item index
            const itemName = bin.item_labels && bin.item_labels[index] 
                ? bin.item_labels[index] 
                : `Item ${item}`;
            
            row.innerHTML = `
                <td>${itemName}</td>
                <td>${bin.item_weights[index]}</td>
            `;
            tableBody.appendChild(row);
        });
        
        // Summary row
        const summaryRow = document.createElement('tr');
        summaryRow.className = 'table-active';
        summaryRow.innerHTML = `
            <td><strong>Total</strong></td>
            <td><strong>${bin.total_weight} / ${bin.capacity} (${((bin.total_weight / bin.capacity) * 100).toFixed(0)}%)</strong></td>
        `;
        
        tableBody.appendChild(summaryRow);
        table.appendChild(tableHead);
        table.appendChild(tableBody);
        
        container.appendChild(binHeader);
        container.appendChild(table);
    });
}

// Save configuration
function saveConfiguration(data) {
    // Call API
    fetch('/api/save_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            alert(result.error);
            return;
        }
        
        alert('Configuration saved successfully!');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the configuration.');
    });
}

// Load configurations
function loadConfigurations() {
    // Call API to get configurations
    fetch('/api/load_configs')
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            alert(result.error);
            return;
        }
        
        // Display configurations
        displayConfigs(result.configs);
        document.getElementById('configsModal').classList.add('show');
        document.getElementById('configsModal').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while loading configurations.');
    });
}

// Display configurations
function displayConfigs(configs) {
    const configsList = document.getElementById('configsList');
    configsList.innerHTML = '';
    
    if (configs.length === 0) {
        configsList.innerHTML = '<div class="list-group-item">No saved configurations found.</div>';
        return;
    }
    
    configs.forEach(config => {
        const item = document.createElement('button');
        item.className = 'list-group-item list-group-item-action';
        
        let objectiveText = 'Unknown';
        if (config.objective === 'min_bins') {
            objectiveText = 'Minimize Bins';
        } else if (config.objective === 'max_weight') {
            objectiveText = 'Maximize Weight';
        } else if (config.objective === 'max_items') {
            objectiveText = 'Maximize Items';
        } else if (config.objective === 'balance_bins') {
            objectiveText = 'Balance Weight';
        }
        
        item.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">Bin Capacity: ${config.bin_capacity}</h5>
                <small>Items: ${config.weights.length}</small>
            </div>
            <p class="mb-1">Weights: ${config.weights.join(', ')}</p>
            <small>Objective: ${objectiveText}</small>
        `;
        
        item.addEventListener('click', function() {
            loadSelectedConfig(config);
            document.getElementById('configsModal').classList.remove('show');
            document.getElementById('configsModal').style.display = 'none';
        });
        
        configsList.appendChild(item);
    });
}

// Load selected configuration
function loadSelectedConfig(config) {
    document.getElementById('weights').value = config.weights.join(', ');
    document.getElementById('binCapacity').value = config.bin_capacity;
    document.querySelector(`input[value="${config.objective}"]`).checked = true;
    document.getElementById('minItems').value = config.min_items_per_bin || 1;
    
    // Handle optional parameters if available
    if (config.item_labels && config.item_labels.length > 0) {
        document.getElementById('itemLabels').value = config.item_labels.join(', ');
    }
    
    if (config.sort_method) {
        document.getElementById('sortItems').value = config.sort_method;
    }
    
    if (config.bin_count && config.objective === 'balance_bins') {
        document.getElementById('binCount').value = config.bin_count;
        document.getElementById('binCountContainer').style.display = 'block';
    } else {
        document.getElementById('binCountContainer').style.display = 'none';
    }
}

// Calculate average fill rate
function calculateAverageFillRate(bins) {
    if (bins.length === 0) return 0;
    
    const totalFillRate = bins.reduce((sum, bin) => {
        return sum + (bin.total_weight / bin.capacity) * 100;
    }, 0);
    
    return totalFillRate / bins.length;
}

// Generate consistent colors for items
function getRandomColor(seed) {
    // Use a simple hash function to get a consistent color based on the item index
    const hue = (seed * 137) % 360;
    return `hsl(${hue}, 70%, 60%)`;
}

// Check for viewport changes to refresh display
window.addEventListener('resize', function() {
    const resultsCard = document.getElementById('resultsCard');
    const comparisonCard = document.getElementById('comparisonCard');
    
    // Refresh results if displayed
    if (resultsCard.style.display !== 'none') {
        // If we have results displayed, we might want to refresh the visualization
        // However, for simplicity we'll skip full re-rendering in the resize handler
    }
    
    // Refresh comparison if displayed
    if (comparisonCard.style.display !== 'none') {
        // Similar to above, we could refresh the comparison visualization
    }
}, { passive: true });

// Create bin visualization for comparison view
function createBinVisualization(bin, data) {
    // Create container for the bin
    const binContainer = document.createElement('div');
    binContainer.className = 'bin-container';
    
    const binLabel = document.createElement('div');
    binLabel.className = 'bin-label';
    binLabel.textContent = `Bin ${bin.bin_id + 1}`;
    
    const binDiv = document.createElement('div');
    binDiv.className = 'bin';
    
    // Responsive design - adjust item display based on screen size
    const isMobile = window.innerWidth < 576;
    
    // Add items to bin
    let currentHeight = 0;
    bin.items.forEach((item, index) => {
        const itemWeight = bin.item_weights[index];
        const itemHeight = (itemWeight / bin.capacity) * 100; // As percentage of bin height
        
        const itemDiv = document.createElement('div');
        itemDiv.className = 'item';
        // Position from bottom of container
        itemDiv.style.height = `${itemHeight}%`;
        itemDiv.style.bottom = `${currentHeight}%`;
        itemDiv.style.backgroundColor = getRandomColor(item);
        
        // Display label or weight
        let itemText = itemWeight;
        if (bin.item_labels && bin.item_labels[index]) {
            // If we have labels, use them for tooltips
            itemDiv.setAttribute('data-bs-toggle', 'tooltip');
            itemDiv.setAttribute('data-bs-placement', 'top');
            itemDiv.setAttribute('title', `${bin.item_labels[index]}: ${itemWeight}`);
            
            // On mobile or for small items, still just show weight
            if (!isMobile && itemHeight > 15) {
                itemText = bin.item_labels[index];
            }
        }
        
        // On mobile, only show text for larger items
        if (!isMobile || itemHeight > 10) {
            itemDiv.textContent = itemText;
        }
        
        binDiv.appendChild(itemDiv);
        currentHeight += itemHeight;
    });
    
    // Add fill rate label
    const fillRateDiv = document.createElement('div');
    fillRateDiv.className = 'fill-info';
    const fillRate = (bin.total_weight / bin.capacity) * 100;
    fillRateDiv.textContent = `${fillRate.toFixed(0)}% full`;
    
    binContainer.appendChild(binLabel);
    binContainer.appendChild(binDiv);
    binContainer.appendChild(fillRateDiv);
    
    return binContainer;
} 