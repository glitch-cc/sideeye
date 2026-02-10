#!/usr/bin/env python3
"""
BEC Detection Web Interface
Flask app for the BEC Scorer POC
"""

from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
from bec_scorer import BECScorer, EmailToAnalyze

app = Flask(__name__)

# Initialize scorer with demo domain
scorer = BECScorer("cyrenity.com")

# Add some demo executives
scorer.add_executive("bbrown@cyrenity.com")
scorer.add_executive("cfo@cyrenity.com")

# Add some demo training data
from demo_training import load_demo_training
load_demo_training(scorer)

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BEC Detection Engine</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { 
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #f97316, #ef4444, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { color: #8b949e; margin-bottom: 30px; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
        
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
        }
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #f0f6fc;
        }
        
        label {
            display: block;
            color: #8b949e;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px 12px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #c9d1d9;
            font-size: 14px;
            margin-bottom: 15px;
        }
        input:focus, textarea:focus { border-color: #58a6ff; outline: none; }
        textarea { min-height: 120px; resize: vertical; }
        
        button {
            width: 100%;
            padding: 12px 24px;
            background: linear-gradient(90deg, #f97316, #ef4444);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            font-size: 1em;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #0d1117;
            border-radius: 8px;
            display: none;
        }
        .result.show { display: block; }
        
        .risk-score {
            font-size: 3em;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
        }
        .risk-level {
            text-align: center;
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 20px;
            padding: 8px;
            border-radius: 6px;
        }
        .risk-CRITICAL { background: #7f1d1d; color: #fca5a5; }
        .risk-HIGH { background: #7c2d12; color: #fdba74; }
        .risk-MEDIUM { background: #713f12; color: #fde047; }
        .risk-LOW { background: #14532d; color: #86efac; }
        
        .component-scores {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .component {
            text-align: center;
            padding: 15px;
            background: #161b22;
            border-radius: 8px;
        }
        .component-name { color: #8b949e; font-size: 0.85em; margin-bottom: 5px; }
        .component-value { font-size: 1.5em; font-weight: 600; }
        
        .risk-factors {
            background: #1c1917;
            border: 1px solid #44403c;
            border-radius: 8px;
            padding: 15px;
        }
        .risk-factors h3 {
            color: #fbbf24;
            margin-bottom: 10px;
            font-size: 0.95em;
        }
        .risk-factors ul {
            list-style: none;
            padding: 0;
        }
        .risk-factors li {
            padding: 8px 0;
            border-bottom: 1px solid #292524;
            color: #d6d3d1;
            font-size: 0.9em;
        }
        .risk-factors li:last-child { border-bottom: none; }
        .risk-factors li::before {
            content: "⚠️ ";
        }
        
        .recommendation {
            margin-top: 15px;
            padding: 15px;
            background: #172554;
            border: 1px solid #1e40af;
            border-radius: 8px;
            color: #93c5fd;
        }
        
        .signals {
            margin-top: 20px;
        }
        .signal-section {
            margin-bottom: 15px;
            padding: 15px;
            background: #161b22;
            border-radius: 8px;
        }
        .signal-section h4 {
            color: #a78bfa;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        .signal-detail {
            font-size: 0.85em;
            color: #8b949e;
            margin: 5px 0;
        }
        
        .method-tags {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .method-tag {
            background: #30363d;
            color: #8b949e;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
        }
        
        .nav {
            margin-bottom: 20px;
        }
        .nav a {
            color: #58a6ff;
            text-decoration: none;
        }
        .nav a:hover { text-decoration: underline; }
        
        .info-box {
            background: #0c4a6e;
            border: 1px solid #0369a1;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #7dd3fc;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav"><a href="/">← Back to Chaos Lab</a></div>
        
        <h1>🛡️ BEC Detection Engine</h1>
        <p class="subtitle">Multi-signal Business Email Compromise detection using blockchain forensics, intelligence tradecraft, and forensic linguistics</p>
        
        <div class="info-box">
            <strong>How it works:</strong> This engine combines three independent detection signals that attackers can't easily fake:
            <strong>Trust Graph</strong> (relationship history), <strong>Temporal Patterns</strong> (when they email), and <strong>Stylometry</strong> (how they write).
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📧 Analyze Email</h2>
                <form id="analyzeForm">
                    <label>From Address</label>
                    <input type="email" id="fromAddr" placeholder="sender@example.com" required>
                    
                    <label>To Address</label>
                    <input type="email" id="toAddr" placeholder="recipient@cyrenity.com" value="bbrown@cyrenity.com">
                    
                    <label>Subject</label>
                    <input type="text" id="subject" placeholder="Email subject" required>
                    
                    <label>Body</label>
                    <textarea id="body" placeholder="Email body content..." required></textarea>
                    
                    <label>Payment Request Amount ($)</label>
                    <input type="number" id="amount" placeholder="0.00" step="0.01" value="0">
                    
                    <label>Sender's Timezone</label>
                    <select id="timezone">
                        <option value="-480">PST (UTC-8)</option>
                        <option value="-420">MST (UTC-7)</option>
                        <option value="-360" selected>CST (UTC-6)</option>
                        <option value="-300">EST (UTC-5)</option>
                        <option value="0">UTC</option>
                        <option value="60">CET (UTC+1)</option>
                        <option value="180">MSK (UTC+3)</option>
                        <option value="480">CST China (UTC+8)</option>
                        <option value="540">JST (UTC+9)</option>
                    </select>
                    
                    <button type="submit" id="submitBtn">🔍 Analyze for BEC</button>
                </form>
            </div>
            
            <div class="card">
                <h2>📊 Analysis Result</h2>
                <div id="resultPlaceholder" style="color: #484f58; text-align: center; padding: 40px;">
                    Enter an email and click Analyze to see results
                </div>
                <div id="result" class="result">
                    <div class="risk-score" id="riskScore">0.00</div>
                    <div class="risk-level" id="riskLevel">ANALYZING...</div>
                    
                    <div class="component-scores">
                        <div class="component">
                            <div class="component-name">Trust Graph</div>
                            <div class="component-value" id="trustScore">-</div>
                        </div>
                        <div class="component">
                            <div class="component-name">Temporal</div>
                            <div class="component-value" id="temporalScore">-</div>
                        </div>
                        <div class="component">
                            <div class="component-name">Stylometry</div>
                            <div class="component-value" id="stylometryScore">-</div>
                        </div>
                    </div>
                    
                    <div class="risk-factors" id="riskFactors">
                        <h3>⚠️ Risk Factors Detected</h3>
                        <ul id="riskFactorsList"></ul>
                    </div>
                    
                    <div class="recommendation" id="recommendation"></div>
                    
                    <div class="signals" id="signals"></div>
                </div>
                
                <div class="method-tags">
                    <span class="method-tag">🔗 Blockchain Forensics</span>
                    <span class="method-tag">🕵️ Intel Tradecraft</span>
                    <span class="method-tag">📝 Forensic Linguistics</span>
                    <span class="method-tag">🎰 Casino Surveillance</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('submitBtn');
            btn.disabled = true;
            btn.textContent = 'Analyzing...';
            
            const data = {
                from_addr: document.getElementById('fromAddr').value,
                to_addr: document.getElementById('toAddr').value,
                subject: document.getElementById('subject').value,
                body: document.getElementById('body').value,
                amount: parseFloat(document.getElementById('amount').value) || 0,
                timezone_offset: parseInt(document.getElementById('timezone').value)
            };
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                displayResult(result);
            } catch (error) {
                alert('Error analyzing email: ' + error.message);
            } finally {
                btn.disabled = false;
                btn.textContent = '🔍 Analyze for BEC';
            }
        });
        
        function displayResult(result) {
            document.getElementById('resultPlaceholder').style.display = 'none';
            document.getElementById('result').classList.add('show');
            
            // Risk score
            const score = result.overall_risk_score;
            document.getElementById('riskScore').textContent = score.toFixed(2);
            document.getElementById('riskScore').style.color = getScoreColor(score);
            
            // Risk level
            const levelEl = document.getElementById('riskLevel');
            levelEl.textContent = result.risk_level;
            levelEl.className = 'risk-level risk-' + result.risk_level;
            
            // Component scores
            document.getElementById('trustScore').textContent = result.trust_score.toFixed(2);
            document.getElementById('temporalScore').textContent = result.temporal_score.toFixed(2);
            document.getElementById('stylometryScore').textContent = result.stylometry_score.toFixed(2);
            
            // Risk factors
            const factorsList = document.getElementById('riskFactorsList');
            factorsList.innerHTML = '';
            if (result.all_risk_factors.length === 0) {
                factorsList.innerHTML = '<li style="color: #86efac;">No risk factors detected</li>';
            } else {
                result.all_risk_factors.forEach(factor => {
                    const li = document.createElement('li');
                    li.textContent = factor;
                    factorsList.appendChild(li);
                });
            }
            
            // Recommendation
            document.getElementById('recommendation').innerHTML = '<strong>Recommendation:</strong> ' + result.recommendation;
            
            // Detailed signals
            const signalsDiv = document.getElementById('signals');
            signalsDiv.innerHTML = '';
            
            // Trust findings
            if (result.trust_findings) {
                signalsDiv.innerHTML += buildSignalSection('🔗 Trust Graph Analysis', result.trust_findings);
            }
            
            // Temporal findings  
            if (result.temporal_findings) {
                signalsDiv.innerHTML += buildSignalSection('⏰ Temporal Analysis', result.temporal_findings);
            }
            
            // Stylometry findings
            if (result.stylometry_findings) {
                signalsDiv.innerHTML += buildSignalSection('📝 Stylometry Analysis', result.stylometry_findings);
            }
        }
        
        function getScoreColor(score) {
            if (score >= 0.7) return '#ef4444';
            if (score >= 0.5) return '#f97316';
            if (score >= 0.3) return '#eab308';
            return '#22c55e';
        }
        
        function buildSignalSection(title, findings) {
            let html = '<div class="signal-section"><h4>' + title + '</h4>';
            for (const [key, value] of Object.entries(findings)) {
                html += '<div class="signal-detail"><strong>' + formatKey(key) + ':</strong> ' + formatValue(value) + '</div>';
            }
            html += '</div>';
            return html;
        }
        
        function formatKey(key) {
            return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
        
        function formatValue(value) {
            if (typeof value === 'number') return value.toFixed(3);
            if (typeof value === 'boolean') return value ? 'Yes' : 'No';
            if (Array.isArray(value)) return value.join(', ') || 'None';
            return String(value);
        }
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze an email for BEC indicators"""
    data = request.json
    
    email = EmailToAnalyze(
        from_addr=data.get('from_addr', ''),
        to_addr=data.get('to_addr', ''),
        subject=data.get('subject', ''),
        body=data.get('body', ''),
        timestamp=datetime.utcnow(),
        timezone_offset=data.get('timezone_offset', 0),
        has_payment_request=data.get('amount', 0) > 0,
        amount_requested=data.get('amount', 0)
    )
    
    result = scorer.analyze(email)
    
    return jsonify({
        'overall_risk_score': result.overall_risk_score,
        'risk_level': result.risk_level,
        'recommendation': result.recommendation,
        'trust_score': result.trust_score,
        'temporal_score': result.temporal_score,
        'stylometry_score': result.stylometry_score,
        'trust_findings': result.trust_findings,
        'temporal_findings': result.temporal_findings,
        'stylometry_findings': result.stylometry_findings,
        'all_risk_factors': result.all_risk_factors
    })


@app.route('/api/stats')
def stats():
    """Get scorer statistics"""
    return jsonify({
        'trained_senders': len(scorer.stylometry_engine.sender_profiles),
        'trust_graph_nodes': len(scorer.trust_graph.graph.nodes),
        'trust_graph_edges': len(scorer.trust_graph.graph.edges),
        'executives': list(scorer.trust_graph.executives),
        'is_trained': scorer.is_trained
    })


if __name__ == '__main__':
    print("Starting BEC Detection Engine on http://0.0.0.0:5006")
    app.run(host='0.0.0.0', port=5006, debug=False)
