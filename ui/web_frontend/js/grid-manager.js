/**
 * Grid Manager Module
 * Handles dynamic grid layout, container placement, and grid configuration
 */

class GridManager {
    constructor() {
        this.gridSize = 3; // 3x3 grid
        this.containers = new Map(); // Map of container ID to container data
        this.gridCells = []; // Array of grid cell elements
        this.gridContainer = null;
        this.selectedCells = new Set(); // For custom grid design
        this.isDesigning = false;
        this.dragStart = null;
        this.smartEngine = new SmartPlacementEngine(this.gridSize); // Smart placement engine
        this.init();
    }

    init() {
        this.gridContainer = document.getElementById('gridContainer');
        this.setupGrid();
        this.setupEventListeners();
    }

    setupGrid() {
        // Clear existing grid
        this.gridContainer.innerHTML = '';
        this.gridCells = [];

        // Create 3x3 grid cells
        for (let row = 0; row < this.gridSize; row++) {
            for (let col = 0; col < this.gridSize; col++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                cell.dataset.index = row * this.gridSize + col;
                
                // Add subtle label for empty cells
                const label = document.createElement('span');
                label.className = 'cell-label';
                label.textContent = `${row + 1},${col + 1}`;
                label.style.opacity = '0.3';
                label.style.fontSize = '0.75rem';
                cell.appendChild(label);

                this.gridContainer.appendChild(cell);
                this.gridCells.push(cell);
            }
        }
    }

    setupEventListeners() {
        // Grid configuration button
        document.getElementById('gridConfigBtn').addEventListener('click', () => {
            this.showGridConfig();
        });

        // Clear grid button
        document.getElementById('clearGridBtn').addEventListener('click', () => {
            this.clearGrid();
        });

        // Grid cell click handlers for custom placement
        this.gridCells.forEach(cell => {
            cell.addEventListener('click', (e) => {
                if (!e.target.closest('.visualization-container')) {
                    this.handleCellClick(cell);
                }
            });
        });
    }

    handleCellClick(cell) {
        // This will be used by AI to specify where to place containers
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        console.log(`Cell clicked at (${row}, ${col})`);
    }

    /**
     * Add a container using smart placement algorithm
     * @param {Object} config - Container configuration
     * @returns {string} Container ID or placement result
     */
    addContainer(config = {}) {
        // If specific position is provided, use legacy method
        if (config.startRow !== undefined && config.startCol !== undefined) {
            return this.addContainerAtPosition(config);
        }

        // Use smart placement algorithm
        return this.addSmartContainer(config);
    }

    /**
     * Add container using smart placement with reorganization
     */
    addSmartContainer(config = {}) {
        const {
            title = 'Container',
            id = `container_${Date.now()}`,
            contentType = 'generic'
        } = config;

        // Get current containers in smart engine format
        const currentContainers = Array.from(this.containers.values()).map(container => ({
            id: container.id,
            title: container.title,
            startRow: container.startRow,
            startCol: container.startCol,
            endRow: container.endRow,
            endCol: container.endCol,
            width: container.endCol - container.startCol + 1,
            height: container.endRow - container.startRow + 1,
            contentType: container.contentType || 'generic'
        }));

        // Use smart placement engine
        const placementResult = this.smartEngine.findOptimalPlacement(currentContainers, {
            id,
            title,
            contentType
        });

        if (!placementResult.success) {
            throw new Error(placementResult.error || 'Could not place container');
        }

        // Apply the new layout
        this.applySmartLayoutResult(placementResult);

        // Log placement details
        console.log('Smart Placement Result:', {
            reorganizationNeeded: placementResult.reorganizationNeeded,
            totalContainers: placementResult.newLayout.length,
            details: placementResult.reorganizationDetails
        });

        return id;
    }

