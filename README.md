# SideEye 👀

**Detects when someone else is using a compromised email account.**

Multi-signal account takeover detection using:
- 🔗 **Trust Graph** — Blockchain forensics-style relationship analysis
- ⏰ **Temporal Analysis** — Intelligence tradecraft pattern-of-life detection  
- 📝 **Stylometry** — Forensic linguistics writing fingerprint analysis

## The Problem

When an email account is compromised (BEC), attackers send emails *from* the legitimate account. Traditional security tools miss this because the email is "from" a trusted sender.

## The Insight

Attackers can fake email content, but they **cannot fake**:
- Relationship history (who this person normally emails)
- Circadian patterns (when they normally email)
- Writing fingerprint (how they write)

SideEye exploits these invariants.

## Live Demo

**https://chaos.cyrenitycyber.com/bec/**

## Quick Start

```bash
# Run locally
pip install flask
python web_app.py

# Or with Docker
docker compose up -d
```

## How It Works

1. **Train** on historical email to learn normal patterns
2. **Monitor** all email (including from "trusted" senders)
3. **Alert** when patterns don't match (wrong timezone, different writing style, unusual recipients)

## Files

- `trust_graph.py` — PageRank-style trust propagation
- `temporal_analyzer.py` — Circadian fingerprinting
- `stylometry_engine.py` — Writing style analysis
- `bec_scorer.py` — Combined multi-signal scorer
- `web_app.py` — Flask web interface

## Research

See [RESEARCH.md](RESEARCH.md) for the full methodology and cross-industry inspiration (blockchain forensics, intelligence tradecraft, casino surveillance, etc.).

## License

MIT
