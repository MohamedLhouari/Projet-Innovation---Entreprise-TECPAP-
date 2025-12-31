// Agent IA de Décision pour l'Amélioration de l'OEE - Interface JavaScript

// Global state
let currentLine = 'L1';
let dashboardData = null;
let charts = {};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    loadDashboardData();
    setupEventListeners();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Tab Management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');
    
    // Load tab-specific data
    switch(tabId) {
        case 'predictions':
            loadPredictions();
            break;
        case 'speed-optimization':
            // Speed optimization tab - no auto-load, user triggers
            break;
        case 'anomalies':
            loadAnomalies();
            break;
        case 'analytics':
            loadAnalytics();
            break;
    }
}

// Event Listeners
function setupEventListeners() {
    // Line selector for predictions
    document.querySelectorAll('.selector-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentLine = btn.dataset.line;
            document.querySelectorAll('.selector-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadPredictions();
        });
    });
    
    // Simulate button
    const simulateBtn = document.getElementById('simulate-btn');
    if (simulateBtn) {
        simulateBtn.addEventListener('click', simulateScenarios);
    }
    
    // Search anomalies
    const searchBtn = document.getElementById('search-anomaly-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', searchSimilarAnomalies);
    }
    
    // Calculate impact
    const calcBtn = document.getElementById('calculate-impact-btn');
    if (calcBtn) {
        calcBtn.addEventListener('click', calculateImpact);
    }
    
    // Speed optimization
    const optimizeSpeedBtn = document.getElementById('optimize-speed-btn');
    if (optimizeSpeedBtn) {
        optimizeSpeedBtn.addEventListener('click', optimizeSpeed);
    }
    
    // Compare all lines
    const compareAllBtn = document.getElementById('compare-all-lines-btn');
    if (compareAllBtn) {
        compareAllBtn.addEventListener('click', compareAllLines);
    }
}

// Dashboard Data Loading
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        
        if (data.success) {
            dashboardData = data;
            updateDashboard(data);
            updateLastUpdateTime();
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboard(data) {
    // Update KPIs
    updateKPIs(data.current);
    
    // Update recommendation
    if (data.recommendation) {
        updateRecommendation(data.recommendation);
    }
    
    // Update alerts
    if (data.alerts) {
        updateAlerts(data.alerts);
    }
    
    // Update chart
    updateOEEChart(data.current);
}

function updateKPIs(current) {
    ['L1', 'L2', 'L3'].forEach(line => {
        if (current[line]) {
            const lineData = current[line];
            document.getElementById(`${line.toLowerCase()}-oee`).textContent = lineData.oee + '%';
            document.getElementById(`${line.toLowerCase()}-availability`).textContent = lineData.availability + '%';
            document.getElementById(`${line.toLowerCase()}-performance`).textContent = lineData.performance + '%';
            document.getElementById(`${line.toLowerCase()}-quality`).textContent = lineData.quality + '%';
        }
    });
}

function updateRecommendation(rec) {
    document.getElementById('recommended-line').textContent = rec.recommended_line;
    document.getElementById('recommendation-score').textContent = rec.score.toFixed(1);
    document.getElementById('recommendation-reason').textContent = rec.reason;
}

function updateAlerts(alerts) {
    const alertsGrid = document.getElementById('alerts-grid');
    
    if (alerts.length === 0) {
        alertsGrid.innerHTML = '<div class="alert-placeholder">Aucune alerte active</div>';
        return;
    }
    
    alertsGrid.innerHTML = alerts.map(alert => `
        <div class="alert-card ${alert.severity.toLowerCase()}">
            <div class="alert-icon">${getSeverityIcon(alert.severity)}</div>
            <div class="alert-content">
                <div class="alert-message">${alert.message}</div>
                <div class="alert-details">
                    ${alert.line_id} - ${alert.type} 
                    ${alert.current_value ? `(Valeur: ${alert.current_value}%)` : ''}
                </div>
                <div class="alert-action">Action: ${alert.recommended_action}</div>
            </div>
        </div>
    `).join('');
}

function getSeverityIcon(severity) {
    const icons = {
        'Critical': '⚠',
        'High': '⬆',
        'Medium': 'ℹ',
        'Low': '○'
    };
    return icons[severity] || 'ℹ';
}

// Chart Updates
function updateOEEChart(current) {
    const ctx = document.getElementById('oeeChart');
    if (!ctx) return;
    
    const lines = ['L1', 'L2', 'L3'];
    const oeeData = lines.map(line => current[line] ? current[line].oee : 0);
    const availData = lines.map(line => current[line] ? current[line].availability : 0);
    const perfData = lines.map(line => current[line] ? current[line].performance : 0);
    const qualData = lines.map(line => current[line] ? current[line].quality : 0);
    
    if (charts.oeeChart) {
        charts.oeeChart.destroy();
    }
    
    charts.oeeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: lines,
            datasets: [
                {
                    label: 'OEE',
                    data: oeeData,
                    backgroundColor: 'rgba(26, 115, 232, 0.8)',
                    borderColor: 'rgba(26, 115, 232, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Disponibilité',
                    data: availData,
                    backgroundColor: 'rgba(52, 168, 83, 0.6)',
                    borderColor: 'rgba(52, 168, 83, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Performance',
                    data: perfData,
                    backgroundColor: 'rgba(251, 188, 4, 0.6)',
                    borderColor: 'rgba(251, 188, 4, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Qualité',
                    data: qualData,
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
                        }
                    }
                }
            }
        }
    });
}