    /**
     * Apply smart layout result to the grid
     */
    applySmartLayoutResult(placementResult) {
        // Clear current grid
        this.clearGridSilently();

        // Add all containers from the new layout
        placementResult.newLayout.forEach(containerData => {
            const container = this.createContainerElement(containerData.id, containerData.title);
            
            // Calculate grid area
            const gridArea = `${containerData.startRow + 1} / ${containerData.startCol + 1} / ${containerData.endRow + 2} / ${containerData.endCol + 2}`;
            container.style.gridArea = gridArea;

            // Store container data
            this.containers.set(containerData.id, {
                id: containerData.id,
                title: containerData.title,
                startRow: containerData.startRow,
                startCol: containerData.startCol,
                endRow: containerData.endRow,
                endCol: containerData.endCol,
                element: container,
                content: null,
                contentType: containerData.contentType,
                width: containerData.width,
                height: containerData.height
            });

            // Mark cells as occupied
            this.markCellsOccupied(
                containerData.startRow, 
                containerData.startCol, 
                containerData.endRow, 
                containerData.endCol, 
                containerData.id
            );

            // Add to grid
            this.gridContainer.appendChild(container);
        });

        // Update container count
        this.updateContainerCount();

        // Show reorganization notification if needed
        if (placementResult.reorganizationNeeded) {
            this.showReorganizationNotification(placementResult.reorganizationDetails);
        }
    }

    /**
     * Legacy method for adding container at specific position
     */
    addContainerAtPosition(config = {}) {
        const {
            startRow = 0,
            startCol = 0,
            endRow = startRow,
            endCol = startCol,
            title = 'Container',
            id = `container_${Date.now()}`
        } = config;

        // Validate position
        if (!this.isValidPosition(startRow, startCol, endRow, endCol)) {
            throw new Error('Invalid container position');
        }

        // Check if cells are available
        if (!this.areCellsAvailable(startRow, startCol, endRow, endCol)) {
            throw new Error('Selected cells are already occupied');
        }

        // Create container element
        const container = this.createContainerElement(id, title);
        
        // Calculate grid area
        const gridArea = `${startRow + 1} / ${startCol + 1} / ${endRow + 2} / ${endCol + 2}`;
        container.style.gridArea = gridArea;

        // Store container data
        this.containers.set(id, {
            id,
            title,
            startRow,
            startCol,
            endRow,
            endCol,
            element: container,
            content: null,
            contentType: null
        });

        // Mark cells as occupied
        this.markCellsOccupied(startRow, startCol, endRow, endCol, id);

        // Add to grid
        this.gridContainer.appendChild(container);

        // Update container count
        this.updateContainerCount();

        return id;
    }

    /**
     * Create container DOM element
     */
    createContainerElement(id, title) {
        const container = document.createElement('div');
        container.className = 'visualization-container';
        container.id = id;
        container.innerHTML = `
            <div class="container-content" id="${id}_content">
                <div class="placeholder-image">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="3" y="3" width="18" height="18" rx="2" stroke="#cbd5e1" stroke-width="1.5" fill="none"/>
                        <circle cx="8.5" cy="8.5" r="1.5" fill="#cbd5e1"/>
                        <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <p class="placeholder-text">${title}</p>
                </div>
            </div>
        `;
        return container;
    }

    /**
     * Remove a container from the grid
     */
    removeContainer(containerId) {
        const containerData = this.containers.get(containerId);
        if (!containerData) return;

        // Remove DOM element
        containerData.element.remove();

        // Mark cells as available
        this.markCellsAvailable(
            containerData.startRow,
            containerData.startCol,
            containerData.endRow,
            containerData.endCol
        );

        // Remove from containers map
        this.containers.delete(containerId);

        // Update container count
        this.updateContainerCount();

        // Notify backend if needed
        if (window.websocketClient && window.websocketClient.connected) {
            window.websocketClient.send({
                type: 'container_removed',
                containerId: containerId
            });
        }
    }

    /**
     * Clear all containers from the grid
     */
    clearGrid() {
        this.clearGridSilently();

        // Notify backend
        if (window.websocketClient && window.websocketClient.connected) {
            window.websocketClient.send({
                type: 'grid_cleared'
            });
        }
    }

    /**
     * Clear grid without notifications (for internal use)
     */
    clearGridSilently() {
        // Remove all containers
        for (const [id, container] of this.containers) {
            container.element.remove();
        }
        
        // Clear containers map
        this.containers.clear();

        // Reset all cells
        this.gridCells.forEach(cell => {
            cell.classList.remove('occupied');
            delete cell.dataset.containerId;
        });

        // Update container count
        this.updateContainerCount();
    }

