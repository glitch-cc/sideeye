# BEC Detection: Unconventional Approaches

## Executive Summary

This research explores 5 unique approaches to Business Email Compromise (BEC) detection, drawing insights from diverse fields: linguistics, blockchain forensics, behavioral biometrics, graph theory, and casino surveillance. Each approach offers a distinct advantage that traditional cybersecurity tools miss.

---

## Approach 1: Forensic Stylometry (from Literary Analysis)

### The Cross-Industry Insight
Just as literary scholars use stylometry to identify anonymous authors (famously used to confirm J.K. Rowling wrote "The Cuckoo's Calling" under a pseudonym), we can fingerprint legitimate executives and detect when an impersonator writes in their name.

### How It Works
- **Writing Fingerprint**: Every person has unique linguistic patterns:
  - Function word frequencies (the, a, but, however)
  - Sentence length distribution
  - Punctuation habits (semicolons vs dashes)
  - Formality markers and hedging language
  - Greeting/closing patterns
  
- **Baseline Construction**: Build a stylometric profile from 50+ legitimate emails per executive
- **Anomaly Detection**: Score incoming "executive" emails against their baseline
- **Alert Threshold**: Significant deviation triggers investigation

### Sources
- Zhou et al. (2004) - "Automating linguistics-based cues for detecting deception in text-based communications"
- Fast Data Science - Forensic Stylometry Library (Python)
- PMC11707938 - "Stylometry and forensic science: A literature review"

### Feasibility: ⭐⭐⭐⭐ (High)
- Well-established algorithms
- Only needs email history as training data
- False positive rate manageable with tuning

### Innovation: ⭐⭐⭐⭐ (High)
- Not commonly used in BEC detection
- Catches sophisticated attacks that pass content analysis

---

## Approach 2: Temporal Pattern-of-Life Analysis (from Intelligence Community)

### The Cross-Industry Insight
Intelligence analysts build "pattern of life" profiles to verify identity and detect anomalies. The CIA and NSA use communication timing, device switching, and behavioral rhythms to identify operatives. We can apply this to email.

### How It Works
- **Circadian Fingerprint**: When does the executive typically send emails?
  - Hour-of-day distribution
  - Day-of-week patterns
  - Response latency to different contacts
  
- **Timezone Consistency**: Cross-reference claimed timezone with:
  - Email header timestamps
  - Historical sending patterns
  - Known travel schedules (calendar integration)

- **Communication Rhythm**: How quickly do they respond to CFO vs random vendors?

### Red Flags
- CEO sends wire transfer request at 3 AM local time
- Email claims to be from NYC but headers show UTC+8 server
- Response time breaks historical patterns (usually replies in hours, now demanding response in minutes)

### Sources
- Behavioral Biometrics research (PMC8519005) - smartphone keyboard circadian patterns
- SEC's ARTEMIS system - temporal trading pattern analysis
- Counter-intelligence pattern-of-life analysis methodology

### Feasibility: ⭐⭐⭐⭐ (High)
- Requires email metadata (easily accessible)
- Calendar integration adds power
- Works immediately with historical data

### Innovation: ⭐⭐⭐⭐⭐ (Very High)
- Rarely seen in commercial BEC tools
- Catches attacks that perfectly mimic writing style but fail on timing

---

## Approach 3: Transaction Graph Analysis (from Blockchain Forensics)

### The Cross-Industry Insight
Chainalysis and Elliptic trace cryptocurrency laundering by building "wallet graphs" — clustering addresses that transact together and identifying patterns that indicate illicit activity. Apply this to email/payment relationships.

### How It Works
- **Communication Graph**: Build a network of who emails whom
  - Node = email address
  - Edge = email communication (weighted by frequency)
  - Attributes = relationship type, monetary value, history length

- **Trust Propagation**: Like PageRank for trust
  - Long-standing vendors have high trust scores
  - New addresses inherit some trust from who introduced them
  - Trust decays with suspicious behavior

- **Pattern Detection**:
  - "First-time vendor" requesting large payment
  - Vendor address suddenly changed (but same person claims to be contacting)
  - Graph anomalies: someone claiming existing relationship but no prior edges

