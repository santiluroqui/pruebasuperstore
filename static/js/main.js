// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("main.js loaded and DOM fully parsed for new dashboard.");

    // --- Helper function to get theme color ---
    function getThemeColor(variable) {
        return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
    }

    // --- Funciones para dibujar gráficos D3.js ---
    // Usado en Dashboard (Ventas por Región, Top Productos, Categoría vs Subcategoría), Tiempo (Heatmap)
    function drawChartD3(data, elementId, config) {
        if (!data || data.length === 0) {
            console.warn(`No hay datos para dibujar el gráfico en ${elementId}.`);
            d3.select(`#${elementId}`).select("svg").html("<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='" + getThemeColor('--text-color') + "'>No hay datos disponibles</text>");
            return;
        }

        const container = d3.select(`#${elementId}`);
        const svg = container.select("svg");
        const margin = config.margin || {top: 40, right: 30, bottom: 80, left: 60};
        const width = +svg.attr("width") - margin.left - margin.right;
        const height = +svg.attr("height") - margin.top - margin.bottom;

        svg.selectAll("*").remove(); // Limpiar SVG anterior

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Título del gráfico
        g.append("text")
            .attr("x", (width / 2))             
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")  
            .style("font-size", "16px") 
            .style("font-weight", "bold")
            .style("fill", getThemeColor('--text-color'))
            .text(config.title);

        // Common axis styling
        function applyAxisStyles(axisG) {
            axisG.selectAll("path, line")
                .style("stroke", getThemeColor('--chart-text'));
            axisG.selectAll("text")
                .style("fill", getThemeColor('--chart-text'));
        }

        if (config.type === 'bar') {
            let x, y, xAxis, yAxis;

            if (config.horizontal) {
                x = d3.scaleLinear()
                    .range([0, width])
                    .domain([0, d3.max(data, d => d[config.yKey]) * 1.1]);

                y = d3.scaleBand()
                    .rangeRound([height, 0])
                    .padding(0.1)
                    .domain(data.map(d => d[config.xKey]));

                xAxis = d3.axisBottom(x).ticks(5, "s");
                yAxis = d3.axisLeft(y);

                applyAxisStyles(g.append("g")
                    .attr("class", "axis axis--x")
                    .attr("transform", `translate(0,${height})`)
                    .call(xAxis));

                applyAxisStyles(g.append("g")
                    .attr("class", "axis axis--y")
                    .call(yAxis));

                g.selectAll(".bar")
                    .data(data)
                    .enter().append("rect")
                        .attr("class", "bar")
                        .attr("x", 0)
                        .attr("y", d => y(d[config.xKey]))
                        .attr("width", d => x(d[config.yKey]))
                        .attr("height", y.bandwidth())
                        .attr("fill", getThemeColor('--sidebar-accent-color'));
            } else { // Vertical bars
                x = d3.scaleBand()
                    .rangeRound([0, width])
                    .padding(0.1)
                    .domain(data.map(d => d[config.xKey]));

                y = d3.scaleLinear()
                    .rangeRound([height, 0])
                    .domain([0, d3.max(data, d => d[config.yKey]) * 1.1]);

                xAxis = d3.axisBottom(x);
                yAxis = d3.axisLeft(y).ticks(5, "s");

                applyAxisStyles(g.append("g")
                    .attr("class", "axis axis--x")
                    .attr("transform", `translate(0,${height})`)
                    .call(xAxis)
                    .selectAll("text")
                        .attr("transform", "rotate(-45)")
                        .style("text-anchor", "end")
                        .attr("dx", "-.8em")
                        .attr("dy", ".15em"));

                applyAxisStyles(g.append("g")
                    .attr("class", "axis axis--y")
                    .call(yAxis));

                g.selectAll(".bar")
                    .data(data)
                    .enter().append("rect")
                        .attr("class", "bar")
                        .attr("x", d => x(d[config.xKey]))
                        .attr("y", d => y(d[config.yKey]))
                        .attr("width", x.bandwidth())
                        .attr("height", d => height - y(d[config.yKey]))
                        .attr("fill", getThemeColor('--sidebar-accent-color'));
            }
        } else if (config.type === 'bubble') {
            const categories = Array.from(new Set(data.map(d => d.category)));
            const subcategories = Array.from(new Set(data.map(d => d.sub_category)));

            let bubbleData = [];
            const nestedData = d3.group(data, d => d.category, d => d.sub_category);
            nestedData.forEach((sub_map, category) => {
                sub_map.forEach((value_arr, sub_category) => {
                    const total_sales = d3.sum(value_arr, d => d.total_sales);
                    bubbleData.push({
                        category: category,
                        sub_category: sub_category,
                        total_sales: total_sales
                    });
                });
            });

            const xScale = d3.scalePoint()
                .range([0, width])
                .padding(0.5)
                .domain(categories);

            const yScale = d3.scalePoint()
                .range([height, 0])
                .padding(0.5)
                .domain(subcategories);

            const rScale = d3.scaleSqrt()
                .range([5, 30])
                .domain([0, d3.max(bubbleData, d => d.total_sales)]);

            const colorScale = d3.scaleOrdinal(d3.schemeCategory10)
                .domain(categories);

            applyAxisStyles(g.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(xScale))
                .selectAll("text")
                    .attr("transform", "rotate(-30)")
                    .style("text-anchor", "end"));

            applyAxisStyles(g.append("g")
                .attr("class", "axis axis--y")
                .call(d3.axisLeft(yScale)));

            g.selectAll(".bubble")
                .data(bubbleData)
                .enter().append("circle")
                    .attr("class", "bubble")
                    .attr("cx", d => xScale(d.category))
                    .attr("cy", d => yScale(d.sub_category))
                    .attr("r", d => rScale(d.total_sales))
                    .attr("fill", d => colorScale(d.category))
                    .attr("opacity", 0.7)
                    .on("mouseover", function(event, d) {
                        d3.select(this).attr("stroke", "black").attr("stroke-width", 2);
                        const tooltip = d3.select("body").append("div")
                            .attr("class", "tooltip");
                        tooltip.transition()
                            .duration(200)
                            .style("opacity", .9);
                        tooltip.html(`Categoría: ${d.category}<br/>Subcategoría: ${d.sub_category}<br/>Ventas: $${d.total_sales.toFixed(2)}`)
                            .style("left", (event.pageX + 5) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    })
                    .on("mouseout", function(event, d) {
                        d3.select(this).attr("stroke", "none");
                        d3.selectAll(".tooltip").remove();
                    });
        } else if (config.type === 'heatmap') {
            const months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
            const days = Array.from({length: 31}, (_, i) => i + 1);

            const x = d3.scaleBand()
                .range([0, width])
                .domain(days)
                .padding(0.01);

            const y = d3.scaleBand()
                .range([height, 0])
                .domain(months.reverse()) // Reverse for Y-axis order
                .padding(0.01);

            const colorScale = d3.scaleSequential(d3.interpolateViridis)
                .domain([0, d3.max(data, d => d.value)]);

            applyAxisStyles(g.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(x)));

            applyAxisStyles(g.append("g")
                .attr("class", "axis axis--y")
                .call(d3.axisLeft(y)));

            g.selectAll(".cell")
                .data(data, d => `${d.month}:${d.day}`)
                .enter().append("rect")
                    .attr("x", d => x(d.day))
                    .attr("y", d => y(d.month))
                    .attr("width", x.bandwidth())
                    .attr("height", y.bandwidth())
                    .style("fill", d => colorScale(d.value))
                    .style("stroke", getThemeColor('--card-border'))
                    .style("stroke-width", 1)
                    .on("mouseover", function(event, d) {
                        d3.select(this).style("stroke", "black").style("stroke-width", 2);
                        const tooltip = d3.select("body").append("div")
                            .attr("class", "tooltip");
                        tooltip.transition()
                            .duration(200)
                            .style("opacity", .9);
                        tooltip.html(`Fecha: ${d.day} ${d.month}<br/>Ventas: $${d.value.toFixed(2)}`)
                            .style("left", (event.pageX + 5) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    })
                    .on("mouseout", function(event, d) {
                        d3.select(this).style("stroke", getThemeColor('--card-border')).style("stroke-width", 1);
                        d3.selectAll(".tooltip").remove();
                    });
        }
    }

    // --- Función para dibujar gráfico de Chart.js ---
    // Usado en Dashboard (Tendencia Temporal), Clientes (Pedidos por Segmento, Top Clientes), Productos (Ganancia vs Ventas), Regiones (Ventas/Ganancias por Estado, Top Ciudades), Tiempo (Ventas por Año/Mes, Ventas por Día de Semana)
    function drawChartJS(data, canvasId, chartType, chartOptions) {
        if (!data || data.length === 0) {
            console.warn(`No hay datos para dibujar el gráfico en ${canvasId}.`);
            const ctx = document.getElementById(canvasId);
            if (ctx) { // Asegurarse de que el canvas exista
                const parentDiv = ctx.parentElement;
                // Borrar canvas y añadir mensaje
                parentDiv.innerHTML = `<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='${getThemeColor('--text-color')}'>No hay datos disponibles</text><canvas id="${canvasId}" width="400" height="200"></canvas>`;
                return;
            }
        }

        const ctx = document.getElementById(canvasId);
        if (!ctx) return; // Si el canvas no existe, salir

        // Destruir instancia anterior si existe
        if (window[canvasId + 'Instance']) {
            window[canvasId + 'Instance'].destroy();
        }

        // Apply theme colors to chart options
        chartOptions.plugins = chartOptions.plugins || {};
        chartOptions.plugins.title = chartOptions.plugins.title || {};
        chartOptions.plugins.title.color = getThemeColor('--text-color');
        chartOptions.plugins.legend = chartOptions.plugins.legend || {};
        chartOptions.plugins.legend.labels = chartOptions.plugins.legend.labels || {};
        chartOptions.plugins.legend.labels.color = getThemeColor('--text-color');

        if (chartOptions.scales) {
            Object.values(chartOptions.scales).forEach(scale => {
                scale.grid = scale.grid || {};
                scale.grid.color = getThemeColor('--kpi-border');
                scale.ticks = scale.ticks || {};
                scale.ticks.color = getThemeColor('--chart-text');
                if (scale.title) {
                    scale.title.color = getThemeColor('--text-color');
                }
            });
        }

        window[canvasId + 'Instance'] = new Chart(ctx, {
            type: chartType,
            data: chartOptions.data,
            options: chartOptions.options
        });
    }

    // --- Función para obtener datos y dibujar gráficos del Dashboard General ---
    function loadDashboardCharts() {
        fetch('/api/sales_by_region')
            .then(response => response.json())
            .then(data => {
                drawChartD3(data, 'sales-by-region-chart', {
                    type: 'bar', xKey: 'region', yKey: 'total_sales', title: 'Ventas por Región', horizontal: false
                });
            })
            .catch(error => console.error('Error fetching sales by region:', error));

        fetch('/api/sales_trend')
            .then(response => response.json())
            .then(data => {
                drawChartJS(data, 'salesTrendCanvas', 'line', {
                    data: {
                        labels: data.map(d => d.month),
                        datasets: [{
                            label: 'Ventas ($)',
                            data: data.map(d => d.total_sales),
                            borderColor: getThemeColor('--sidebar-accent-color'),
                            backgroundColor: getThemeColor('--sidebar-accent-color') + '33', // 20% opacity
                            fill: true, tension: 0.1
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Tendencia de Ventas Mensual' } } }
                });
            })
            .catch(error => console.error('Error fetching sales trend:', error));
        
        fetch('/api/top_products')
            .then(response => response.json())
            .then(data => {
                drawChartD3(data, 'top-products-chart', {
                    type: 'bar', xKey: 'product_name', yKey: 'total_sales', title: 'Top 10 Productos Más Vendidos', horizontal: true
                });
            })
            .catch(error => console.error('Error fetching top products:', error));

        fetch('/api/category_subcategory_sales')
            .then(response => response.json())
            .then(data => {
                drawChartD3(data, 'category-subcategory-chart', {
                    type: 'bubble', title: 'Ventas por Categoría y Subcategoría'
                });
            })
            .catch(error => console.error('Error fetching category/subcategory sales:', error));
    }


    // --- Listener para cambios de tema (para actualizar colores de gráficos) ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme(newTheme); // applyTheme es global en base.html

            // Cambiar el icono del botón
            if (newTheme === 'dark') {
                themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            }

            // Un pequeño retraso para permitir que las variables CSS se actualicen
            setTimeout(() => {
                // Si estamos en el dashboard, recargar sus gráficos
                if (window.location.pathname === '/dashboard') {
                    loadDashboardCharts();
                } else if (window.location.pathname === '/clientes') {
                    // Recargar gráficos de clientes
                    loadCustomersCharts();
                } else if (window.location.pathname === '/productos') {
                    loadProductsCharts();
                } else if (window.location.pathname === '/regiones') {
                    loadRegionsCharts();
                } else if (window.location.pathname === '/tiempo') {
                    loadTimeCharts();
                }
            }, 100); 
        });

        // Establecer el icono inicial al cargar
        const initialTheme = document.documentElement.getAttribute('data-theme');
        if (initialTheme === 'dark') {
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }


    // --- Funciones para cargar gráficos de secciones específicas ---
    // Clientes
    function loadCustomersCharts() {
        fetch('/api/orders_by_segment')
            .then(response => response.json())
            .then(data => {
                drawChartJS(data, 'ordersBySegmentCanvas', 'doughnut', {
                    data: {
                        labels: data.map(d => d.segment),
                        datasets: [{
                            label: 'Cantidad de Pedidos',
                            data: data.map(d => d.order_count),
                            backgroundColor: [
                                'rgba(52, 152, 219, 0.8)', // Azul (Consumer)
                                'rgba(46, 204, 113, 0.8)', // Verde (Corporate)
                                'rgba(230, 126, 34, 0.8)'  // Naranja (Home Office)
                            ],
                            borderColor: [
                                'rgba(52, 152, 219, 1)',
                                'rgba(46, 204, 113, 1)',
                                'rgba(230, 126, 34, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' }, title: { display: true, text: 'Pedidos por Segmento de Cliente' } } }
                });
            })
            .catch(error => console.error('Error fetching orders by segment:', error));

        fetch('/api/top_customers_by_sales')
            .then(response => response.json())
            .then(data => {
                drawChartJS(data, 'topCustomersCanvas', 'bar', {
                    data: {
                        labels: data.map(d => d.customer_name),
                        datasets: [{
                            label: 'Ventas ($)',
                            data: data.map(d => d.total_sales),
                            backgroundColor: getThemeColor('--sidebar-accent-color'),
                            borderColor: getThemeColor('--sidebar-accent-color'),
                            borderWidth: 1
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false }, title: { display: true, text: 'Top 10 Clientes por Ventas' } }, scales: { x: { beginAtZero: true } } }
                });
            })
            .catch(error => console.error('Error fetching top customers by sales:', error));
    }

    // Productos
    function loadProductsCharts() {
        fetch('/api/profit_vs_sales_by_category')
            .then(response => response.json())
            .then(data => {
                const datasets = data.map(item => ({
                    label: item.category,
                    data: [{ x: item.sales, y: item.profit }],
                    backgroundColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.6)`,
                    borderColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`,
                    pointRadius: 8, pointHoverRadius: 10
                }));
                drawChartJS(data, 'profitVsSalesCategoryCanvas', 'scatter', {
                    data: { datasets: datasets },
                    options: { 
                        responsive: true, maintainAspectRatio: false, 
                        plugins: { 
                            title: { display: true, text: 'Ganancia vs Ventas por Categoría' }, 
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) { label += ': '; }
                                        label += `Ventas: $${context.parsed.x.toFixed(2)}, Ganancia: $${context.parsed.y.toFixed(2)}`;
                                        return label;
                                    }
                                }
                            }
                        }, 
                        scales: { x: { type: 'linear', position: 'bottom', title: { display: true, text: 'Ventas ($)' } }, y: { type: 'linear', position: 'left', title: { display: true, text: 'Ganancia ($)' } } }
                    }
                });
            })
            .catch(error => console.error('Error fetching profit vs sales by category:', error));
    }

    // Regiones
    function loadRegionsCharts() {
        fetch('/api/sales_profit_by_state')
            .then(response => response.json())
            .then(data => {
                drawChartJS(data, 'salesByStateCanvas', 'bar', {
                    data: {
                        labels: data.map(d => d.state),
                        datasets: [
                            { label: 'Ventas ($)', data: data.map(d => d.sales), backgroundColor: getThemeColor('--sidebar-accent-color') },
                            { label: 'Ganancia ($)', data: data.map(d => d.profit), backgroundColor: 'rgba(46, 204, 113, 0.8)' } // Green
                        ]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Ventas y Ganancias por Estado' } }, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } }
                });
            })
            .catch(error => console.error('Error fetching sales profit by state:', error));
        
        fetch('/api/top_cities_by_sales')
            .then(response => response.json())
            .then(data => {
                drawChartJS(data, 'topCitiesCanvas', 'bar', {
                    data: {
                        labels: data.map(d => `${d.city}, ${d.state}`),
                        datasets: [{
                            label: 'Ventas ($)',
                            data: data.map(d => d.sales),
                            backgroundColor: getThemeColor('--sidebar-accent-color')
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false }, title: { display: true, text: 'Top 20 Ciudades por Ventas' } }, scales: { x: { beginAtZero: true } } }
                });
            })
            .catch(error => console.error('Error fetching top cities by sales:', error));
    }

    // Tiempo
    function loadTimeCharts() {
        fetch('/api/sales_by_year_month')
            .then(response => response.json())
            .then(data => {
                drawChartJS(data, 'salesByYearMonthCanvas', 'line', {
                    data: {
                        labels: data.map(d => d.year_month),
                        datasets: [{
                            label: 'Ventas ($)', data: data.map(d => d.total_sales),
                            borderColor: getThemeColor('--sidebar-accent-color'),
                            backgroundColor: getThemeColor('--sidebar-accent-color') + '33', fill: true, tension: 0.1
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Ventas Mensuales a lo largo del Tiempo' } } }
                });
            })
            .catch(error => console.error('Error fetching sales by year month:', error));

        fetch('/api/sales_by_day_of_week')
            .then(response => response.json())
            .then(data => {
                drawChartJS(data, 'salesByDayOfWeekCanvas', 'bar', {
                    data: {
                        labels: data.map(d => d.day),
                        datasets: [{
                            label: 'Ventas ($)', data: data.map(d => d.total_sales),
                            backgroundColor: getThemeColor('--sidebar-accent-color')
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, title: { display: true, text: 'Ventas por Día de la Semana' } }, scales: { y: { beginAtZero: true } } }
                });
            })
            .catch(error => console.error('Error fetching sales by day of week:', error));
        
        fetch('/api/sales_heatmap')
            .then(response => response.json())
            .then(data => {
                drawChartD3(data, 'sales-heatmap', {
                    type: 'heatmap', title: 'Ventas Mensuales (Heatmap)',
                    margin: {top: 40, right: 30, bottom: 60, left: 60} // Keep this specific margin
                });
            })
            .catch(error => console.error('Error fetching sales heatmap:', error));
    }


    // --- Cargar gráficos al cargar la página, según la ruta actual ---
    if (window.location.pathname === '/dashboard') {
        loadDashboardCharts();
    } else if (window.location.pathname === '/clientes') {
        loadCustomersCharts();
    } else if (window.location.pathname === '/productos') {
        loadProductsCharts();
    } else if (window.location.pathname === '/regiones') {
        loadRegionsCharts();
    } else if (window.location.pathname === '/tiempo') {
        loadTimeCharts();
    }
});

// Helper para Fetch API: manejar errores de red y de servidor
window.fetch = (function(originalFetch) {
    return function(...args) {
        return originalFetch.apply(this, args).then(response => {
            if (!response.ok) {
                // Redirigir a login si es un 401 (No autorizado)
                if (response.status === 401) {
                    window.location.href = '/login';
                }
                // Opcional: manejar otros errores HTTP aquí
                return Promise.reject(new Error(`HTTP error! status: ${response.status}`));
            }
            return response;
        }).catch(error => {
            console.error('Fetch error:', error);
            return Promise.reject(error);
        });
    };
})(window.fetch);