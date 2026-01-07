// IronGhost - Behavioral Biometrics (Client Side)

let keyTimes = [];
let backspaceCount = 0;

document.addEventListener('keydown', (e) => {
    keyTimes.push({ type: 'down', time: Date.now() });
    if (e.key === 'Backspace') backspaceCount++;
});

document.addEventListener('keyup', (e) => {
    keyTimes.push({ type: 'up', time: Date.now() });
});

function calculateFlightMetrics() {
    if (keyTimes.length < 2) return null;
    
    // Calculate intervals between keydowns
    let intervals = [];
    let downs = keyTimes.filter(k => k.type === 'down');
    
    for (let i = 1; i < downs.length; i++) {
        intervals.push(downs[i].time - downs[i-1].time);
    }
    
    if (intervals.length === 0) return { variance: 0, backspace: backspaceCount };

    // Calculate variance
    let mean = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    let variance = intervals.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / intervals.length;
    
    return {
        variance: variance,
        flight_data: intervals,
        backspace_count: backspaceCount
    };
}

// Inject into forms
document.addEventListener('submit', (e) => {
    const metrics = calculateFlightMetrics();
    if (metrics) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'x-bio-auth';
        input.value = JSON.stringify(metrics);
        e.target.appendChild(input);
    }
});
