/**
 * Main Application Entry Point
 * Initializes all modules and handles global interactions
 */

// Global application state
window.appState = {
    conversationId: null,
    isInitialized: false,
    config: {
        apiEndpoint: '/api',
        wsEndpoint: '/ws',
        debugMode: true
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    console.log('Initializing AI Data Analyst...');

    try {
        // Initialize modules (they auto-instantiate)
        // GridManager, ChartManager, ChatInterface, WebSocketClient are already created

        // Setup global event handlers
        setupGlobalEventHandlers();

        // Setup grid templates
        setupGridTemplates();

        // Initialize with a default layout
        setTimeout(() => {
            if (window.gridManager.containers.size === 0) {
                // Start with a simple analytics layout
                window.gridManager.applySmartLayout('analytics');
            }
        }, 500);

        // Mark as initialized
        window.appState.isInitialized = true;
        console.log('Application initialized successfully');

    } catch (error) {
        console.error('Error initializing application:', error);
        showError('Failed to initialize application. Please refresh the page.');
    }
}

/**
 * Setup global event handlers
 */
function setupGlobalEventHandlers() {
    // Window resize handler
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (window.chartManager) {
                window.chartManager.resizeAllCharts();
            }
        }, 250);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K: Focus chat input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('chatInput')?.focus();
        }

        // Escape: Close modals
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });

    // Handle visibility change (tab switching)
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && window.websocketClient && !window.websocketClient.isConnected()) {
            console.log('Page visible, attempting to reconnect WebSocket...');
            window.websocketClient.connect();
        }
    });
}

/**
 * Setup grid template functions
 */
function setupGridTemplates() {
    // Make smart layout functions globally available
    window.applySmartLayout = (preset) => {
        window.gridManager.applySmartLayout(preset);
    };

    window.closeGridConfig = () => {
        window.gridManager.closeGridConfig();
    };

    // Test function for smart placement
    window.testSmartPlacement = () => {
        console.log('🧠 Testing Smart Placement Algorithm...');
        
        // Check if gridManager is available
        if (!window.gridManager) {
            console.error('❌ GridManager not available');
            alert('GridManager not initialized yet. Please wait a moment and try again.');
            return;
        }

        // Check if smart engine is available
        if (!window.gridManager.smartEngine) {
            console.error('❌ Smart Placement Engine not available');
            alert('Smart Placement Engine not initialized. Please refresh the page.');
            return;
        }

        console.log('✅ Smart Placement Engine ready');
        
        // Clear grid first
        window.gridManager.clearGrid();
        
        // Add containers one by one to test the algorithm
        setTimeout(() => {
            console.log('🔍 Adding first container (line_chart)...');
            try {
                window.gridManager.addContainer({ 
                    title: 'Sales Trends', 
                    contentType: 'line_chart' 
                });
                console.log('✅ First container added successfully');
            } catch (error) {
                console.error('❌ Error adding first container:', error);
            }
        }, 500);
        
        setTimeout(() => {
            console.log('🔍 Adding second container (kpi_card)...');
            try {
                window.gridManager.addContainer({ 
                    title: 'Key Metrics', 
                    contentType: 'kpi_card' 
                });
                console.log('✅ Second container added successfully');
            } catch (error) {
                console.error('❌ Error adding second container:', error);
            }
        }, 1500);
        
        setTimeout(() => {
            console.log('🔍 Adding third container (bar_chart)...');
            try {
                window.gridManager.addContainer({ 
                    title: 'Category Analysis', 
                    contentType: 'bar_chart' 
                });
                console.log('✅ Third container added successfully');
            } catch (error) {
                console.error('❌ Error adding third container:', error);
            }
        }, 2500);
        
        setTimeout(() => {
            console.log('🔍 Adding fourth container (data_table)...');
            try {
                window.gridManager.addContainer({ 
                    title: 'Data Details', 
                    contentType: 'data_table' 
                });
                console.log('✅ Fourth container added successfully');
                console.log('🎉 Smart Placement Algorithm test completed!');
            } catch (error) {
                console.error('❌ Error adding fourth container:', error);
            }
        }, 3500);
        
        // Close the modal if it's open
        if (window.gridManager.closeGridConfig) {
            window.gridManager.closeGridConfig();
        }
        
        // Show notification
        console.log('🧠 Smart Placement Algorithm test started!');
        
        // Also add a simple test first
        setTimeout(() => {
            console.log('🔧 Testing basic container addition...');
            try {
                const testId = window.gridManager.addContainer({ 
                    title: 'Debug Test', 
                    contentType: 'generic' 
                });
                console.log('✅ Basic test successful, container ID:', testId);
            } catch (error) {
                console.error('❌ Basic test failed:', error);
                console.error('Error details:', error.stack);
            }
        }, 100);
    };
}

/**
 * Close all modals
 */
function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
}

/**
 * Show error message
 */
function showError(message) {
    if (window.chatInterface) {
        window.chatInterface.addSystemMessage(`❌ ${message}`);
    } else {
        alert(message);
    }
}

