"""
BEC Scorer - Combined multi-signal BEC detection engine

Combines insights from:
- Blockchain forensics (trust graphs)
- Intelligence community (pattern-of-life)
- Forensic linguistics (stylometry)
- Behavioral psychology (deception markers)

This is the "outrageous" hybrid approach - treating email like 
cryptocurrency transactions on a trust ledger.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from trust_graph import TrustGraph, EmailInteraction
from temporal_analyzer import TemporalAnalyzer, EmailEvent
from stylometry_engine import StylometryEngine


@dataclass
class EmailToAnalyze:
    """An incoming email to analyze for BEC indicators"""
    from_addr: str
    to_addr: str
    subject: str
    body: str
    timestamp: datetime
    timezone_offset: int = 0  # Minutes from UTC
    has_payment_request: bool = False
    amount_requested: float = 0.0
    message_id: str = ""
    in_reply_to: str = ""


@dataclass
class BECAnalysisResult:
    """Complete BEC analysis result"""
    # Overall scores
    overall_risk_score: float
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    recommendation: str
    
    # Component scores
    trust_score: float
    temporal_score: float
    stylometry_score: float
    
    # Detailed findings
    trust_findings: Dict
    temporal_findings: Dict
    stylometry_findings: Dict
    
    # Combined risk factors
    all_risk_factors: List[str]


class BECScorer:
    """
    Multi-signal BEC detection engine.
    
    Think of this as a "fraud score" like credit cards use,
    but specifically designed for business email compromise.
    
    Each signal catches different attack types:
    - Trust Graph: Catches unknown senders, fake vendors
    - Temporal: Catches wrong timezone, unusual hours
    - Stylometry: Catches writing style mismatches
    """
    
    def __init__(self, organization_domain: str):
        self.trust_graph = TrustGraph(organization_domain)
        self.temporal_analyzer = TemporalAnalyzer()
        self.stylometry_engine = StylometryEngine()
        self.is_trained = False
        
        # Weight configuration
        self.weights = {
            'trust': 0.35,       # Graph position and relationship
            'temporal': 0.30,   # Timing patterns
            'stylometry': 0.25, # Writing style
            'payment': 0.10     # Payment request indicators
        }
        
    def add_executive(self, email: str):
        """Mark an email as an executive (high-value target)"""
        self.trust_graph.add_executive(email)
        
    def train_on_email(self, email: EmailToAnalyze):
        """
        Add a historical email to training data.
        
        Call this for each email in your historical corpus.
        """
        # Add to trust graph
        self.trust_graph.add_interaction(EmailInteraction(
            from_addr=email.from_addr,
            to_addr=email.to_addr,
            timestamp=email.timestamp,
            subject=email.subject,
            has_payment_request=email.has_payment_request,
            amount_requested=email.amount_requested
        ))
        
        # Add to temporal analyzer
        self.temporal_analyzer.add_email(EmailEvent(
            sender=email.from_addr,
            recipient=email.to_addr,
            timestamp=email.timestamp,
            timezone_offset=email.timezone_offset,
            message_id=email.message_id,
            response_to=email.in_reply_to if email.in_reply_to else None
        ))
        
        # Add to stylometry (only for substantial emails)
        if len(email.body) > 100:
            self.stylometry_engine.add_sample(email.from_addr, email.body)
            
    def finalize_training(self):
        """
        Finalize training and build all profiles.
        
        Call this after adding all historical emails.
        """
        # Propagate trust through the graph
        self.trust_graph.propagate_trust()
        
        # Calculate temporal statistics
        self.temporal_analyzer.finalize_profiles()
        
        # Build stylometry profiles for all authors with enough samples
        for author in self.stylometry_engine.sample_texts.keys():
            self.stylometry_engine.build_profile(author)
            
        self.is_trained = True
        
    def analyze_email(self, email: EmailToAnalyze) -> BECAnalysisResult:
        """
        Analyze an email for BEC indicators.
        
        Returns comprehensive risk assessment with component scores.
        """
        if not self.is_trained:
            raise RuntimeError("Must call finalize_training() before analysis")
            
        all_risk_factors = []
        
        # === Component 1: Trust Graph Analysis ===
        if email.has_payment_request:
            trust_result = self.trust_graph.analyze_payment_request(
                from_addr=email.from_addr,
                to_addr=email.to_addr,
                amount=email.amount_requested
            )
        else:
            # Basic trust check without payment context
            trust_score = self.trust_graph.get_trust_score(email.from_addr)
            relationship = self.trust_graph.calculate_relationship_strength(
                email.from_addr, email.to_addr
            )
            trust_result = {
                "trust_score": trust_score,
                "relationship_strength": relationship,
                "risk_score": 0.0 if trust_score > 0.5 else (0.5 - trust_score),
                "risk_factors": []
            }
            
            if trust_score < 0.3:
                trust_result["risk_factors"].append(f"LOW_TRUST: Score {trust_score:.2f}")
            if relationship < 0.2:
                trust_result["risk_factors"].append("WEAK_RELATIONSHIP: Limited history")
                
        trust_risk = trust_result.get("risk_score", 0)
        all_risk_factors.extend(trust_result.get("risk_factors", []))
        
        # === Component 2: Temporal Analysis ===
        temporal_result = self.temporal_analyzer.analyze_email(EmailEvent(
            sender=email.from_addr,
            recipient=email.to_addr,
            timestamp=email.timestamp,
            timezone_offset=email.timezone_offset,
            message_id=email.message_id
        ))
        
        temporal_risk = temporal_result.get("anomaly_score", 0.5)
        all_risk_factors.extend(temporal_result.get("anomalies", []))
        
        # === Component 3: Stylometry Analysis ===
        stylometry_result = self.stylometry_engine.compare_to_profile(
            email.body, 
            email.from_addr
        )
        
        # Convert similarity to risk (low similarity = high risk)
        stylometry_risk = 1 - stylometry_result.get("similarity", 0.5)
        all_risk_factors.extend(stylometry_result.get("deviations", []))
        
        # === Component 4: Payment Request Indicators ===
        payment_risk = 0.0
        if email.has_payment_request:
            payment_risk = 0.2  # Base risk for any payment request
            
            # Higher amounts = higher risk
            if email.amount_requested > 50000:
                payment_risk += 0.3
                all_risk_factors.append(f"HIGH_VALUE: ${email.amount_requested:,.0f} requested")
            elif email.amount_requested > 10000:
                payment_risk += 0.1
                
            # Check for urgency in subject/body
            urgency_keywords = ['urgent', 'asap', 'immediately', 'rush', 'today', 'now']
            text_lower = (email.subject + " " + email.body).lower()
            urgency_count = sum(1 for kw in urgency_keywords if kw in text_lower)
            
            if urgency_count >= 2:
                payment_risk += 0.2
                all_risk_factors.append(f"URGENCY_PRESSURE: {urgency_count} urgency markers")
                
            # Check for secrecy requests
            secrecy_keywords = ['confidential', 'secret', 'dont tell', "don't tell", 
                               'between us', 'private', 'discreet']
            if any(kw in text_lower for kw in secrecy_keywords):
                payment_risk += 0.2
                all_risk_factors.append("SECRECY_REQUEST: Asks for confidentiality")
                
        # === Calculate Combined Score ===
        overall_risk = (
            self.weights['trust'] * trust_risk +
            self.weights['temporal'] * temporal_risk +
            self.weights['stylometry'] * stylometry_risk +
            self.weights['payment'] * payment_risk
        )
        
        # Clamp to 0-1
        overall_risk = max(0, min(1, overall_risk))
        
        # Determine risk level and recommendation
        if overall_risk >= 0.7:
            risk_level = "CRITICAL"
            recommendation = "BLOCK: Do not proceed. Verify through phone call to known number."
        elif overall_risk >= 0.5:
            risk_level = "HIGH"
            recommendation = "HOLD: Requires manager approval and verbal confirmation."
        elif overall_risk >= 0.3:
            risk_level = "MEDIUM"
            recommendation = "REVIEW: Examine request carefully. Consider verification."
        else:
            risk_level = "LOW"
            recommendation = "PROCEED: Normal risk level."
            
        return BECAnalysisResult(
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            recommendation=recommendation,
            trust_score=trust_risk,
            temporal_score=temporal_risk,
            stylometry_score=stylometry_risk,
            trust_findings=trust_result,
            temporal_findings=temporal_result,
            stylometry_findings=stylometry_result,
            all_risk_factors=all_risk_factors
        )
        
    def to_dict(self, result: BECAnalysisResult) -> Dict:
        """Convert result to JSON-serializable dict"""
        return {
            "overall_risk_score": round(result.overall_risk_score, 3),
            "risk_level": result.risk_level,
            "recommendation": result.recommendation,
            "component_scores": {
                "trust": round(result.trust_score, 3),
                "temporal": round(result.temporal_score, 3),
                "stylometry": round(result.stylometry_score, 3)
            },
            "risk_factors": result.all_risk_factors,
            "detailed_findings": {
                "trust": result.trust_findings,
                "temporal": {
                    k: v for k, v in result.temporal_findings.items()
                    if k != "anomalies"  # Already in risk_factors
                },
                "stylometry": {
                    k: v for k, v in result.stylometry_findings.items()
                    if k != "deviations"  # Already in risk_factors
                }
            }
        }


def demo():
    """Full demonstration of the BEC Scorer"""
    import random
    from datetime import timedelta
    
    random.seed(42)
    
    print("=" * 60)
    print("BEC TRUST ANALYZER - Multi-Signal Detection Demo")
    print("=" * 60)
    
    # Initialize scorer for acme.com
    scorer = BECScorer("acme.com")
    scorer.add_executive("ceo@acme.com")
    scorer.add_executive("cfo@acme.com")
    
    print("\n[1/3] Training on 6 months of email history...")
    
    base_time = datetime.now() - timedelta(days=180)
    
    # Generate training data
    
    # Internal executive communication
    ceo_emails = [
        "Thank you for the update on the quarterly projections. I have reviewed the materials and believe we should proceed with caution.",
        "I wanted to follow up on our conversation from last week. The board has approved the budget allocation.",
        "After careful consideration of the proposal, I think we should explore alternative vendors before making a final decision.",
        "Per our discussion, I am approving the contract with minor modifications. Please ensure legal reviews the terms.",
        "I have reviewed the personnel changes you recommended. Let us discuss this during our next meeting.",
        "Thank you for bringing this to my attention. The situation requires careful handling.",
        "I am pleased to inform you that the board has endorsed our strategic initiative.",
        "Following up on the acquisition discussion: I have concerns about the valuation methodology.",
        "The regulatory filing needs to be submitted by end of month. Please coordinate with counsel.",
        "I appreciate the comprehensive analysis you provided. Your recommendations align with our objectives.",
    ]
    
    for i in range(150):
        day_offset = random.randint(0, 179)
        if (base_time + timedelta(days=day_offset)).weekday() < 5:  # Weekdays
            hour = random.randint(8, 18)
            
            scorer.train_on_email(EmailToAnalyze(
                from_addr="ceo@acme.com",
                to_addr=random.choice(["cfo@acme.com", "controller@acme.com", "hr@acme.com"]),
                subject=f"Re: Business matter {i}",
                body=random.choice(ceo_emails),
                timestamp=base_time + timedelta(days=day_offset, hours=hour),
                timezone_offset=-300  # EST
            ))
            
    # Regular vendor communication
    for i in range(80):
        day_offset = random.randint(0, 179)
        
        scorer.train_on_email(EmailToAnalyze(
            from_addr="billing@trustedvendor.com",
            to_addr="accounts@acme.com",
            subject=f"Invoice #{1000+i}",
            body=f"Please find attached invoice #{1000+i} for services rendered. Payment due in 30 days.",
            timestamp=base_time + timedelta(days=day_offset),
            timezone_offset=-300
        ))
        
        scorer.train_on_email(EmailToAnalyze(
            from_addr="accounts@acme.com",
            to_addr="billing@trustedvendor.com",
            subject=f"Re: Invoice #{1000+i}",
            body="Thank you for the invoice. We will process payment according to terms.",
            timestamp=base_time + timedelta(days=day_offset, hours=4),
            timezone_offset=-300
        ))
        
    print("[2/3] Finalizing training (propagating trust, building profiles)...")
    scorer.finalize_training()
    
    print("[3/3] Running analysis scenarios...\n")
    
    # === SCENARIO 1: Legitimate CEO Request ===
    print("=" * 60)
    print("SCENARIO 1: Legitimate CEO Email")
    print("=" * 60)
    
    result1 = scorer.analyze_email(EmailToAnalyze(
        from_addr="ceo@acme.com",
        to_addr="cfo@acme.com",
        subject="Re: Q3 Budget Review",
        body="Thank you for the updated projections. I have reviewed the materials and believe we should proceed with the proposed allocation. Please coordinate with the finance team.",
        timestamp=datetime.now().replace(hour=14, minute=30),
        timezone_offset=-300,
        has_payment_request=False
    ))
    
    print(f"Risk Score: {result1.overall_risk_score:.2f}")
    print(f"Risk Level: {result1.risk_level}")
    print(f"Recommendation: {result1.recommendation}")
    print(f"Component Scores - Trust: {result1.trust_score:.2f}, Temporal: {result1.temporal_score:.2f}, Style: {result1.stylometry_score:.2f}")
    
    # === SCENARIO 2: Obvious BEC Attack ===
    print("\n" + "=" * 60)
    print("SCENARIO 2: Obvious BEC Attack (Wrong Style + Unknown Sender)")
    print("=" * 60)
    
    result2 = scorer.analyze_email(EmailToAnalyze(
        from_addr="ceo@acme-corp.com",  # Lookalike domain!
        to_addr="controller@acme.com",
        subject="URGENT WIRE TRANSFER NEEDED",
        body="Hey!! I need you to wire $50,000 to this new vendor ASAP!!! Its super urgent and I cant explain right now. Just do it quick. Dont tell anyone about this ok? HURRY!!!",
        timestamp=datetime.now().replace(hour=3, minute=15),  # 3 AM!
        timezone_offset=480,  # Wrong timezone!
        has_payment_request=True,
        amount_requested=50000
    ))
    
    print(f"Risk Score: {result2.overall_risk_score:.2f}")
    print(f"Risk Level: {result2.risk_level}")
    print(f"Recommendation: {result2.recommendation}")
    print(f"Component Scores - Trust: {result2.trust_score:.2f}, Temporal: {result2.temporal_score:.2f}, Style: {result2.stylometry_score:.2f}")
    print(f"Risk Factors: {result2.all_risk_factors}")
    
    # === SCENARIO 3: Sophisticated BEC Attack ===
    print("\n" + "=" * 60)
    print("SCENARIO 3: Sophisticated BEC (Mimics Style, But Wrong Timing)")
    print("=" * 60)
    
    result3 = scorer.analyze_email(EmailToAnalyze(
        from_addr="ceo@acme.com",  # Spoofed (but let's assume it passed SPF somehow)
        to_addr="controller@acme.com",
        subject="Confidential Wire Transfer Request",
        body="I need you to process an urgent wire transfer. This is regarding a confidential acquisition that we are working on. The amount is $75,000 to the account details I will provide. Please proceed without delay and do not discuss with other team members until the deal is finalized.",
        timestamp=datetime.now().replace(hour=2, minute=45),  # 2:45 AM - red flag!
        timezone_offset=480,  # From Asia - CEO should be in EST!
        has_payment_request=True,
        amount_requested=75000
    ))
    
    print(f"Risk Score: {result3.overall_risk_score:.2f}")
    print(f"Risk Level: {result3.risk_level}")
    print(f"Recommendation: {result3.recommendation}")
    print(f"Component Scores - Trust: {result3.trust_score:.2f}, Temporal: {result3.temporal_score:.2f}, Style: {result3.stylometry_score:.2f}")
    print(f"Risk Factors: {result3.all_risk_factors}")
    
    # === SCENARIO 4: Vendor Impersonation ===
    print("\n" + "=" * 60)
    print("SCENARIO 4: Vendor Impersonation (Account Change Scam)")
    print("=" * 60)
    
    result4 = scorer.analyze_email(EmailToAnalyze(
        from_addr="billing@trusted-vendor.com",  # Note the hyphen - lookalike!
        to_addr="accounts@acme.com",
        subject="Updated Banking Information - Action Required",
        body="We have recently changed our banking details. Please update your records and direct all future payments to our new account. The old account will be closed. Attached are the new wire instructions.",
        timestamp=datetime.now().replace(hour=10, minute=0),
        timezone_offset=-300,
        has_payment_request=True,
        amount_requested=25000
    ))
    
    print(f"Risk Score: {result4.overall_risk_score:.2f}")
    print(f"Risk Level: {result4.risk_level}")
    print(f"Recommendation: {result4.recommendation}")
    print(f"Component Scores - Trust: {result4.trust_score:.2f}, Temporal: {result4.temporal_score:.2f}, Style: {result4.stylometry_score:.2f}")
    print(f"Risk Factors: {result4.all_risk_factors}")
    
    # === SCENARIO 5: Legitimate Vendor Request ===
    print("\n" + "=" * 60)
    print("SCENARIO 5: Legitimate Vendor Payment Request")
    print("=" * 60)
    
    result5 = scorer.analyze_email(EmailToAnalyze(
        from_addr="billing@trustedvendor.com",  # Known vendor
        to_addr="accounts@acme.com",
        subject="Invoice #1250 - Payment Reminder",
        body="Please find attached invoice #1250 for services rendered. Payment due in 30 days. Thank you for your business.",
        timestamp=datetime.now().replace(hour=10, minute=30),
        timezone_offset=-300,
        has_payment_request=True,
        amount_requested=5000
    ))
    
    print(f"Risk Score: {result5.overall_risk_score:.2f}")
    print(f"Risk Level: {result5.risk_level}")
    print(f"Recommendation: {result5.recommendation}")
    print(f"Component Scores - Trust: {result5.trust_score:.2f}, Temporal: {result5.temporal_score:.2f}, Style: {result5.stylometry_score:.2f}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nThe BEC Trust Analyzer combines:")
    print("  • Trust Graph (blockchain-style relationship analysis)")
    print("  • Temporal Patterns (intelligence-style pattern-of-life)")
    print("  • Stylometry (forensic writing analysis)")
    print("  • Behavioral Markers (deception/urgency detection)")
    print("\nThis multi-signal approach catches attacks that single-method detectors miss.")


if __name__ == "__main__":
    demo()