    /**
     * Show reorganization notification
     */
    showReorganizationNotification(details) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'reorganization-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">🔄</span>
                <span class="notification-text">
                    Grid reorganized for optimal layout! 
                    ${details.wastedCells === 0 ? 'Perfect fit achieved.' : `${details.wastedCells} cells unused.`}
                </span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Apply smart layout presets
     */
    applySmartLayout(preset) {
        this.clearGrid();

        switch (preset) {
            case 'dashboard':
                this.addContainer({ title: 'Main Dashboard', contentType: 'generic' });
                break;

            case 'analytics':
                this.addContainer({ title: 'Key Metrics', contentType: 'kpi_card' });
                this.addContainer({ title: 'Trend Analysis', contentType: 'line_chart' });
                break;

            case 'comparison':
                this.addContainer({ title: 'Dataset A', contentType: 'bar_chart' });
                this.addContainer({ title: 'Dataset B', contentType: 'bar_chart' });
                break;

            case 'detailed':
                this.addContainer({ title: 'Overview', contentType: 'kpi_card' });
                this.addContainer({ title: 'Main Chart', contentType: 'line_chart' });
                this.addContainer({ title: 'Data Table', contentType: 'data_table' });
                break;

            case 'custom':
                this.showCustomGridDesigner();
                break;
        }

        // Close modal if not custom
        if (preset !== 'custom') {
            this.closeGridConfig();
        }
    }

    /**
     * Show grid configuration modal
     */
    showGridConfig() {
        const modal = document.getElementById('gridConfigModal');
        modal.style.display = 'flex';
    }

    /**
     * Close grid configuration modal
     */
    closeGridConfig() {
        const modal = document.getElementById('gridConfigModal');
        modal.style.display = 'none';
        document.getElementById('customGridConfig').style.display = 'none';
    }

    /**
     * Show custom grid designer
     */
    showCustomGridDesigner() {
        document.getElementById('customGridConfig').style.display = 'block';
        this.initGridDesigner();
    }

    /**
     * Initialize grid designer for custom layouts
     */
    initGridDesigner() {
        const designer = document.getElementById('gridDesigner');
        designer.innerHTML = '';
        this.selectedCells.clear();

        // Create designer grid
        for (let i = 0; i < 9; i++) {
            const cell = document.createElement('div');
            cell.className = 'designer-cell';
            cell.dataset.designIndex = i;
            
            // Mouse events for drag selection
            cell.addEventListener('mousedown', (e) => this.startDragSelection(e, i));
            cell.addEventListener('mouseenter', (e) => this.updateDragSelection(e, i));
            cell.addEventListener('mouseup', (e) => this.endDragSelection(e));
            
            designer.appendChild(cell);
        }

        // Add create button
        const createBtn = document.createElement('button');
        createBtn.className = 'btn btn-primary';
        createBtn.textContent = 'Create Container';
        createBtn.style.marginTop = '1rem';
        createBtn.onclick = () => this.createCustomContainer();
        designer.parentElement.appendChild(createBtn);
    }

    /**
     * Handle drag selection in grid designer
     */
    startDragSelection(e, index) {
        e.preventDefault();
        this.isDesigning = true;
        this.dragStart = index;
        this.selectedCells.clear();
        this.selectedCells.add(index);
        this.updateDesignerDisplay();
    }

    updateDragSelection(e, index) {
        if (!this.isDesigning) return;
        
        // Calculate rectangle from drag start to current
        const startRow = Math.floor(this.dragStart / 3);
        const startCol = this.dragStart % 3;
        const currentRow = Math.floor(index / 3);
        const currentCol = index % 3;
        
        const minRow = Math.min(startRow, currentRow);
        const maxRow = Math.max(startRow, currentRow);
        const minCol = Math.min(startCol, currentCol);
        const maxCol = Math.max(startCol, currentCol);
        
        // Select all cells in rectangle
        this.selectedCells.clear();
        for (let row = minRow; row <= maxRow; row++) {
            for (let col = minCol; col <= maxCol; col++) {
                this.selectedCells.add(row * 3 + col);
            }
        }
        
        this.updateDesignerDisplay();
    }

    endDragSelection(e) {
        this.isDesigning = false;
    }

    updateDesignerDisplay() {
        const cells = document.querySelectorAll('.designer-cell');
        cells.forEach((cell, index) => {
            if (this.selectedCells.has(index)) {
                cell.classList.add('selected');
            } else {
                cell.classList.remove('selected');
            }
        });
    }

