/**
 * Chart Manager Module
 * Handles rendering visualizations using Chart.js and Plotly
 */

class ChartManager {
    constructor() {
        this.charts = new Map(); // Map of container ID to chart instance
        this.chartColors = [
            '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe',
            '#fa709a', '#fee140', '#30cfd0', '#a8edea', '#fed6e3'
        ];
    }

    /**
     * Render a chart in a container
     * @param {string} containerId - Container ID
     * @param {Object} chartConfig - Chart configuration from backend
     */
    renderChart(containerId, chartConfig) {
        const container = document.getElementById(`${containerId}_content`);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Clear existing content
        container.innerHTML = '';

        // Determine chart library and type
        if (chartConfig.chart_config && (chartConfig.chart_config.data || chartConfig.chart_config.layout)) {
            // Plotly chart (from existing functions)
            this.renderPlotlyChart(container, chartConfig);
        } else if (chartConfig.table_data) {
            // Data table
            this.renderDataTable(container, chartConfig);
        } else {
            // Chart.js chart (for new implementations)
            this.renderChartJS(container, chartConfig);
        }

        // Update container metadata in grid manager
        if (window.gridManager) {
            const containerData = window.gridManager.containers.get(containerId);
            if (containerData) {
                containerData.contentType = chartConfig.chart_type || 'chart';
                containerData.content = chartConfig;
            }
        }
    }

    /**
     * Render Plotly chart (compatibility with existing backend)
     */
    renderPlotlyChart(container, chartConfig) {
        // Create div for Plotly
        const plotDiv = document.createElement('div');
        plotDiv.style.width = '100%';
        plotDiv.style.height = '100%';
        container.appendChild(plotDiv);

        try {
            // Use Plotly to render
            const config = chartConfig.chart_config;
            const layout = {
                ...config.layout,
                autosize: true,
                margin: { l: 40, r: 40, t: 40, b: 40 }
            };

            Plotly.newPlot(plotDiv, config.data, layout, {
                responsive: true,
                displayModeBar: false
            });

            // Store reference
            this.charts.set(container.id, {
                type: 'plotly',
                instance: plotDiv,
                config: chartConfig
            });
        } catch (error) {
            console.error('Error rendering Plotly chart:', error);
            container.innerHTML = `<p class="error">Error rendering chart: ${error.message}</p>`;
        }
    }

    /**
     * Render Chart.js chart
     */
    renderChartJS(container, chartConfig) {
        // Create canvas for Chart.js
        const canvas = document.createElement('canvas');
        canvas.className = 'chart-canvas';
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');

        try {
            let chartJsConfig;

            // Convert chart type to Chart.js format
            switch (chartConfig.type) {
                case 'line':
                    chartJsConfig = this.createLineChartConfig(chartConfig);
                    break;
                case 'bar':
                    chartJsConfig = this.createBarChartConfig(chartConfig);
                    break;
                case 'pie':
                    chartJsConfig = this.createPieChartConfig(chartConfig);
                    break;
                case 'scatter':
                    chartJsConfig = this.createScatterChartConfig(chartConfig);
                    break;
                case 'doughnut':
                    chartJsConfig = this.createDoughnutChartConfig(chartConfig);
                    break;
                default:
                    throw new Error(`Unsupported chart type: ${chartConfig.type}`);
            }

            // Create Chart.js instance
            const chart = new Chart(ctx, chartJsConfig);

            // Store reference
            this.charts.set(container.id, {
                type: 'chartjs',
                instance: chart,
                config: chartConfig
            });
        } catch (error) {
            console.error('Error rendering Chart.js chart:', error);
            container.innerHTML = `<p class="error">Error rendering chart: ${error.message}</p>`;
        }
    }

