// Admin Panel JavaScript

let currentAnomalies = [];
let editingAnomalyId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupModal();
    loadAnomalies();
});

// Tabs Management
function setupTabs() {
    document.querySelectorAll('.admin-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.dataset.tab;
            
            // Update tab buttons
            document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update content
            document.querySelectorAll('.admin-content').forEach(c => c.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// Modal Management
function setupModal() {
    const modal = document.getElementById('anomaly-modal');
    const addBtn = document.getElementById('add-anomaly-btn');
    const closeBtn = document.getElementById('modal-close');
    const cancelBtn = document.getElementById('cancel-btn');
    const form = document.getElementById('anomaly-form');
    
    addBtn.addEventListener('click', () => openModal());
    closeBtn.addEventListener('click', () => closeModal());
    cancelBtn.addEventListener('click', () => closeModal());
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        saveAnomaly();
    });
}

function openModal(anomaly = null) {
    const modal = document.getElementById('anomaly-modal');
    const title = document.getElementById('modal-title');
    
    if (anomaly) {
        // Edit mode
        title.textContent = 'Modifier Anomalie';
        editingAnomalyId = anomaly.anomaly_id;
        
        document.getElementById('anomaly-id').value = anomaly.anomaly_id;
        document.getElementById('line-id').value = anomaly.line_id;
        document.getElementById('machine-id').value = anomaly.machine_id;
        document.getElementById('symptom').value = anomaly.symptom;
        document.getElementById('root-cause').value = anomaly.root_cause;
        document.getElementById('solution-applied').value = anomaly.solution_applied;
        document.getElementById('resolution-time').value = anomaly.resolution_time_minutes;
        document.getElementById('impact-oee').value = anomaly.impact_oee;
        document.getElementById('priority').value = anomaly.priority;
    } else {
        // Add mode
        title.textContent = 'Ajouter Anomalie';
        editingAnomalyId = null;
        document.getElementById('anomaly-form').reset();
    }
    
    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('anomaly-modal').classList.remove('active');
    editingAnomalyId = null;
}

// Anomalies CRUD
async function loadAnomalies() {
    try {
        const response = await fetch('/api/admin/anomalies');
        const data = await response.json();
        
        if (data.success) {
            currentAnomalies = data.anomalies;
            displayAnomalies(currentAnomalies);
        }
    } catch (error) {
        console.error('Error loading anomalies:', error);
    }
}

function displayAnomalies(anomalies) {
    const tbody = document.getElementById('anomalies-tbody');
    
    if (anomalies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;">Aucune anomalie</td></tr>';
        return;
    }
    
    tbody.innerHTML = anomalies.map(anomaly => `
        <tr>
            <td>${anomaly.anomaly_id}</td>
            <td>${new Date(anomaly.timestamp).toLocaleDateString('fr-FR')}</td>
            <td>${anomaly.line_id}</td>
            <td>${anomaly.machine_id}</td>
            <td>${truncate(anomaly.symptom, 50)}</td>
            <td>${truncate(anomaly.root_cause, 50)}</td>
            <td>${truncate(anomaly.solution_applied, 50)}</td>
            <td>${anomaly.impact_oee}%</td>
            <td>
                <span class="priority-badge priority-${anomaly.priority.toLowerCase()}">
                    ${anomaly.priority}
                </span>
            </td>
            <td class="action-buttons">
                <button class="btn-edit" onclick="editAnomaly(${anomaly.anomaly_id})">
                    Modifier
                </button>
                <button class="btn-delete" onclick="deleteAnomaly(${anomaly.anomaly_id})">
                    Supprimer
                </button>
            </td>
        </tr>
    `).join('');
}

function truncate(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

async function saveAnomaly() {
    const anomalyData = {
        line_id: document.getElementById('line-id').value,
        machine_id: document.getElementById('machine-id').value,
        symptom: document.getElementById('symptom').value,
        root_cause: document.getElementById('root-cause').value,
        solution_applied: document.getElementById('solution-applied').value,
        resolution_time_minutes: parseInt(document.getElementById('resolution-time').value),
        impact_oee: parseInt(document.getElementById('impact-oee').value),
        priority: document.getElementById('priority').value
    };
    
    try {
        let response;
        
        if (editingAnomalyId) {
            // Update
            response = await fetch(`/api/admin/anomalies/${editingAnomalyId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(anomalyData)
            });
        } else {
            // Create
            response = await fetch('/api/admin/anomalies', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(anomalyData)
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            closeModal();
            loadAnomalies();
            alert(editingAnomalyId ? 'Anomalie modifiée avec succès!' : 'Anomalie ajoutée avec succès!');
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Error saving anomaly:', error);
        alert('Erreur lors de la sauvegarde');
    }
}

function editAnomaly(anomalyId) {
    const anomaly = currentAnomalies.find(a => a.anomaly_id === anomalyId);
    if (anomaly) {
        openModal(anomaly);
    }
}

async function deleteAnomaly(anomalyId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette anomalie?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/anomalies/${anomalyId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadAnomalies();
            alert('Anomalie supprimée avec succès!');
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Error deleting anomaly:', error);
        alert('Erreur lors de la suppression');
    }
}