### The Blockchain Parallel
Just as Chainalysis detects money laundering by finding:
- Rapid movement through many wallets
- Unusual clustering patterns
- Connections to known bad actors

We detect BEC by finding:
- New edges requesting high-value transactions
- Communication patterns that don't match claimed relationships
- Connections to known BEC infrastructure

### Sources
- Chainalysis Reactor methodology
- ScienceDirect: "Graph-based anomaly detection approaches in fraud detection"
- CMU: "Graph based Anomaly Detection and Description: A Survey"

### Feasibility: ⭐⭐⭐⭐ (High)
- Requires organizational email history
- Graph databases (Neo4j) handle scale well
- Integrates with existing email security

### Innovation: ⭐⭐⭐⭐ (High)
- Some vendors do basic relationship checking
- Full graph analysis with trust propagation is rare

---

## Approach 4: Linguistic Deception Markers (from Interrogation/Poker)

### The Cross-Industry Insight
Deception researchers (and poker players) know that lies manifest in language. The FBI's behavioral analysis unit and professional poker players look for specific linguistic tells. Academic NLP research has validated many of these markers.

### How It Works
- **Verifiability Analysis**: Truth-tellers include checkable details; liars avoid them
  - "I'm in a meeting" (vague) vs "I'm in the Q3 board meeting in Room 401" (verifiable)
  
- **Cognitive Load Markers**: Lying is mentally taxing
  - Shorter sentences under pressure
  - Less complex grammar
  - More repetition
  
- **Urgency Injection**: BEC relies on rushed decisions
  - "URGENT", "ASAP", "before end of day"
  - Unusual pressure tactics

- **Hedging & Certainty**: Deceivers hedge more OR overcompensate with excessive certainty
  - "I believe", "I think", "probably"
  - Or: "I absolutely need this immediately"

### Detection Markers (from Research)
| Marker | What It Indicates |
|--------|-------------------|
| Low verifiable details | Potential deception |
| Urgency language spike | BEC pressure tactic |
| Unusual formality shift | Identity inconsistency |
| Missing personal context | Impersonation gap |
| Cognitive load indicators | Deceptive composition |

### Sources
- Nature: "Verbal lie detection using Large Language Models" (2023)
- PMC: "Analysing Deception in Witness Memory through Linguistic Styles"
- MIT TACL: "Acoustic-Prosodic and Lexical Cues to Deception and Trust"
- Zhou's Linguistics-Based Cues (LBC) framework

### Feasibility: ⭐⭐⭐ (Medium)
- NLP models available (LIWC, custom transformers)
- Requires calibration per organization
- Some false positives with legitimate urgent requests

### Innovation: ⭐⭐⭐⭐ (High)
- Directly targets BEC's psychological manipulation
- Academic research validates the approach

---

## Approach 5: Casino-Style Behavioral Surveillance (from Gaming Industry)

### The Cross-Industry Insight 🎰 
Casinos detect cheaters not by looking at individual hands, but by monitoring behavioral patterns across time. They build player profiles, detect "advantage play," and catch conspiracies through relationship analysis. The pit boss doesn't just watch the cards — they watch the player.

### How It Works
**The Casino Model:**
1. **Player Profiling**: Track every interaction, build statistical baselines
2. **Anomaly Detection**: Real-time deviation from expected behavior
3. **Conspiracy Detection**: Find coordinated actors across the floor
4. **Heat Maps**: Identify where/when suspicious activity clusters

**Applied to BEC:**
1. **Executive Profiling**: 
   - Communication velocity (emails/day, response times)
   - Financial request patterns (amounts, frequencies, vendors)
   - Device/location patterns
   
2. **Real-Time Behavioral Scoring**:
   - Every email gets a "suspicion score"
   - Combines multiple signals (timing, language, recipient, request type)
   - Like a credit card fraud score

3. **Conspiracy Detection**:
   - Is there a pattern across the organization?
   - Multiple unusual wire requests in a week?
   - Same "vendor" contacting multiple employees?

4. **Investigation Triggers**:
   - Behavioral change > threshold → flag for review
   - Pattern matching against known BEC campaigns
   - "Card counting" equivalent: detecting systematic probing