// Predictions
async function loadPredictions() {
    try {
        const response = await fetch(`/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                line_id: currentLine,
                horizon: 7
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updatePredictionsTable(data.prediction.predictions);
            updatePredictionsChart(data.prediction.predictions);
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

function updatePredictionsTable(predictions) {
    const tbody = document.getElementById('predictions-tbody');
    
    tbody.innerHTML = predictions.map(pred => `
        <tr>
            <td>${pred.date}</td>
            <td><strong>${pred.oee_predicted}%</strong></td>
            <td><span class="kpi-badge status-${pred.confidence.toLowerCase()}">${pred.confidence}</span></td>
            <td>${pred.trend}</td>
        </tr>
    `).join('');
}

function updatePredictionsChart(predictions) {
    const ctx = document.getElementById('predictionsChart');
    if (!ctx) return;
    
    if (charts.predictionsChart) {
        charts.predictionsChart.destroy();
    }
    
    charts.predictionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: predictions.map(p => p.date),
            datasets: [{
                label: `OEE Prédit ${currentLine}`,
                data: predictions.map(p => p.oee_predicted),
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 60,
                    max: 90,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

// Scenarios Simulation
async function simulateScenarios() {
    const productType = document.getElementById('product-type').value;
    const quantity = parseInt(document.getElementById('quantity-input').value);
    
    if (!productType) {
        alert('Veuillez sélectionner un type de produit');
        return;
    }
    
    try {
        const response = await fetch(`/api/recommend?product_type=${productType}&quantity=${quantity}`);
        const data = await response.json();
        
        if (data.success) {
            displayScenarios(data);
            displayComparison(data.comparison);
        } else {
            console.error('Erreur:', data.error);
            alert('Erreur lors de la simulation: ' + (data.error || 'Erreur inconnue'));
        }
    } catch (error) {
        console.error('Error simulating scenarios:', error);
        alert('Erreur de connexion au serveur');
    }
}

function displayScenarios(data) {
    const grid = document.getElementById('scenarios-grid');
    const scenarios = data.scenarios;
    
    grid.innerHTML = scenarios.map((scenario, index) => `
        <div class="scenario-card ${index === 0 ? 'best' : ''}">
            <h3>${scenario.line_id} ${index === 0 ? '(Recommandé)' : ''}</h3>
            <div class="kpi-details">
                <div class="detail-item">
                    <span class="detail-label">OEE Prédit:</span>
                    <span class="detail-value">${scenario.oee_predicted}%</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Temps Production:</span>
                    <span class="detail-value">${scenario.production_time.toFixed(2)}h</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Qualité Attendue:</span>
                    <span class="detail-value">${scenario.quality_expected}%</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Niveau Risque:</span>
                    <span class="kpi-badge status-${scenario.risk_level.toLowerCase()}">${scenario.risk_level}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function displayComparison(comparison) {
    const section = document.getElementById('comparison-section');
    const grid = document.getElementById('comparison-grid');
    
    section.style.display = 'block';
    
    grid.innerHTML = `
        <div class="kpi-card">
            <h4>Plus Rapide</h4>
            <div class="kpi-value" style="font-size: 36px;">${comparison.fastest}</div>
            <p>Gain: ${comparison.time_difference.toFixed(2)}h</p>
        </div>
        <div class="kpi-card">
            <h4>Plus Fiable</h4>
            <div class="kpi-value" style="font-size: 36px;">${comparison.most_reliable}</div>
            <p>Meilleur OEE prédit</p>
        </div>
        <div class="kpi-card">
            <h4>Meilleure Qualité</h4>
            <div class="kpi-value" style="font-size: 36px;">${comparison.best_quality}</div>
            <p>Meilleur taux qualité</p>
        </div>
    `;
}

// Anomalies
async function loadAnomalies() {
    try {
        const response = await fetch('/api/anomalies?period=30');
        const data = await response.json();
        
        if (data.success) {
            displayAnomaliesTable(data.anomalies);
        }
    } catch (error) {
        console.error('Error loading anomalies:', error);
    }
}

function displayAnomaliesTable(anomalies) {
    const tbody = document.getElementById('anomalies-tbody');
    
    if (anomalies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8">Aucune anomalie récente</td></tr>';
        return;
    }
    
    tbody.innerHTML = anomalies.slice(0, 20).map(anomaly => `
        <tr>
            <td>${new Date(anomaly.date).toLocaleDateString('fr-FR')}</td>
            <td><strong>${anomaly.line}</strong></td>
            <td>${anomaly.machine}</td>
            <td>${anomaly.symptom}</td>
            <td>${anomaly.cause}</td>
            <td>${anomaly.solution}</td>
            <td><span style="color: var(--danger-color);">${anomaly.impact}%</span></td>
            <td>${anomaly.resolution_time}min</td>
        </tr>
    `).join('');
}

async function searchSimilarAnomalies() {
    const description = document.getElementById('anomaly-search-input').value;
    
    if (!description) {
        alert('Veuillez décrire l\'anomalie');
        return;
    }
    
    try {
        const response = await fetch('/api/anomaly/similar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: description,
                machine_id: ''
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySimilarCases(data.similar_cases);
        }
    } catch (error) {
        console.error('Error searching anomalies:', error);
    }
}

function displaySimilarCases(cases) {
    const resultsDiv = document.getElementById('search-results');
    const casesDiv = document.getElementById('similar-cases');
    
    resultsDiv.style.display = 'block';
    
    if (cases.length === 0) {
        casesDiv.innerHTML = '<p>Aucun cas similaire trouvé dans l\'historique</p>';
        return;
    }
    
    casesDiv.innerHTML = cases.map(c => `
        <div class="similar-case">
            <div class="similarity-badge">Similarité: ${c.similarity}%</div>
            <h4>${c.symptom}</h4>
            <div class="case-details">
                <div class="detail-row">
                    <strong>Ligne/Machine:</strong>
                    <span>${c.line} - ${c.machine}</span>
                </div>
                <div class="detail-row">
                    <strong>Cause Identifiée:</strong>
                    <span>${c.root_cause}</span>
                </div>
                <div class="detail-row">
                    <strong>Solution Appliquée:</strong>
                    <span>${c.solution}</span>
                </div>
                <div class="detail-row">
                    <strong>Temps Résolution:</strong>
                    <span>${c.resolution_time} minutes</span>
                </div>
                <div class="detail-row">
                    <strong>Impact OEE:</strong>
                    <span style="color: var(--danger-color);">${c.impact}%</span>
                </div>
                <div class="detail-row">
                    <strong>Efficacité:</strong>
                    <span class="kpi-badge status-${c.effectiveness.toLowerCase()}">${c.effectiveness}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Analytics
async function loadAnalytics() {
    // Load historical data for chart
    try {
        const response = await fetch('/api/historical?days=90');
        const data = await response.json();
        
        if (data.success) {
            updateHistoricalChart(data.data);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function updateHistoricalChart(data) {
    const ctx = document.getElementById('historicalChart');
    if (!ctx) return;
    
    // Group by date and line
    const groupedData = {};
    data.forEach(record => {
        const date = new Date(record.timestamp).toLocaleDateString('fr-FR');
        if (!groupedData[date]) {
            groupedData[date] = { L1: [], L2: [], L3: [] };
        }
        if (groupedData[date][record.line_id]) {
            groupedData[date][record.line_id].push(record.oee);
        }
    });
    
    const dates = Object.keys(groupedData).slice(-30); // Last 30 days
    
    const datasets = ['L1', 'L2', 'L3'].map((line, idx) => {
        const colors = [
            'rgba(26, 115, 232, 1)',
            'rgba(52, 168, 83, 1)',
            'rgba(251, 188, 4, 1)'
        ];
        
        return {
            label: line,
            data: dates.map(date => {
                const values = groupedData[date][line];
                return values.length > 0 ? values.reduce((a, b) => a + b) / values.length : null;
            }),
            borderColor: colors[idx],
            backgroundColor: colors[idx].replace('1)', '0.1)'),
            tension: 0.3,
            borderWidth: 2
        };
    });
    
    if (charts.historicalChart) {
        charts.historicalChart.destroy();
    }
    
    charts.historicalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 60,
                    max: 85,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

async function calculateImpact() {
    const currentOEE = parseFloat(document.getElementById('current-oee-input').value);
    const improvement = parseFloat(document.getElementById('improvement-input').value);
    
    try {
        const response = await fetch(`/api/impact?improvement=${improvement}`);
        const data = await response.json();
        
        if (data.success) {
            displayImpactResults(data.impact);
        }
    } catch (error) {
        console.error('Error calculating impact:', error);
    }
}

function displayImpactResults(impact) {
    const resultsDiv = document.getElementById('impact-results');
    resultsDiv.style.display = 'block';
    
    document.getElementById('target-oee').textContent = impact.target_oee.toFixed(2);
    document.getElementById('gain-hours').textContent = impact.estimated_gain.gain_hours.toFixed(0);
    document.getElementById('gain-percent').textContent = impact.estimated_gain.gain_percent.toFixed(2);
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR');
    document.getElementById('last-update').textContent = timeString;
}

// ============================================
// SPEED OPTIMIZATION FUNCTIONS
// ============================================

async function optimizeSpeed() {
    const lineId = document.getElementById('speed-line-select').value;
    const productType = document.getElementById('speed-product-select').value;
    const btn = document.getElementById('optimize-speed-btn');
    
    // Show loading state
    btn.disabled = true;
    btn.textContent = '⏳ Calcul en cours...';
    
    try {
        const response = await fetch('/api/speed/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                line_id: lineId,
                product_type: productType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayOptimizationResults(data.optimization);
            createSweetSpotChart(data.optimization);
        } else {
            alert('Erreur lors de l\'optimisation: ' + data.error);
        }
    } catch (error) {
        console.error('Error optimizing speed:', error);
        alert('Erreur de connexion au serveur');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Trouver le Sweet Spot';
    }
}

function displayOptimizationResults(result) {
    // Show results section
    document.getElementById('optimization-results').style.display = 'block';
    
    // Build recommendation card
    const recommendationDiv = document.getElementById('speed-recommendation');
    
    const improvementClass = result.improvement_pct > 0 ? 'positive' : 
                            result.improvement_pct < -2 ? 'negative' : 'neutral';
    
    const actionIcon = result.action === 'increase' ? '↑' : 
                      result.action === 'decrease' ? '↓' : '→';
    
    recommendationDiv.innerHTML = `
        <div class="recommendation-main">
            <div class="recommendation-icon ${result.action}">
                ${actionIcon}
            </div>
            <div class="recommendation-details">
                <h4>${result.recommendation}</h4>
                <p class="recommendation-subtitle">
                    Confiance: <span class="badge badge-${result.confidence.toLowerCase()}">${result.confidence}</span>
                </p>
            </div>
        </div>
        
        <div class="recommendation-stats">
            <div class="stat-item">
                <span class="stat-label">Vitesse Optimale</span>
                <span class="stat-value highlight">${result.optimal_speed} pcs/h</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Production Nette Max</span>
                <span class="stat-value">${result.max_net_output.toFixed(1)} pcs/h</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Amélioration Potentielle</span>
                <span class="stat-value ${improvementClass}">
                    ${result.improvement_pct > 0 ? '+' : ''}${result.improvement_pct.toFixed(2)}%
                </span>
            </div>
        </div>
    `;
    
    // Build metrics grid
    const metricsDiv = document.getElementById('speed-metrics');
    metricsDiv.innerHTML = `
        <div class="metric-card">
            <h4>Vitesse Actuelle</h4>
            <div class="metric-value">${result.current_speed} pcs/h</div>
            <div class="metric-detail">Production nette: ${result.current_net_output.toFixed(1)} pcs/h</div>
        </div>
        
        <div class="metric-card highlight">
            <h4>Sweet Spot Optimal</h4>
            <div class="metric-value">${result.optimal_speed} pcs/h</div>
            <div class="metric-detail">Production nette: ${result.max_net_output.toFixed(1)} pcs/h</div>
        </div>
        
        <div class="metric-card">
            <h4>Gain Attendu</h4>
            <div class="metric-value ${improvementClass}">
                ${result.improvement_pct > 0 ? '+' : ''}${result.improvement_pct.toFixed(2)}%
            </div>
            <div class="metric-detail">
                ${Math.abs(result.max_net_output - result.current_net_output).toFixed(1)} pcs/h supplémentaires
            </div>
        </div>
    `;
    
    // Scroll to results
    document.getElementById('optimization-results').scrollIntoView({ behavior: 'smooth' });
}

function createSweetSpotChart(result) {
    const ctx = document.getElementById('sweetSpotChart');
    
    // Destroy existing chart if any
    if (charts.sweetSpotChart) {
        charts.sweetSpotChart.destroy();
    }
    
    const curveData = result.curve_data;
    const speeds = curveData.map(d => d.speed);
    const production = curveData.map(d => d.production_rate);
    const quality = curveData.map(d => d.quality_rate);
    const netOutput = curveData.map(d => d.net_output);
    const defects = curveData.map(d => d.defect_rate);
    
    // Find optimal point index
    const optimalIndex = speeds.indexOf(result.optimal_speed);
    
    charts.sweetSpotChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: speeds,
            datasets: [
                {
                    label: 'Production Nette (pcs/h)',
                    data: netOutput,
                    borderColor: 'rgba(46, 204, 113, 1)',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    yAxisID: 'y',
                    pointRadius: speeds.map((_, i) => i === optimalIndex ? 8 : 3),
                    pointBackgroundColor: speeds.map((_, i) => 
                        i === optimalIndex ? 'rgba(255, 215, 0, 1)' : 'rgba(46, 204, 113, 1)'
                    ),
                    pointBorderWidth: speeds.map((_, i) => i === optimalIndex ? 3 : 1)
                },
                {
                    label: 'Production Totale (pcs/h)',
                    data: production,
                    borderColor: 'rgba(52, 152, 219, 1)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y',
                    borderDash: [5, 5]
                },
                {
                    label: 'Taux de Défauts (%)',
                    data: defects,
                    borderColor: 'rgba(231, 76, 60, 1)',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 12,
                            family: "'Segoe UI', Arial, sans-serif"
                        }
                    }
                },
                title: {
                    display: true,
                    text: `Courbe d'Optimisation - ${result.line_id} - ${formatProductName(result.product_type)}`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `Vitesse: ${context[0].label} pcs/h`;
                        },
                        afterLabel: function(context) {
                            if (context.dataIndex === optimalIndex) {
                                return '⭐ SWEET SPOT OPTIMAL';
                            }
                            return '';
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Vitesse Machine (pièces/heure)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Production (pcs/h)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Taux de Défauts (%)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

async function compareAllLines() {
    const productType = document.getElementById('speed-product-select').value;
    const btn = document.getElementById('compare-all-lines-btn');
    
    btn.disabled = true;
    btn.textContent = '⏳ Comparaison en cours...';
    
    try {
        const response = await fetch(`/api/speed/compare?product_type=${productType}`);
        const data = await response.json();
        
        if (data.success) {
            displayLinesComparison(data.comparison);
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Error comparing lines:', error);
        alert('Erreur de connexion');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄 Comparer L1 vs L2 vs L3';
    }
}

function displayLinesComparison(comparison) {
    const comparisonDiv = document.getElementById('lines-comparison');
    comparisonDiv.style.display = 'grid';
    
    const recommendations = comparison.recommendations;
    const bestLine = comparison.best_line;
    
    let html = '';
    
    ['L1', 'L2', 'L3'].forEach(lineId => {
        const result = recommendations[lineId];
        const isBest = lineId === bestLine;
        
        html += `
            <div class="comparison-card ${isBest ? 'best-option' : ''}">
                ${isBest ? '<div class="best-badge">MEILLEUR CHOIX</div>' : ''}
                <h4>${lineId}</h4>
                <div class="comparison-stats">
                    <div class="stat-row">
                        <span>Vitesse Optimale:</span>
                        <strong>${result.optimal_speed} pcs/h</strong>
                    </div>
                    <div class="stat-row">
                        <span>Production Nette Max:</span>
                        <strong>${result.max_net_output.toFixed(1)} pcs/h</strong>
                    </div>
                    <div class="stat-row">
                        <span>Amélioration:</span>
                        <strong class="${result.improvement_pct > 0 ? 'positive' : 'neutral'}">
                            ${result.improvement_pct > 0 ? '+' : ''}${result.improvement_pct.toFixed(2)}%
                        </strong>
                    </div>
                    <div class="stat-row">
                        <span>Action:</span>
                        <strong>${result.recommendation}</strong>
                    </div>
                </div>
            </div>
        `;
    });
    
    comparisonDiv.innerHTML = html;
    comparisonDiv.scrollIntoView({ behavior: 'smooth' });
}

function formatProductName(productType) {
    const names = {
        'Fond_Plat': 'Fond Plat',
        'Fond_Carre_Sans_Poignees': 'Fond Carré Sans Poignées',
        'Fond_Carre_Poignees_Plates': 'Fond Carré Poignées Plates',
        'Fond_Carre_Poignees_Torsadees': 'Fond Carré Poignées Torsadées'
    };
    return names[productType] || productType;
}