    /**
     * Create Chart.js line chart configuration
     */
    createLineChartConfig(config) {
        return {
            type: 'line',
            data: {
                labels: config.labels || [],
                datasets: config.datasets || [{
                    label: config.label || 'Dataset',
                    data: config.data || [],
                    borderColor: this.chartColors[0],
                    backgroundColor: this.chartColors[0] + '20',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: !!config.title,
                        text: config.title
                    },
                    legend: {
                        display: config.showLegend !== false
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: !!config.xLabel,
                            text: config.xLabel
                        }
                    },
                    y: {
                        title: {
                            display: !!config.yLabel,
                            text: config.yLabel
                        }
                    }
                }
            }
        };
    }

    /**
     * Create Chart.js bar chart configuration
     */
    createBarChartConfig(config) {
        return {
            type: 'bar',
            data: {
                labels: config.labels || [],
                datasets: config.datasets || [{
                    label: config.label || 'Dataset',
                    data: config.data || [],
                    backgroundColor: this.chartColors,
                    borderColor: this.chartColors.map(c => c + 'dd'),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: !!config.title,
                        text: config.title
                    },
                    legend: {
                        display: config.showLegend !== false
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: !!config.xLabel,
                            text: config.xLabel
                        }
                    },
                    y: {
                        title: {
                            display: !!config.yLabel,
                            text: config.yLabel
                        },
                        beginAtZero: true
                    }
                }
            }
        };
    }

    /**
     * Create Chart.js pie chart configuration
     */
    createPieChartConfig(config) {
        return {
            type: 'pie',
            data: {
                labels: config.labels || [],
                datasets: [{
                    data: config.data || [],
                    backgroundColor: this.chartColors,
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: !!config.title,
                        text: config.title
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };
    }

    /**
     * Create Chart.js scatter chart configuration
     */
    createScatterChartConfig(config) {
        return {
            type: 'scatter',
            data: {
                datasets: config.datasets || [{
                    label: config.label || 'Dataset',
                    data: config.data || [],
                    backgroundColor: this.chartColors[0],
                    borderColor: this.chartColors[0] + 'dd'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: !!config.title,
                        text: config.title
                    },
                    legend: {
                        display: config.showLegend !== false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: !!config.xLabel,
                            text: config.xLabel
                        }
                    },
                    y: {
                        title: {
                            display: !!config.yLabel,
                            text: config.yLabel
                        }
                    }
                }
            }
        };
    }

    /**
     * Create Chart.js doughnut chart configuration
     */
    createDoughnutChartConfig(config) {
        const pieConfig = this.createPieChartConfig(config);
        pieConfig.type = 'doughnut';
        return pieConfig;
    }

    /**
     * Render data table
     */
    renderDataTable(container, tableConfig) {
        const tableData = tableConfig.table_data || [];
        const columns = tableConfig.columns || (tableData.length > 0 ? Object.keys(tableData[0]) : []);

        // Create table element
        const tableWrapper = document.createElement('div');
        tableWrapper.className = 'table-wrapper';
        tableWrapper.style.overflow = 'auto';
        tableWrapper.style.height = '100%';

        const table = document.createElement('table');
        table.className = 'data-table';
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';

        // Create header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            th.style.padding = '12px';
            th.style.backgroundColor = '#f8f9fa';
            th.style.borderBottom = '2px solid #dee2e6';
            th.style.textAlign = 'left';
            th.style.fontWeight = '600';
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create body
        const tbody = document.createElement('tbody');
        tableData.forEach((row, index) => {
            const tr = document.createElement('tr');
            if (index % 2 === 0) {
                tr.style.backgroundColor = '#f8f9fa';
            }
            columns.forEach(col => {
                const td = document.createElement('td');
                td.textContent = row[col] !== null && row[col] !== undefined ? row[col] : '';
                td.style.padding = '10px 12px';
                td.style.borderBottom = '1px solid #dee2e6';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        tableWrapper.appendChild(table);
        container.appendChild(tableWrapper);

        // Store reference
        this.charts.set(container.id, {
            type: 'table',
            instance: table,
            config: tableConfig
        });
    }

    /**
     * Update chart data
     */
    updateChart(containerId, newData) {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) return;

        if (chartInfo.type === 'chartjs') {
            // Update Chart.js chart
            chartInfo.instance.data = newData;
            chartInfo.instance.update();
        } else if (chartInfo.type === 'plotly') {
            // Update Plotly chart
            Plotly.react(chartInfo.instance, newData.data, newData.layout);
        }
    }

    /**
     * Destroy chart
     */
    destroyChart(containerId) {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) return;

        if (chartInfo.type === 'chartjs') {
            chartInfo.instance.destroy();
        } else if (chartInfo.type === 'plotly') {
            Plotly.purge(chartInfo.instance);
        }

        this.charts.delete(containerId);
    }

    /**
     * Resize all charts (call when container size changes)
     */
    resizeAllCharts() {
        for (const [containerId, chartInfo] of this.charts) {
            if (chartInfo.type === 'plotly') {
                Plotly.Plots.resize(chartInfo.instance);
            }
            // Chart.js auto-resizes with responsive: true
        }
    }

    /**
     * Export chart as image
     */
    exportChart(containerId, format = 'png') {
        const chartInfo = this.charts.get(containerId);
        if (!chartInfo) return;

        if (chartInfo.type === 'chartjs') {
            // Export Chart.js chart
            const url = chartInfo.instance.toBase64Image();
            this.downloadImage(url, `chart_${containerId}.${format}`);
        } else if (chartInfo.type === 'plotly') {
            // Export Plotly chart
            Plotly.downloadImage(chartInfo.instance, {
                format: format,
                width: 1000,
                height: 600,
                filename: `chart_${containerId}`
            });
        }
    }

    /**
     * Helper to download image
     */
    downloadImage(url, filename) {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// Create global instance
window.chartManager = new ChartManager();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartManager;
} 