    /**
     * Create container from custom selection
     */
    createCustomContainer() {
        if (this.selectedCells.size === 0) {
            alert('Please select cells for the container');
            return;
        }

        // Calculate bounds
        const indices = Array.from(this.selectedCells);
        const rows = indices.map(i => Math.floor(i / 3));
        const cols = indices.map(i => i % 3);
        
        const startRow = Math.min(...rows);
        const endRow = Math.max(...rows);
        const startCol = Math.min(...cols);
        const endCol = Math.max(...cols);

        // Add container
        try {
            this.addContainer({
                startRow,
                startCol,
                endRow,
                endCol,
                title: `Custom Container ${this.containers.size + 1}`
            });
            
            // Clear selection
            this.selectedCells.clear();
            this.updateDesignerDisplay();
            
            // Close modal
            this.closeGridConfig();
        } catch (error) {
            alert(error.message);
        }
    }

    /**
     * Utility methods
     */
    isValidPosition(startRow, startCol, endRow, endCol) {
        return startRow >= 0 && startCol >= 0 && 
               endRow < this.gridSize && endCol < this.gridSize &&
               startRow <= endRow && startCol <= endCol;
    }

    areCellsAvailable(startRow, startCol, endRow, endCol) {
        for (let row = startRow; row <= endRow; row++) {
            for (let col = startCol; col <= endCol; col++) {
                const cell = this.gridCells[row * this.gridSize + col];
                if (cell.classList.contains('occupied')) {
                    return false;
                }
            }
        }
        return true;
    }

    markCellsOccupied(startRow, startCol, endRow, endCol, containerId) {
        for (let row = startRow; row <= endRow; row++) {
            for (let col = startCol; col <= endCol; col++) {
                const cell = this.gridCells[row * this.gridSize + col];
                cell.classList.add('occupied');
                cell.dataset.containerId = containerId;
            }
        }
    }

    markCellsAvailable(startRow, startCol, endRow, endCol) {
        for (let row = startRow; row <= endRow; row++) {
            for (let col = startCol; col <= endCol; col++) {
                const cell = this.gridCells[row * this.gridSize + col];
                cell.classList.remove('occupied');
                delete cell.dataset.containerId;
            }
        }
    }

    updateContainerCount() {
        document.getElementById('containerCount').textContent = this.containers.size;
    }

    /**
     * Get grid state for AI
     */
    getGridState() {
        const state = {
            gridSize: this.gridSize,
            containers: []
        };

        for (const [id, container] of this.containers) {
            state.containers.push({
                id,
                title: container.title,
                position: {
                    startRow: container.startRow,
                    startCol: container.startCol,
                    endRow: container.endRow,
                    endCol: container.endCol
                },
                contentType: container.contentType
            });
        }

        return state;
    }

    /**
     * Add container from position description (for AI)
     */
    addContainerFromDescription(description) {
        // Parse descriptions like "bottom right", "top left corner", etc.
        const position = this.parsePositionDescription(description);
        return this.addContainer(position);
    }

    parsePositionDescription(description) {
        const desc = description.toLowerCase();
        
        // Define position mappings
        const positions = {
            'top left': { startRow: 0, startCol: 0, endRow: 2, endCol: 2 },
            'top center': { startRow: 0, startCol: 2, endRow: 2, endCol: 3 },
            'top right': { startRow: 0, startCol: 3, endRow: 2, endCol: 5 },
            'middle left': { startRow: 2, startCol: 0, endRow: 3, endCol: 2 },
            'center': { startRow: 2, startCol: 2, endRow: 3, endCol: 3 },
            'middle right': { startRow: 2, startCol: 3, endRow: 3, endCol: 5 },
            'bottom left': { startRow: 3, startCol: 0, endRow: 5, endCol: 2 },
            'bottom center': { startRow: 3, startCol: 2, endRow: 5, endCol: 3 },
            'bottom right': { startRow: 3, startCol: 3, endRow: 5, endCol: 5 },
            // Full spans
            'top': { startRow: 0, startCol: 0, endRow: 2, endCol: 5 },
            'bottom': { startRow: 3, startCol: 0, endRow: 5, endCol: 5 },
            'left': { startRow: 0, startCol: 0, endRow: 5, endCol: 2 },
            'right': { startRow: 0, startCol: 3, endRow: 5, endCol: 5 },
            'full': { startRow: 0, startCol: 0, endRow: 5, endCol: 5 }
        };

        // Find best match
        for (const [key, pos] of Object.entries(positions)) {
            if (desc.includes(key)) {
                return pos;
            }
        }

        // Default to center
        return positions.center;
    }
}

// Create global instance
window.gridManager = new GridManager();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GridManager;
} 