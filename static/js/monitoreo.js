let inventoryData = {};
let ventasData = {};
let currentInvView = 'sucursales';
let currentInvSucursal = null;
let currentInvProducto = null;
let chartInv = null;
let chartVentas = null;
let currentVentasView = 'sucursales';

/*
HISTORIAL DE INVENTARIOS
*/

// Cargar datos del inventario
async function loadInventoryData() {
    try {
        const response = await fetch('/analista/api/inventario');
        inventoryData = await response.json();
        displayInvSucursales();
    } catch (error) {
        console.error('Error cargando datos:', error);
        document.getElementById('invSucursalesContainer').innerHTML = 
            '<div class="alert alert-danger">Error cargando los datos</div>';
    }
}

// Mostrar sucursales
function displayInvSucursales() {
    const container = document.getElementById('invSucursalesContainer');
    let html = '';

    for (const sucursalId in inventoryData) {
        const sucursalData = inventoryData[sucursalId];
        const firstProduct = Object.values(sucursalData)[0];
        const sucursalName = firstProduct[0].sucursal;
        
        // Determinar el estado general de la sucursal
        let hasLowStock = false;
        for (const productoId in sucursalData) {
            const latestRecord = sucursalData[productoId][0];
            if (latestRecord.estado_stock === 'Bajo') {
                hasLowStock = true;
                break;
            }
        }
        
        const cardClass = hasLowStock ? 'card-stock-bajo' : 'card-stock-ok';
        const badgeClass = hasLowStock ? 'bg-danger' : 'bg-success';
        const statusText = hasLowStock ? 'Stock Bajo' : 'Stock OK';
        
        html += `
            <div class="col-md-4 mb-3">
                <div class="card ${cardClass}" onclick="showProductos(${sucursalId}, '${sucursalName}')">
                    <div class="card-body">
                        <h5 class="card-title">${sucursalName}</h5>
                        <p class="card-text">Productos: ${Object.keys(sucursalData).length}</p>
                        <span class="badge ${badgeClass}">${statusText}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Mostrar productos de una sucursal
function showProductos(sucursalId, sucursalName) {
    currentInvView = 'productos';
    currentInvSucursal = sucursalId;
    
    document.getElementById('invSucursalesView').classList.add('d-none');
    document.getElementById('invProductosView').classList.remove('d-none');
    document.getElementById('invBackButton').classList.remove('d-none');
    document.getElementById('invSucursalTitle').textContent = `Productos - ${sucursalName}`;
    
    const container = document.getElementById('invProductosContainer');
    const sucursalData = inventoryData[sucursalId];
    let html = '';
    
    for (const productoId in sucursalData) {
        const productData = sucursalData[productoId];
        const latestRecord = productData[0];
        const cardClass = latestRecord.estado_stock === 'Bajo' ? 'card-stock-bajo' : 'card-stock-ok';
        const badgeClass = latestRecord.estado_stock === 'Bajo' ? 'bg-danger' : 'bg-success';
        
        html += `
            <div class="col-md-4 mb-3">
                <div class="card ${cardClass}" onclick="showGrafico(${sucursalId}, ${productoId}, '${latestRecord.producto}')">
                    <div class="card-body">
                        <h5 class="card-title">${latestRecord.producto}</h5>
                        <p class="card-text">
                            Stock Actual: ${latestRecord.stock_actual}<br>
                            Stock Mínimo: ${latestRecord.stock_minimo}
                        </p>
                        <span class="badge ${badgeClass}">${latestRecord.estado_stock}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Mostrar gráfico de un producto
function showGrafico(sucursalId, productoId, productoName) {
    currentInvView = 'grafico';
    currentInvProducto = productoId;
    
    document.getElementById('invProductosView').classList.add('d-none');
    document.getElementById('invGraficoView').classList.remove('d-none');
    document.getElementById('invProductoTitle').textContent = `Evolución del Stock - ${productoName}`;
    
    const productData = inventoryData[sucursalId][productoId];
    
    // Preparar datos para el gráfico
    const labels = productData.map(record => record.fecha).reverse();
    const stockActual = productData.map(record => record.stock_actual).reverse();
    const stockMinimo = productData.map(record => record.stock_minimo).reverse();
    
    // Destruir gráfico anterior si existe
    if (chartInv) {
        chartInv.destroy();
    }
    
    // Crear nuevo gráfico
    const ctx = document.getElementById('inventoryChart').getContext('2d');
    chartInv = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Stock Actual',
                    data: stockActual,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Stock Mínimo',
                    data: stockMinimo,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderDash: [5, 5],
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cantidad'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Fecha'
                    }
                }
            }
        }
    });
}

