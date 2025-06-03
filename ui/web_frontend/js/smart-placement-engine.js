/**
 * Smart Placement Engine
 * Implements Smart Best-Fit with Reorganization algorithm
 */

class SmartPlacementEngine {
    constructor(gridSize = 3) {
        this.gridSize = gridSize;
        this.totalCells = gridSize * gridSize;
    }

    /**
     * Main placement function with reorganization capability
     */
    findOptimalPlacement(containers, newContainerRequirements) {
        // Try normal placement first (without reorganization)
        const normalPlacement = this.tryNormalPlacement(containers, newContainerRequirements);
        if (normalPlacement) {
            return {
                success: true,
                reorganizationNeeded: false,
                placement: normalPlacement,
                newLayout: [...containers, normalPlacement]
            };
        }

        // Normal placement failed - need reorganization
        return this.performReorganization(containers, newContainerRequirements);
    }

    /**
     * Try to place new container without reorganizing existing ones
     */
    tryNormalPlacement(existingContainers, requirements) {
        const occupiedGrid = this.createOccupiedGrid(existingContainers);
        const availableSpaces = this.findAvailableRectangles(occupiedGrid);
        
        const optimalSize = this.determineOptimalSize(requirements.contentType, availableSpaces);
        if (!optimalSize) return null;

        const suitableSpaces = availableSpaces.filter(space => 
            space.width >= optimalSize.width && space.height >= optimalSize.height
        );

        if (suitableSpaces.length === 0) return null;

        // Use best-fit: minimize wasted space
        const bestSpace = suitableSpaces.reduce((best, current) => {
            const currentWaste = (current.width * current.height) - (optimalSize.width * optimalSize.height);
            const bestWaste = (best.width * best.height) - (optimalSize.width * optimalSize.height);
            return currentWaste < bestWaste ? current : best;
        });

        return {
            id: requirements.id || `container_${Date.now()}`,
            title: requirements.title || 'New Container',
            startRow: bestSpace.startRow,
            startCol: bestSpace.startCol,
            endRow: bestSpace.startRow + optimalSize.height - 1,
            endCol: bestSpace.startCol + optimalSize.width - 1,
            width: optimalSize.width,
            height: optimalSize.height,
            contentType: requirements.contentType
        };
    }

    /**
     * Perform complete reorganization to accommodate new container
     */
    performReorganization(existingContainers, newRequirements) {
        const totalContainers = existingContainers.length + 1;
        
        // Generate all possible size combinations
        const sizeCombinations = this.generateSizeCombinations(totalContainers);
        
        // Generate all possible layouts for each size combination
        const allLayouts = [];
        for (const sizes of sizeCombinations) {
            const layouts = this.generateLayoutsForSizes(sizes, existingContainers, newRequirements);
            allLayouts.push(...layouts);
        }

        if (allLayouts.length === 0) {
            return {
                success: false,
                error: "No valid reorganization found"
            };
        }

        // Score and select best layout
        const scoredLayouts = allLayouts.map(layout => ({
            ...layout,
            score: this.scoreLayout(layout.containers)
        }));

        const bestLayout = scoredLayouts.reduce((best, current) => 
            current.score < best.score ? current : best
        );

        return {
            success: true,
            reorganizationNeeded: true,
            newLayout: bestLayout.containers,
            score: bestLayout.score,
            reorganizationDetails: {
                totalLayouts: allLayouts.length,
                wastedCells: this.totalCells - bestLayout.containers.reduce((sum, c) => sum + c.width * c.height, 0)
            }
        };
    }

    /**
     * Generate all possible ways to divide total cells among containers
     */
    generateSizeCombinations(containerCount) {
        const combinations = [];
        this.generatePartitions(this.totalCells, containerCount, [], combinations);
        
        // Convert cell counts to valid width/height combinations
        const validCombinations = [];
        for (const partition of combinations) {
            const sizeSets = partition.map(cellCount => this.cellCountToSizes(cellCount));
            
            // Generate cartesian product of all size options
            const cartesianProduct = this.cartesianProduct(sizeSets);
            validCombinations.push(...cartesianProduct);
        }

        return validCombinations;
    }

    /**
     * Generate all partitions of n into k parts
     */
    generatePartitions(n, k, current, results) {
        if (k === 1) {
            if (n > 0) {
                results.push([...current, n]);
            }
            return;
        }

        for (let i = 1; i <= n - k + 1; i++) {
            current.push(i);
            this.generatePartitions(n - i, k - 1, current, results);
            current.pop();
        }
    }

