// src/dashboard/static/script.js

// Update status every second
setInterval(updateStatus, 1000);
// Update risks every 500ms for real-time feedback
setInterval(updateRisks, 500);

let audioEnabled = true;

function updateStatus() {
    fetch('/api/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('object-count').textContent = data.detections;
            document.getElementById('risk-count').textContent = data.risks;
            
            // Update description if available and not empty
            if (data.description && data.description !== document.getElementById('scene-description').innerHTML) {
                document.getElementById('scene-description').innerHTML = 
                    `<span class="blue-text">✨</span> ${data.description}`;
            }
            
            // Update system status
            document.getElementById('system-status').textContent = data.detections > 0 ? '✓' : '●';
        })
        .catch(error => {
            console.error('Error fetching status:', error);
            document.getElementById('scene-description').innerHTML = 
                '⚠️ Connection error. Make sure the server is running.';
        });
}

function updateRisks() {
    fetch('/api/risks')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const riskList = document.getElementById('risk-list');
            riskList.innerHTML = '';
            
            if (data.risks.length === 0) {
                riskList.innerHTML = '<div class="risk-low">✨ No immediate risks detected. Path is clear.</div>';
            } else {
                data.risks.forEach(risk => {
                    let riskClass = 'risk-low';
                    let icon = 'ℹ️';
                    
                    switch(risk.risk_level) {
                        case 'CRITICAL':
                            riskClass = 'risk-critical';
                            icon = '🚨';
                            break;
                        case 'HIGH':
                            riskClass = 'risk-high';
                            icon = '⚠️';
                            break;
                        case 'MEDIUM':
                            riskClass = 'risk-medium';
                            icon = '⚡';
                            break;
                        default:
                            riskClass = 'risk-low';
                            icon = '✓';
                    }
                    
                    const riskElement = document.createElement('div');
                    riskElement.className = riskClass;
                    
                    let positionText = risk.position ? 
                        `at ${risk.position.horizontal} side` : 
                        'ahead';
                    
                    riskElement.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.5rem;">${icon}</span>
                            <div style="flex: 1;">
                                <strong>${risk.type === 'vehicle' ? '🚗 Vehicle' : '🚶 Person'}</strong><br>
                                ${risk.action}<br>
                                <small>${risk.distance}m ${positionText}</small>
                            </div>
                        </div>
                    `;
                    
                    riskList.appendChild(riskElement);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching risks:', error);
        });
}

function describeScene() {
    const button = event.target;
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '⏳ Describing...';
    button.disabled = true;
    
    fetch('/api/describe')
        .then(response => response.json())
        .then(data => {
            document.getElementById('scene-description').innerHTML = 
                `<span class="blue-text">🔮</span> ${data.description}`;
            
            // Visual feedback
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
                button.innerHTML = originalText;
                button.disabled = false;
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            button.innerHTML = originalText;
            button.disabled = false;
        });
}

function toggleAudio() {
    const btn = document.getElementById('audioBtn');
    audioEnabled = !audioEnabled;
    
    if (audioEnabled) {
        btn.innerHTML = '🔊 Audio On';
        btn.classList.remove('secondary');
        btn.classList.add('primary');
    } else {
        btn.innerHTML = '🔇 Audio Off';
        btn.classList.remove('primary');
        btn.classList.add('secondary');
    }
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Press 'D' to describe scene
    if (event.key === 'd' || event.key === 'D') {
        describeScene();
    }
    // Press 'M' to toggle audio
    if (event.key === 'm' || event.key === 'M') {
        toggleAudio();
    }
});

// Auto-refresh connection check
setInterval(() => {
    fetch('/api/status')
        .then(response => {
            if (response.ok) {
                document.querySelector('.status-indicator span:last-child').textContent = 'Connected';
                document.querySelector('.dot').style.backgroundColor = '#10b981';
            }
        })
        .catch(() => {
            document.querySelector('.status-indicator span:last-child').textContent = 'Reconnecting...';
            document.querySelector('.dot').style.backgroundColor = '#ff6b6b';
        });
}, 5000);