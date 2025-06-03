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
     * Add a container to the grid at specified position
     * @param {Object} config - Container configuration
     * @returns {string} Container ID
     */
    addContainer(config = {}) {
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
            <div class="container-header">
                <h3 class="container-title">${title}</h3>
                <div class="container-actions">
                    <button class="container-action" onclick="gridManager.moveContainer('${id}')" title="Move">
                        <span>↔️</span>
                    </button>
                    <button class="container-action" onclick="gridManager.resizeContainer('${id}')" title="Resize">
                        <span>📏</span>
                    </button>
                    <button class="container-action" onclick="gridManager.removeContainer('${id}')" title="Remove">
                        <span>🗑️</span>
                    </button>
                </div>
            </div>
            <div class="container-content" id="${id}_content">
                <p style="color: #adb5bd;">No content yet</p>
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

        // Notify backend
        if (window.websocketClient && window.websocketClient.connected) {
            window.websocketClient.send({
                type: 'grid_cleared'
            });
        }
    }

    /**
     * Apply a grid template
     */
    applyGridTemplate(template) {
        this.clearGrid();

        switch (template) {
            case 'single':
                this.addContainer({
                    startRow: 0, startCol: 0,
                    endRow: 2, endCol: 2,
                    title: 'Main Dashboard'
                });
                break;

            case 'two-columns':
                this.addContainer({
                    startRow: 0, startCol: 0,
                    endRow: 2, endCol: 0,
                    title: 'Left Panel'
                });
                this.addContainer({
                    startRow: 0, startCol: 1,
                    endRow: 2, endCol: 2,
                    title: 'Right Panel'
                });
                break;

            case 'two-rows':
                this.addContainer({
                    startRow: 0, startCol: 0,
                    endRow: 0, endCol: 2,
                    title: 'Top Panel'
                });
                this.addContainer({
                    startRow: 1, startCol: 0,
                    endRow: 2, endCol: 2,
                    title: 'Bottom Panel'
                });
                break;

            case 'quadrants':
                this.addContainer({
                    startRow: 0, startCol: 0,
                    endRow: 0, endCol: 0,
                    title: 'Top Left'
                });
                this.addContainer({
                    startRow: 0, startCol: 2,
                    endRow: 0, endCol: 2,
                    title: 'Top Right'
                });
                this.addContainer({
                    startRow: 2, startCol: 0,
                    endRow: 2, endCol: 0,
                    title: 'Bottom Left'
                });
                this.addContainer({
                    startRow: 2, startCol: 2,
                    endRow: 2, endCol: 2,
                    title: 'Bottom Right'
                });
                break;

            case 'three-columns':
                this.addContainer({
                    startRow: 0, startCol: 0,
                    endRow: 2, endCol: 0,
                    title: 'Left Column'
                });
                this.addContainer({
                    startRow: 0, startCol: 1,
                    endRow: 2, endCol: 1,
                    title: 'Center Column'
                });
                this.addContainer({
                    startRow: 0, startCol: 2,
                    endRow: 2, endCol: 2,
                    title: 'Right Column'
                });
                break;

            case 'custom':
                this.showCustomGridDesigner();
                break;
        }

        // Close modal if not custom
        if (template !== 'custom') {
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