    /**
     * Convert cell count to possible width/height combinations
     */
    cellCountToSizes(cellCount) {
        const sizes = [];
        for (let width = 1; width <= this.gridSize; width++) {
            for (let height = 1; height <= this.gridSize; height++) {
                if (width * height === cellCount) {
                    sizes.push({ width, height });
                }
            }
        }
        return sizes.length > 0 ? sizes : [{ width: 1, height: 1 }]; // Fallback
    }

    /**
     * Generate cartesian product of arrays
     */
    cartesianProduct(arrays) {
        return arrays.reduce((acc, curr) => {
            const result = [];
            acc.forEach(a => {
                curr.forEach(c => {
                    result.push([...a, c]);
                });
            });
            return result;
        }, [[]]);
    }

    /**
     * Generate all possible layouts for given size combination
     */
    generateLayoutsForSizes(sizes, existingContainers, newRequirements) {
        const layouts = [];
        
        // Try all possible arrangements using backtracking
        this.placeContainersRecursively(
            sizes, 
            0, 
            new Array(this.gridSize).fill(null).map(() => new Array(this.gridSize).fill(false)),
            [],
            layouts,
            existingContainers,
            newRequirements
        );

        return layouts;
    }

    /**
     * Recursively place containers using backtracking
     */
    placeContainersRecursively(sizes, containerIndex, grid, currentLayout, results, existingContainers, newRequirements) {
        if (containerIndex === sizes.length) {
            // All containers placed successfully
            const containers = this.createContainerObjects(currentLayout, existingContainers, newRequirements);
            results.push({ containers });
            return;
        }

        const { width, height } = sizes[containerIndex];

        // Try placing current container at every possible position
        for (let row = 0; row <= this.gridSize - height; row++) {
            for (let col = 0; col <= this.gridSize - width; col++) {
                if (this.canPlaceAt(grid, row, col, width, height)) {
                    // Place container
                    this.markOccupied(grid, row, col, width, height, true);
                    currentLayout.push({ 
                        containerIndex, 
                        startRow: row, 
                        startCol: col, 
                        width, 
                        height 
                    });

                    // Recursively place remaining containers
                    this.placeContainersRecursively(sizes, containerIndex + 1, grid, currentLayout, results, existingContainers, newRequirements);

                    // Backtrack
                    this.markOccupied(grid, row, col, width, height, false);
                    currentLayout.pop();
                }
            }
        }
    }

    /**
     * Check if container can be placed at position
     */
    canPlaceAt(grid, startRow, startCol, width, height) {
        for (let r = startRow; r < startRow + height; r++) {
            for (let c = startCol; c < startCol + width; c++) {
                if (grid[r][c]) return false;
            }
        }
        return true;
    }

    /**
     * Mark grid cells as occupied/free
     */
    markOccupied(grid, startRow, startCol, width, height, occupied) {
        for (let r = startRow; r < startRow + height; r++) {
            for (let c = startCol; c < startCol + width; c++) {
                grid[r][c] = occupied;
            }
        }
    }

    /**
     * Create container objects from layout positions
     */
    createContainerObjects(layout, existingContainers, newRequirements) {
        const containers = [];
        
        layout.forEach((position, index) => {
            if (index < existingContainers.length) {
                // Existing container (possibly resized/moved)
                const existing = existingContainers[index];
                containers.push({
                    ...existing,
                    startRow: position.startRow,
                    startCol: position.startCol,
                    endRow: position.startRow + position.height - 1,
                    endCol: position.startCol + position.width - 1,
                    width: position.width,
                    height: position.height
                });
            } else {
                // New container
                containers.push({
                    id: newRequirements.id || `container_${Date.now()}`,
                    title: newRequirements.title || 'New Container',
                    startRow: position.startRow,
                    startCol: position.startCol,
                    endRow: position.startRow + position.height - 1,
                    endCol: position.startCol + position.width - 1,
                    width: position.width,
                    height: position.height,
                    contentType: newRequirements.contentType || 'generic'
                });
            }
        });

        return containers;
    }

    /**
     * Score layout quality (lower is better)
     */
    scoreLayout(containers) {
        const usedCells = containers.reduce((sum, c) => sum + c.width * c.height, 0);
        const wastedCells = this.totalCells - usedCells;
        
        // Additional penalties
        const fragmentationPenalty = this.calculateFragmentationPenalty(containers);
        const aspectRatioPenalty = this.calculateAspectRatioPenalty(containers);
        
        return wastedCells + fragmentationPenalty + aspectRatioPenalty;
    }

    /**
     * Calculate fragmentation penalty
     */
    calculateFragmentationPenalty(containers) {
        const grid = this.createOccupiedGrid(containers);
        const freeRegions = this.findFreeRegions(grid);
        
        // Penalize many small regions
        return freeRegions.filter(region => region.size < 2).length * 0.5;
    }