/**
 * Show success message
 */
function showSuccess(message) {
    if (window.chatInterface) {
        window.chatInterface.addSystemMessage(`✅ ${message}`);
    }
}

/**
 * Export current dashboard
 */
window.exportDashboard = () => {
    const dashboardData = {
        version: '1.0.0',
        exportedAt: new Date().toISOString(),
        gridState: window.gridManager.getGridState(),
        charts: []
    };

    // Collect chart data
    for (const [containerId, containerData] of window.gridManager.containers) {
        if (containerData.content) {
            dashboardData.charts.push({
                containerId,
                title: containerData.title,
                content: containerData.content
            });
        }
    }

    // Download as JSON
    const blob = new Blob([JSON.stringify(dashboardData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showSuccess('Dashboard exported successfully');
};

/**
 * Import dashboard from file
 */
window.importDashboard = async (file) => {
    try {
        const text = await file.text();
        const dashboardData = JSON.parse(text);

        // Clear current grid
        window.gridManager.clearGrid();

        // Recreate containers
        for (const container of dashboardData.gridState.containers) {
            const containerId = window.gridManager.addContainer({
                startRow: container.position.startRow,
                startCol: container.position.startCol,
                endRow: container.position.endRow,
                endCol: container.position.endCol,
                title: container.title,
                id: container.id
            });
        }

        // Restore charts
        for (const chartData of dashboardData.charts) {
            if (window.gridManager.containers.has(chartData.containerId)) {
                window.chartManager.renderChart(chartData.containerId, chartData.content);
            }
        }

        showSuccess('Dashboard imported successfully');
    } catch (error) {
        console.error('Error importing dashboard:', error);
        showError('Failed to import dashboard. Please check the file format.');
    }
};

/**
 * Debug utilities
 */
if (window.appState.config.debugMode) {
    window.debug = {
        // Get current grid state
        getGridState: () => window.gridManager.getGridState(),
        
        // Get all containers
        getContainers: () => Array.from(window.gridManager.containers.values()),
        
        // Get all charts
        getCharts: () => Array.from(window.chartManager.charts.entries()),
        
        // Send test message
        sendTestMessage: (message) => {
            window.chatInterface.handleUserMessage();
            window.chatInterface.chatInput.value = message;
            window.chatInterface.handleUserMessage();
        },
        
        // Add test container
        addTestContainer: () => {
            const id = window.gridManager.addContainer({
                startRow: 0,
                startCol: 0,
                endRow: 2,
                endCol: 2,
                title: 'Test Container'
            });
            console.log('Added test container:', id);
            return id;
        },
        
        // Create test chart
        createTestChart: (containerId) => {
            const testData = {
                type: 'bar',
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                data: [65, 59, 80, 81, 56],
                title: 'Test Chart',
                xLabel: 'Months',
                yLabel: 'Values'
            };
            window.chartManager.renderChart(containerId, testData);
        }
    };

    console.log('Debug utilities available at window.debug');
}

/**
 * Sample data for testing (remove in production)
 */
window.sampleActions = {
    createSampleDashboard: () => {
        // Clear grid
        window.gridManager.clearGrid();
        
        // Create quadrant layout
        window.gridManager.applyGridTemplate('quadrants');
        
        // Get container IDs
        const containers = Array.from(window.gridManager.containers.keys());
        
        // Create sample charts
        if (containers[0]) {
            window.chartManager.renderChart(containers[0], {
                type: 'line',
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                data: [30, 45, 60, 70, 85, 95],
                title: 'Sales Growth',
                xLabel: 'Month',
                yLabel: 'Sales ($k)'
            });
        }
        
        if (containers[1]) {
            window.chartManager.renderChart(containers[1], {
                type: 'pie',
                labels: ['Product A', 'Product B', 'Product C', 'Product D'],
                data: [30, 25, 20, 25],
                title: 'Product Distribution'
            });
        }
        
        if (containers[2]) {
            window.chartManager.renderChart(containers[2], {
                type: 'bar',
                labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                data: [120, 150, 180, 200],
                title: 'Quarterly Revenue',
                xLabel: 'Quarter',
                yLabel: 'Revenue ($k)'
            });
        }
        
        if (containers[3]) {
            window.chartManager.renderChart(containers[3], {
                table_data: [
                    { Metric: 'Total Sales', Value: '$545,000', Change: '+12%' },
                    { Metric: 'New Customers', Value: '1,234', Change: '+5%' },
                    { Metric: 'Avg Order Value', Value: '$89', Change: '+8%' },
                    { Metric: 'Conversion Rate', Value: '3.2%', Change: '+0.5%' }
                ],
                columns: ['Metric', 'Value', 'Change']
            });
        }
        
        showSuccess('Sample dashboard created');
    }
};

console.log('AI Data Analyst application loaded');
console.log('For sample dashboard, run: sampleActions.createSampleDashboard()'); 