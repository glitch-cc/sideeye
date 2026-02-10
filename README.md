# BEC Trust Analyzer

A multi-signal Business Email Compromise (BEC) detection system that combines unconventional approaches from blockchain forensics, intelligence analysis, and forensic linguistics.

## 🎯 The Concept

Traditional BEC detection focuses on:
- Email authentication (SPF/DKIM/DMARC)
- URL/attachment scanning
- Known bad sender lists

This misses sophisticated attacks. Our approach treats email like a **trust ledger** — every interaction builds or erodes trust, and we analyze multiple behavioral signals that attackers can't easily fake.

## 🧠 The Five Approaches

This project explores 5 unique detection methods (see [RESEARCH.md](RESEARCH.md)):

1. **Forensic Stylometry** - Writing fingerprint analysis (like identifying anonymous authors)
2. **Pattern-of-Life Analysis** - Temporal behavior profiling (from intelligence tradecraft)
3. **Trust Graph Analysis** - Blockchain-style relationship mapping
4. **Deception Markers** - Linguistic indicators from psychology research
5. **Casino-Style Surveillance** - Holistic behavioral monitoring

The POC implements a hybrid of approaches 1-3.

## 📁 Project Structure

```
bec-detection/
├── README.md           # This file
├── RESEARCH.md         # Full research document
├── trust_graph.py      # Blockchain-style trust propagation
├── temporal_analyzer.py # Pattern-of-life detection
├── stylometry_engine.py # Writing fingerprint analysis
├── bec_scorer.py       # Combined multi-signal scorer
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### Installation

```bash
cd /root/.openclaw/workspace/projects/bec-detection
pip install -r requirements.txt  # No external deps needed!
```

### Run the Demo

```bash
# Full integrated demo
python bec_scorer.py

# Individual component demos
python trust_graph.py
python temporal_analyzer.py
python stylometry_engine.py
```

### Sample Output

```
============================================================
BEC TRUST ANALYZER - Multi-Signal Detection Demo
============================================================

SCENARIO 2: Obvious BEC Attack (Wrong Style + Unknown Sender)
============================================================
Risk Score: 0.87
Risk Level: CRITICAL
Recommendation: BLOCK: Do not proceed. Verify through phone call to known number.
Component Scores - Trust: 0.85, Temporal: 0.75, Style: 0.82
Risk Factors: ['UNKNOWN_SENDER', 'LOW_TRUST', 'UNUSUAL_HOUR', 'TIMEZONE_MISMATCH', ...]
```

## 💡 How It Works

### 1. Trust Graph (Inspired by Chainalysis)

Every email is a "transaction" that builds relationship history:

```python
from trust_graph import TrustGraph, EmailInteraction

graph = TrustGraph("yourcompany.com")
graph.add_executive("ceo@yourcompany.com")

# Add historical emails
graph.add_interaction(EmailInteraction(
    from_addr="vendor@example.com",
    to_addr="accounts@yourcompany.com",
    timestamp=datetime.now(),
    subject="Invoice"
))

# Propagate trust through the network
graph.propagate_trust()

# Analyze a payment request
result = graph.analyze_payment_request(
    from_addr="new-vendor@unknown.com",
    to_addr="accounts@yourcompany.com",
    amount=50000
)
# Returns: risk_score, risk_factors, recommendation
```

### 2. Temporal Analyzer (Inspired by Intelligence Tradecraft)

Builds a "circadian fingerprint" for each sender:

```python
from temporal_analyzer import TemporalAnalyzer, EmailEvent

analyzer = TemporalAnalyzer()

# Train on historical emails
analyzer.add_email(EmailEvent(
    sender="ceo@company.com",
    timestamp=datetime(...),
    timezone_offset=-300  # EST
))

analyzer.finalize_profiles()

# Analyze new email
result = analyzer.analyze_email(EmailEvent(
    sender="ceo@company.com",
    timestamp=datetime.now().replace(hour=3),  # 3 AM?!
    timezone_offset=480  # From Asia?!
))
# Returns: anomaly_score, anomalies list
```

### 3. Stylometry Engine (Inspired by Forensic Linguistics)

Builds writing fingerprints from function words, sentence patterns, etc:

```python
from stylometry_engine import StylometryEngine

engine = StylometryEngine()

# Train on known emails
engine.add_sample("ceo@company.com", "Thank you for the update...")
engine.build_profile("ceo@company.com")

# Compare new email to profile
result = engine.compare_to_profile(
    "Hey!! Wire money ASAP!!!",  # Obviously different style
    "ceo@company.com"
)
# Returns: similarity score, deviations
```

### 4. Combined BEC Scorer

Brings everything together:

```python
from bec_scorer import BECScorer, EmailToAnalyze

scorer = BECScorer("yourcompany.com")
scorer.add_executive("ceo@yourcompany.com")

# Train on 6 months of email
for email in historical_emails:
    scorer.train_on_email(email)
    
scorer.finalize_training()

# Analyze incoming email
result = scorer.analyze_email(EmailToAnalyze(
    from_addr="ceo@yourcompany.com",
    to_addr="cfo@yourcompany.com",
    subject="Urgent Wire Transfer",
    body="...",
    timestamp=datetime.now(),
    has_payment_request=True,
    amount_requested=50000
))

print(f"Risk: {result.risk_level}")  # CRITICAL / HIGH / MEDIUM / LOW
print(f"Recommendation: {result.recommendation}")
```

## 🔬 What Makes This Different

| Traditional Detection | Our Approach |
|----------------------|--------------|
| Check sender reputation | Build relationship graph with trust propagation |
| Scan for malicious URLs | Analyze temporal behavior patterns |
| Keyword matching | Forensic stylometry analysis |
| Single-point-in-time | Continuous behavioral baseline |
| Binary good/bad | Probabilistic risk scoring |

## 🎰 The Casino Insight

Casinos don't catch cheaters by watching single hands — they build player profiles over time and detect when behavior deviates from the baseline. We do the same for email:

- **Every email is logged** (like casino floor surveillance)
- **Behavioral baselines are built** (like player tracking)
- **Deviations trigger investigation** (like pit boss alerts)
- **Conspiracy detection** (finding coordinated attacks)

## 📊 Scoring Weights

Default weights for the combined score:

```python
weights = {
    'trust': 0.35,       # Relationship/graph position
    'temporal': 0.30,    # Timing patterns
    'stylometry': 0.25,  # Writing style
    'payment': 0.10      # Payment request indicators
}
```

Adjust based on your organization's risk profile.

## 🚧 Limitations & Future Work

**Current Limitations:**
- Requires sufficient email history for training (50+ emails per executive)
- No email authentication (SPF/DKIM) integration in POC
- Single-organization focus (no cross-org threat intel)

**Future Enhancements:**
- Integration with email gateway (Microsoft 365, Google Workspace)
- Real-time scoring API
- ML-enhanced stylometry with transformers
- Cross-organization threat sharing
- Slack/Teams extension

## 📚 Research Sources

See [RESEARCH.md](RESEARCH.md) for full citations, including:
- Zhou et al. on linguistic deception detection
- Chainalysis methodology for transaction graph analysis
- SEC ARTEMIS system for temporal pattern detection
- Forensic stylometry academic literature

## 📝 License

MIT License - Use responsibly for defensive security purposes.

---

Built with 🧠 by exploring blockchain forensics, intelligence tradecraft, and forensic linguistics.