    /**
     * Calculate aspect ratio penalty
     */
    calculateAspectRatioPenalty(containers) {
        return containers.reduce((penalty, container) => {
            const aspectRatio = Math.max(container.width, container.height) / Math.min(container.width, container.height);
            return penalty + (aspectRatio > 3 ? 0.3 : 0); // Penalize very elongated containers
        }, 0);
    }

    /**
     * Create occupied grid from containers
     */
    createOccupiedGrid(containers) {
        const grid = new Array(this.gridSize).fill(null).map(() => new Array(this.gridSize).fill(false));
        
        containers.forEach(container => {
            for (let r = container.startRow; r <= container.endRow; r++) {
                for (let c = container.startCol; c <= container.endCol; c++) {
                    grid[r][c] = true;
                }
            }
        });

        return grid;
    }

    /**
     * Find available rectangles in grid
     */
    findAvailableRectangles(occupiedGrid) {
        const rectangles = [];

        for (let row = 0; row < this.gridSize; row++) {
            for (let col = 0; col < this.gridSize; col++) {
                if (!occupiedGrid[row][col]) {
                    // Try all possible rectangle sizes from this starting point
                    for (let width = 1; width <= this.gridSize - col; width++) {
                        for (let height = 1; height <= this.gridSize - row; height++) {
                            if (this.isRectangleFree(occupiedGrid, row, col, width, height)) {
                                rectangles.push({
                                    startRow: row,
                                    startCol: col,
                                    width: width,
                                    height: height,
                                    area: width * height
                                });
                            }
                        }
                    }
                }
            }
        }

        return rectangles;
    }

    /**
     * Check if rectangle area is free
     */
    isRectangleFree(grid, startRow, startCol, width, height) {
        for (let r = startRow; r < startRow + height; r++) {
            for (let c = startCol; c < startCol + width; c++) {
                if (grid[r][c]) return false;
            }
        }
        return true;
    }

    /**
     * Find connected free regions
     */
    findFreeRegions(grid) {
        const visited = new Array(this.gridSize).fill(null).map(() => new Array(this.gridSize).fill(false));
        const regions = [];

        for (let row = 0; row < this.gridSize; row++) {
            for (let col = 0; col < this.gridSize; col++) {
                if (!grid[row][col] && !visited[row][col]) {
                    const region = this.exploreRegion(grid, visited, row, col);
                    regions.push(region);
                }
            }
        }

        return regions;
    }

    /**
     * Explore connected free region using DFS
     */
    exploreRegion(grid, visited, startRow, startCol) {
        const stack = [[startRow, startCol]];
        const cells = [];

        while (stack.length > 0) {
            const [row, col] = stack.pop();
            
            if (row < 0 || row >= this.gridSize || col < 0 || col >= this.gridSize ||
                visited[row][col] || grid[row][col]) {
                continue;
            }

            visited[row][col] = true;
            cells.push([row, col]);

            // Add adjacent cells
            stack.push([row + 1, col], [row - 1, col], [row, col + 1], [row, col - 1]);
        }

        return { size: cells.length, cells };
    }

    /**
     * Determine optimal size for content type
     */
    determineOptimalSize(contentType, availableSpaces) {
        const sizePreferences = {
            'line_chart': [{ width: 2, height: 1 }, { width: 2, height: 2 }, { width: 1, height: 2 }],
            'bar_chart': [{ width: 1, height: 2 }, { width: 2, height: 1 }, { width: 2, height: 2 }],
            'scatter_plot': [{ width: 2, height: 2 }, { width: 2, height: 1 }, { width: 1, height: 2 }],
            'kpi_card': [{ width: 1, height: 1 }],
            'data_table': [{ width: 1, height: 2 }, { width: 2, height: 2 }, { width: 1, height: 3 }],
            'heatmap': [{ width: 2, height: 2 }],
            'generic': [{ width: 1, height: 1 }, { width: 2, height: 1 }, { width: 1, height: 2 }]
        };

        const preferences = sizePreferences[contentType] || sizePreferences['generic'];

        // Try each preferred size in order
        for (const preferredSize of preferences) {
            const fittingSpaces = availableSpaces.filter(space =>
                space.width >= preferredSize.width && space.height >= preferredSize.height
            );

            if (fittingSpaces.length > 0) {
                return preferredSize;
            }
        }

        return null; // No suitable size found
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SmartPlacementEngine;
}

// Make available globally
window.SmartPlacementEngine = SmartPlacementEngine; 