### The Eye in the Sky
Casinos use "eye in the sky" cameras that record everything, then replay suspicious moments. 

**Our equivalent**: Log all email metadata + financial request content, enable retroactive pattern analysis when a BEC is discovered. "Who else did this attacker contact? What other requests look similar?"

### Sources
- Casino surveillance methodology (game protection)
- CrossClassify: "Detect behavioral anomalies across... carrier accounts, and third-party vendors"
- FINRA/SEC pattern surveillance systems

### Feasibility: ⭐⭐⭐ (Medium)
- Requires comprehensive logging
- Needs integration with financial systems
- Privacy considerations

### Innovation: ⭐⭐⭐⭐⭐ (Very High)
- Holistic behavioral monitoring is rare in email security
- Conspiracy detection across organization is almost nonexistent
- Retroactive analysis capability valuable for incident response

---

## THE MOST OUTRAGEOUS APPROACH 🎯

### Winner: **Temporal Pattern-of-Life + Blockchain Trust Graph Hybrid**

**Why This Is Wild:**

Combine intelligence community tradecraft with cryptocurrency forensics to create a **"Reputation Ledger"** — a continuously-updating trust graph where every email interaction is a transaction that builds or erodes trust.

**The Concept:**
1. Every email is a "transaction" on your internal trust graph
2. Trust propagates through the network (like PageRank, like Chainalysis entity clustering)
3. Temporal patterns create a "circadian signature" for each node
4. New payment requests must pass a "trust threshold" based on:
   - Graph position (how connected is this address?)
   - Temporal consistency (does timing match pattern-of-life?)
   - Linguistic fingerprint match
   - Verifiability of claims

**Why It's Defensive Genius:**
- Attackers can't fake relationship history
- Attackers can't fake circadian patterns easily
- Attackers can't fake graph position
- Even perfect content impersonation fails on these metrics

**The POC**: I'll build a prototype that scores incoming emails based on:
1. Sender trust score (graph position)
2. Temporal anomaly score (timing deviation)
3. Linguistic deviation score (stylometry mismatch)
4. Urgency/deception marker score

---

## Comparison Matrix

| Approach | Feasibility | Innovation | Catches What Others Miss |
|----------|-------------|------------|-------------------------|
| Stylometry | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Perfect grammar impersonators |
| Pattern-of-Life | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Timezone/timing inconsistencies |
| Trust Graph | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | First-time vendor fraud |
| Deception Markers | ⭐⭐⭐ | ⭐⭐⭐⭐ | Psychological manipulation |
| Casino Surveillance | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Coordinated attacks, patterns |

---

## POC Implementation Plan

Building: **BEC Trust Analyzer** — A multi-signal BEC detection system

### Components:
1. `trust_graph.py` — Email relationship graph with trust propagation
2. `temporal_analyzer.py` — Pattern-of-life deviation scoring
3. `stylometry_engine.py` — Writing style fingerprinting
4. `deception_detector.py` — Linguistic manipulation markers
5. `bec_scorer.py` — Combined scoring engine
6. `api.py` — REST API for email analysis

### Data Flow:
```
Email → Parse Headers → Extract Features → 
  → Trust Graph Position Score
  → Temporal Deviation Score  
  → Stylometry Match Score
  → Deception Marker Score
→ Combined BEC Risk Score → Alert/Pass
```

---

## References

1. Zhou, L., Burgoon, J. K., Nunamaker, J. F., & Twitchell, D. (2004). Automating linguistics-based cues for detecting deception in text-based asynchronous computer-mediated communications.
2. Grieve, J. (2007). Quantitative Authorship Attribution: an Evaluation of Techniques. Literary and Linguistic Computing.
3. Akoglu, L., Tong, H., & Koutra, D. (2015). Graph based Anomaly Detection and Description: A Survey. CMU.
4. Vrij, A. (2008). Detecting Lies and Deceit: Pitfalls and Opportunities. Wiley.
5. Chainalysis Reactor Documentation - Entity clustering and transaction tracing.
6. SEC ARTEMIS - Advanced Relational Trading Enforcement Metrics Investigation System.