// Función para regresar
function goInvBack() {
    if (currentInvView === 'grafico') {
        document.getElementById('invGraficoView').classList.add('d-none');
        document.getElementById('invProductosView').classList.remove('d-none');
        currentInvView = 'productos';
        if (chartInv) {
            chartInv.destroy();
            chartInv = null;
        }
    } else if (currentInvView === 'productos') {
        document.getElementById('invProductosView').classList.add('d-none');
        document.getElementById('invSucursalesView').classList.remove('d-none');
        document.getElementById('invBackButton').classList.add('d-none');
        currentInvView = 'sucursales';
        currentInvSucursal = null;
    }
}

/*
HISTORIAL DE VENTAS
*/

// Cargar datos de ventas
async function loadVentasData() {
    try {
        const response = await fetch('/analista/api/ventas');
        ventasData = await response.json();
        displayVentasSucursales();
    } catch (error) {
        console.error('Error cargando datos de ventas:', error);
        document.getElementById('ventasSucursalesContainer').innerHTML = 
            '<div class="alert alert-danger">Error cargando los datos</div>';
    }
}

function displayVentasSucursales() {
    const container = document.getElementById('ventasSucursalesContainer');
    let html = '';

    for (const sucursalId in ventasData) {
        const data = Object.values(ventasData[sucursalId]);
        const primerRegistro = data[0]; // accede a 'sucursal'
        const sucursalName = primerRegistro.sucursal;

        html += `
            <div class="col-md-4 mb-3">
                <div class="card card-stock-info" onclick="showVentasGrafico(${sucursalId}, '${sucursalName}')">
                    <div class="card-body">
                        <h5 class="card-title">${sucursalName}</h5>
                        <p class="card-text">Ver ventas históricas</p>
                    </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

function showVentasGrafico(sucursalId, sucursalName) {
    const ventasView = document.getElementById('ventasView');
    const ventasGraficoView = document.getElementById('ventasGraficoView');
    const ventasSucursalTitle = document.getElementById('ventasSucursalTitle');
    const ventasChartCanvas = document.getElementById('ventasChart');

    if (!ventasView || !ventasGraficoView || !ventasSucursalTitle || !ventasChartCanvas) {
        console.error('Uno o más elementos no existen en el DOM');
        return;
    }

    ventasView.classList.add('d-none');
    ventasGraficoView.classList.remove('d-none');
    ventasSucursalTitle.textContent = `Ventas Diarias - ${sucursalName}`;

    const ventasSucursal = ventasData[sucursalId];
    if (!ventasSucursal) {
        console.error(`No se encontraron datos de ventas para la sucursal ${sucursalId}`);
        return;
    }

    const fechas = [];
    const cantidades = [];

    for (const registro of ventasSucursal) {
        const fechaTexto = registro.fecha;
        const cantidad = registro.cantidad_vendida;
        fechas.push(fechaTexto);
        cantidades.push(cantidad);
    }

    // Combinar y ordenar por fecha
    const combinado = fechas.map((f, i) => ({ fecha: f, cantidad: cantidades[i] }));
    combinado.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

    const labels = combinado.map(d => d.fecha);
    const data = combinado.map(d => d.cantidad);

    const ctx = ventasChartCanvas.getContext('2d');

    if (chartVentas) chartVentas.destroy();

    chartVentas = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cantidad Vendida',
                data: data,
                borderColor: '#f1c40f',
                backgroundColor: 'rgba(241, 196, 15, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cantidad Vendida'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Fecha'
                    }
                }
            }
        }
    });
}

// Función para regresar
function goVentasBack() {
    document.getElementById('ventasGraficoView').classList.add('d-none');
    document.getElementById('ventasView').classList.remove('d-none');
    if (chartVentas) {
        chartVentas.destroy();
        chartVentas = null;
    }
}


// Cargar datos al iniciar
window.onload = function() {
    loadInventoryData();
    loadVentasData();
};

// Toggle minimizar/maximizar sección de stock
document.querySelectorAll('.toggleSeccion').forEach(boton => {
    boton.addEventListener('click', function () {
        const targetId = this.getAttribute('data-target');
        const seccion = document.getElementById(targetId);

        if (seccion.style.display === 'none') {
            seccion.style.display = 'block';
            this.textContent = '−';
        } else {
            seccion.style.display = 'none';
            this.textContent = '+';
        }
    });
});