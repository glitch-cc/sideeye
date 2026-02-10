#!/usr/bin/env python3
"""
BEC Detection Web Interface v2
Better UX: drag-drop .eml, paste screenshots, paste raw email
"""

from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
from email import policy
from email.parser import BytesParser
import base64
import re
from bec_scorer import BECScorer, EmailToAnalyze

app = Flask(__name__)

# Initialize scorer with demo domain
scorer = BECScorer("cyrenity.com")
scorer.add_executive("bbrown@cyrenity.com")
scorer.add_executive("cfo@cyrenity.com")

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
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { 
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #f97316, #ef4444, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { color: #8b949e; margin-bottom: 30px; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 1000px) { .grid { grid-template-columns: 1fr; } }
        
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 24px;
        }
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #f0f6fc;
        }
        
        /* Tab navigation */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 10px;
        }
        .tab {
            padding: 10px 20px;
            background: transparent;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #8b949e;
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.2s;
        }
        .tab:hover { border-color: #58a6ff; color: #58a6ff; }
        .tab.active { background: #238636; border-color: #238636; color: white; }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Drop zone */
        .drop-zone {
            border: 2px dashed #30363d;
            border-radius: 12px;
            padding: 60px 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #0d1117;
        }
        .drop-zone:hover, .drop-zone.dragover {
            border-color: #58a6ff;
            background: rgba(88, 166, 255, 0.05);
        }
        .drop-zone.has-file {
            border-color: #238636;
            background: rgba(35, 134, 54, 0.1);
        }
        .drop-zone-icon { font-size: 3em; margin-bottom: 15px; }
        .drop-zone-text { color: #8b949e; margin-bottom: 10px; }
        .drop-zone-hint { color: #484f58; font-size: 0.85em; }
        .drop-zone input[type="file"] { display: none; }
        .file-name {
            margin-top: 15px;
            padding: 10px;
            background: #161b22;
            border-radius: 6px;
            color: #58a6ff;
            font-family: monospace;
        }
        
        /* Screenshot paste area */
        .paste-zone {
            border: 2px dashed #30363d;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            min-height: 200px;
            background: #0d1117;
            cursor: pointer;
            transition: all 0.3s;
        }
        .paste-zone:hover, .paste-zone:focus {
            border-color: #a855f7;
            background: rgba(168, 85, 247, 0.05);
            outline: none;
        }
        .paste-zone.has-image {
            padding: 20px;
            border-color: #238636;
        }
        .paste-zone img {
            max-width: 100%;
            max-height: 300px;
            border-radius: 8px;
        }
        .paste-hint {
            color: #8b949e;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        /* Raw paste textarea */
        .raw-paste {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #c9d1d9;
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 13px;
            resize: vertical;
            line-height: 1.5;
        }
        .raw-paste:focus { border-color: #58a6ff; outline: none; }
        .raw-paste::placeholder { color: #484f58; }
        
        /* Analyze button */
        .analyze-btn {
            width: 100%;
            padding: 16px 24px;
            background: linear-gradient(90deg, #f97316, #ef4444);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            font-size: 1.1em;
            cursor: pointer;
            transition: opacity 0.2s;
            margin-top: 20px;
        }
        .analyze-btn:hover { opacity: 0.9; }
        .analyze-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        /* Results */
        .result { display: none; }
        .result.show { display: block; }
        
        .risk-display {
            text-align: center;
            padding: 30px;
            background: #0d1117;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .risk-score {
            font-size: 4em;
            font-weight: 700;
            line-height: 1;
        }
        .risk-label {
            font-size: 1.5em;
            font-weight: 600;
            margin-top: 10px;
            padding: 8px 20px;
            border-radius: 8px;
            display: inline-block;
        }
        .risk-CRITICAL { background: #7f1d1d; color: #fca5a5; }
        .risk-HIGH { background: #7c2d12; color: #fdba74; }
        .risk-MEDIUM { background: #713f12; color: #fde047; }
        .risk-LOW { background: #14532d; color: #86efac; }
        
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .score-card {
            background: #0d1117;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .score-card-label { color: #8b949e; font-size: 0.85em; margin-bottom: 5px; }
        .score-card-value { font-size: 1.8em; font-weight: 600; }
        
        .risk-factors {
            background: #1c1917;
            border: 1px solid #44403c;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .risk-factors h3 { color: #fbbf24; margin-bottom: 15px; }
        .risk-factors ul { list-style: none; }
        .risk-factors li {
            padding: 10px 0;
            border-bottom: 1px solid #292524;
            color: #d6d3d1;
        }
        .risk-factors li:last-child { border-bottom: none; }
        .risk-factors li::before { content: "⚠️ "; }
        .no-risks { color: #86efac; }
        .no-risks::before { content: "✅ " !important; }
        
        .recommendation {
            background: #172554;
            border: 1px solid #1e40af;
            border-radius: 8px;
            padding: 20px;
            color: #93c5fd;
        }
        
        .parsed-info {
            background: #0d1117;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 0.9em;
        }
        .parsed-info-row {
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #21262d;
        }
        .parsed-info-row:last-child { border-bottom: none; }
        .parsed-info-label { color: #8b949e; width: 100px; flex-shrink: 0; }
        .parsed-info-value { color: #c9d1d9; word-break: break-all; }
        
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
        
        .nav { margin-bottom: 20px; }
        .nav a { color: #58a6ff; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        
        .processing {
            display: none;
            text-align: center;
            padding: 40px;
        }
        .processing.show { display: block; }
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid #30363d;
            border-top-color: #58a6ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav"><a href="/">← Back to Chaos Lab</a></div>
        
        <h1>🛡️ BEC Detection Engine</h1>
        <p class="subtitle">Multi-signal Business Email Compromise detection</p>
        
        <div class="grid">
            <div class="card">
                <h2>📧 Submit Email for Analysis</h2>
                
                <div class="tabs">
                    <button class="tab active" data-tab="upload">📎 Upload .eml</button>
                    <button class="tab" data-tab="screenshot">📷 Screenshot</button>
                    <button class="tab" data-tab="paste">📋 Paste Raw</button>
                </div>
                
                <!-- Upload .eml tab -->
                <div id="tab-upload" class="tab-content active">
                    <div class="drop-zone" id="dropZone">
                        <div class="drop-zone-icon">📁</div>
                        <div class="drop-zone-text">Drag & drop .eml or .msg file here</div>
                        <div class="drop-zone-hint">or click to browse</div>
                        <input type="file" id="fileInput" accept=".eml,.msg,.txt">
                        <div class="file-name" id="fileName" style="display:none"></div>
                    </div>
                </div>
                
                <!-- Screenshot tab -->
                <div id="tab-screenshot" class="tab-content">
                    <div class="paste-zone" id="pasteZone" tabindex="0">
                        <div class="drop-zone-icon">📷</div>
                        <div class="drop-zone-text">Click here and paste screenshot</div>
                        <div class="paste-hint">Ctrl+V / Cmd+V after clicking</div>
                    </div>
                    <p style="color: #f97316; margin-top: 15px; font-size: 0.85em;">
                        ⚠️ Screenshot OCR requires OpenAI API key (not configured)
                    </p>
                </div>
                
                <!-- Paste raw tab -->
                <div id="tab-paste" class="tab-content">
                    <textarea class="raw-paste" id="rawPaste" placeholder="Paste the email content here...

From: cfo@company.com
To: you@company.com
Subject: Urgent wire transfer needed

Hi,

I need you to process an urgent payment..."></textarea>
                </div>
                
                <button class="analyze-btn" id="analyzeBtn">🔍 Analyze for BEC</button>
                
                <div class="method-tags">
                    <span class="method-tag">🔗 Trust Graph</span>
                    <span class="method-tag">⏰ Temporal Analysis</span>
                    <span class="method-tag">📝 Stylometry</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Analysis Result</h2>
                
                <div id="placeholder" style="color: #484f58; text-align: center; padding: 60px 20px;">
                    <div style="font-size: 3em; margin-bottom: 15px;">📨</div>
                    <div>Upload or paste an email to analyze</div>
                </div>
                
                <div class="processing" id="processing">
                    <div class="spinner"></div>
                    <div>Analyzing email...</div>
                </div>
                
                <div class="result" id="result">
                    <div class="parsed-info" id="parsedInfo"></div>
                    
                    <div class="risk-display">
                        <div class="risk-score" id="riskScore">0.00</div>
                        <div class="risk-label" id="riskLabel">ANALYZING</div>
                    </div>
                    
                    <div class="scores-grid">
                        <div class="score-card">
                            <div class="score-card-label">Trust Graph</div>
                            <div class="score-card-value" id="trustScore">-</div>
                        </div>
                        <div class="score-card">
                            <div class="score-card-label">Temporal</div>
                            <div class="score-card-value" id="temporalScore">-</div>
                        </div>
                        <div class="score-card">
                            <div class="score-card-label">Stylometry</div>
                            <div class="score-card-value" id="stylometryScore">-</div>
                        </div>
                    </div>
                    
                    <div class="risk-factors" id="riskFactors">
                        <h3>⚠️ Risk Factors</h3>
                        <ul id="riskList"></ul>
                    </div>
                    
                    <div class="recommendation" id="recommendation"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
            });
        });
        
        // File upload / drag-drop
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        let uploadedFile = null;
        
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleFile(fileInput.files[0]);
            }
        });
        
        function handleFile(file) {
            uploadedFile = file;
            dropZone.classList.add('has-file');
            fileName.style.display = 'block';
            fileName.textContent = file.name;
        }
        
        // Screenshot paste
        const pasteZone = document.getElementById('pasteZone');
        let pastedImage = null;
        
        pasteZone.addEventListener('paste', (e) => {
            const items = e.clipboardData.items;
            for (let item of items) {
                if (item.type.startsWith('image/')) {
                    const file = item.getAsFile();
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        pastedImage = e.target.result;
                        pasteZone.innerHTML = '<img src="' + pastedImage + '">';
                        pasteZone.classList.add('has-image');
                    };
                    reader.readAsDataURL(file);
                    break;
                }
            }
        });
        
        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', async () => {
            const btn = document.getElementById('analyzeBtn');
            const activeTab = document.querySelector('.tab.active').dataset.tab;
            
            btn.disabled = true;
            document.getElementById('placeholder').style.display = 'none';
            document.getElementById('result').classList.remove('show');
            document.getElementById('processing').classList.add('show');
            
            try {
                let response;
                
                if (activeTab === 'upload' && uploadedFile) {
                    const formData = new FormData();
                    formData.append('file', uploadedFile);
                    response = await fetch('/api/analyze-file', {
                        method: 'POST',
                        body: formData
                    });
                } else if (activeTab === 'screenshot' && pastedImage) {
                    response = await fetch('/api/analyze-screenshot', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: pastedImage })
                    });
                } else if (activeTab === 'paste') {
                    const rawText = document.getElementById('rawPaste').value;
                    if (!rawText.trim()) {
                        alert('Please paste email content first');
                        throw new Error('No content');
                    }
                    response = await fetch('/api/analyze-raw', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ raw: rawText })
                    });
                } else {
                    alert('Please upload a file, paste a screenshot, or paste raw email text');
                    throw new Error('No input');
                }
                
                const result = await response.json();
                if (result.error) {
                    alert('Error: ' + result.error);
                    throw new Error(result.error);
                }
                displayResult(result);
            } catch (error) {
                console.error(error);
            } finally {
                btn.disabled = false;
                document.getElementById('processing').classList.remove('show');
            }
        });
        
        function displayResult(result) {
            document.getElementById('result').classList.add('show');
            
            // Parsed info
            const parsedInfo = document.getElementById('parsedInfo');
            parsedInfo.innerHTML = `
                <div class="parsed-info-row">
                    <div class="parsed-info-label">From:</div>
                    <div class="parsed-info-value">${result.parsed?.from || 'Unknown'}</div>
                </div>
                <div class="parsed-info-row">
                    <div class="parsed-info-label">To:</div>
                    <div class="parsed-info-value">${result.parsed?.to || 'Unknown'}</div>
                </div>
                <div class="parsed-info-row">
                    <div class="parsed-info-label">Subject:</div>
                    <div class="parsed-info-value">${result.parsed?.subject || 'Unknown'}</div>
                </div>
            `;
            
            // Risk score
            const score = result.overall_risk_score;
            document.getElementById('riskScore').textContent = score.toFixed(2);
            document.getElementById('riskScore').style.color = getScoreColor(score);
            
            const label = document.getElementById('riskLabel');
            label.textContent = result.risk_level;
            label.className = 'risk-label risk-' + result.risk_level;
            
            // Component scores
            document.getElementById('trustScore').textContent = result.trust_score?.toFixed(2) || '-';
            document.getElementById('temporalScore').textContent = result.temporal_score?.toFixed(2) || '-';
            document.getElementById('stylometryScore').textContent = result.stylometry_score?.toFixed(2) || '-';
            
            // Risk factors
            const riskList = document.getElementById('riskList');
            riskList.innerHTML = '';
            if (!result.all_risk_factors || result.all_risk_factors.length === 0) {
                riskList.innerHTML = '<li class="no-risks">No risk factors detected</li>';
            } else {
                result.all_risk_factors.forEach(factor => {
                    const li = document.createElement('li');
                    li.textContent = factor;
                    riskList.appendChild(li);
                });
            }
            
            // Recommendation
            document.getElementById('recommendation').innerHTML = 
                '<strong>Recommendation:</strong> ' + (result.recommendation || 'Review manually');
        }
        
        function getScoreColor(score) {
            if (score >= 0.7) return '#ef4444';
            if (score >= 0.5) return '#f97316';
            if (score >= 0.3) return '#eab308';
            return '#22c55e';
        }
    </script>
</body>
</html>
"""


def parse_eml(content):
    """Parse .eml file content"""
    try:
        msg = BytesParser(policy=policy.default).parsebytes(content)
        
        # Get body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_content()
                    break
        else:
            body = msg.get_content()
        
        return {
            'from': msg.get('From', ''),
            'to': msg.get('To', ''),
            'subject': msg.get('Subject', ''),
            'body': body if isinstance(body, str) else str(body),
            'date': msg.get('Date', '')
        }
    except Exception as e:
        return {'error': str(e)}


def parse_raw_email(raw):
    """Parse raw pasted email text"""
    lines = raw.strip().split('\n')
    
    from_addr = ''
    to_addr = ''
    subject = ''
    body_lines = []
    in_body = False
    
    for line in lines:
        line_lower = line.lower()
        if not in_body:
            if line_lower.startswith('from:'):
                from_addr = line[5:].strip()
                # Extract just email if it's "Name <email>"
                match = re.search(r'<([^>]+)>', from_addr)
                if match:
                    from_addr = match.group(1)
            elif line_lower.startswith('to:'):
                to_addr = line[3:].strip()
                match = re.search(r'<([^>]+)>', to_addr)
                if match:
                    to_addr = match.group(1)
            elif line_lower.startswith('subject:'):
                subject = line[8:].strip()
            elif line.strip() == '':
                in_body = True
        else:
            body_lines.append(line)
    
    # If no headers found, treat whole thing as body
    if not from_addr and not to_addr and not subject:
        body_lines = lines
    
    return {
        'from': from_addr or 'unknown@example.com',
        'to': to_addr or 'bbrown@cyrenity.com',
        'subject': subject or '(no subject)',
        'body': '\n'.join(body_lines)
    }


@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    """Analyze uploaded .eml file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    content = file.read()
    
    parsed = parse_eml(content)
    if 'error' in parsed:
        return jsonify({'error': parsed['error']})
    
    return analyze_parsed(parsed)


@app.route('/api/analyze-raw', methods=['POST'])
def analyze_raw():
    """Analyze raw pasted email"""
    data = request.json
    raw = data.get('raw', '')
    
    if not raw.strip():
        return jsonify({'error': 'No email content provided'})
    
    parsed = parse_raw_email(raw)
    return analyze_parsed(parsed)


@app.route('/api/analyze-screenshot', methods=['POST'])
def analyze_screenshot():
    """Analyze screenshot (requires OCR)"""
    # For now, return error - would need OCR integration
    return jsonify({
        'error': 'Screenshot OCR not configured. Please use file upload or paste raw email text.'
    })


def analyze_parsed(parsed):
    """Run BEC analysis on parsed email"""
    email = EmailToAnalyze(
        from_addr=parsed.get('from', ''),
        to_addr=parsed.get('to', ''),
        subject=parsed.get('subject', ''),
        body=parsed.get('body', ''),
        timestamp=datetime.utcnow(),
        timezone_offset=-360,  # Default CST
        has_payment_request='wire' in parsed.get('body', '').lower() or 
                           'transfer' in parsed.get('body', '').lower() or
                           'payment' in parsed.get('body', '').lower(),
        amount_requested=0
    )
    
    result = scorer.analyze(email)
    
    return jsonify({
        'parsed': {
            'from': parsed.get('from', ''),
            'to': parsed.get('to', ''),
            'subject': parsed.get('subject', '')
        },
        'overall_risk_score': result.overall_risk_score,
        'risk_level': result.risk_level,
        'recommendation': result.recommendation,
        'trust_score': result.trust_score,
        'temporal_score': result.temporal_score,
        'stylometry_score': result.stylometry_score,
        'all_risk_factors': result.all_risk_factors
    })


@app.route('/api/stats')
def stats():
    """Get scorer statistics"""
    return jsonify({
        'trained_senders': len(scorer.stylometry_engine.sender_profiles),
        'trust_graph_nodes': len(scorer.trust_graph.nodes),
        'trust_graph_edges': len(scorer.trust_graph.edges),
        'executives': list(scorer.trust_graph.executives)
    })


if __name__ == '__main__':
    print("Starting BEC Detection Engine on http://0.0.0.0:5006")
    app.run(host='0.0.0.0', port=5006, debug=False)
