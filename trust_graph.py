"""
Trust Graph Engine - Blockchain-style trust propagation for email relationships

Inspired by: Chainalysis wallet clustering + PageRank trust propagation
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class EmailInteraction:
    """A single email interaction (like a blockchain transaction)"""
    from_addr: str
    to_addr: str
    timestamp: datetime
    subject: str
    has_payment_request: bool = False
    amount_requested: float = 0.0
    
    
@dataclass 
class NodeProfile:
    """Profile for an email address node in the graph"""
    address: str
    first_seen: datetime = None
    last_seen: datetime = None
    interaction_count: int = 0
    incoming_count: int = 0
    outgoing_count: int = 0
    trust_score: float = 0.5  # Start neutral
    is_internal: bool = False  # Part of organization
    is_executive: bool = False
    payment_requests_made: int = 0
    payment_requests_fulfilled: int = 0


class TrustGraph:
    """
    Email communication graph with trust propagation.
    
    Think of it like a blockchain analyst's wallet graph:
    - Each email address is a "wallet"
    - Each email is a "transaction"
    - Trust propagates through the network
    - Anomalies are detected by graph position and trust scores
    """
    
    def __init__(self, organization_domain: str):
        self.org_domain = organization_domain
        self.nodes: Dict[str, NodeProfile] = {}
        self.edges: Dict[Tuple[str, str], List[EmailInteraction]] = defaultdict(list)
        self.executives: List[str] = []
        
    def is_internal(self, email: str) -> bool:
        """Check if email belongs to the organization"""
        return email.lower().endswith(f"@{self.org_domain}")
        
    def add_executive(self, email: str):
        """Mark an email as an executive (high-value target)"""
        self.executives.append(email.lower())
        if email.lower() in self.nodes:
            self.nodes[email.lower()].is_executive = True
            
    def get_or_create_node(self, email: str) -> NodeProfile:
        """Get existing node or create new one"""
        email = email.lower()
        if email not in self.nodes:
            self.nodes[email] = NodeProfile(
                address=email,
                is_internal=self.is_internal(email),
                is_executive=email in self.executives
            )
        return self.nodes[email]
        
    def add_interaction(self, interaction: EmailInteraction):
        """Add an email interaction to the graph"""
        from_addr = interaction.from_addr.lower()
        to_addr = interaction.to_addr.lower()
        
        # Update nodes
        from_node = self.get_or_create_node(from_addr)
        to_node = self.get_or_create_node(to_addr)
        
        if from_node.first_seen is None:
            from_node.first_seen = interaction.timestamp
        from_node.last_seen = interaction.timestamp
        from_node.interaction_count += 1
        from_node.outgoing_count += 1
        
        if to_node.first_seen is None:
            to_node.first_seen = interaction.timestamp
        to_node.last_seen = interaction.timestamp
        to_node.incoming_count += 1
        
        if interaction.has_payment_request:
            from_node.payment_requests_made += 1
            
        # Add edge
        edge_key = (from_addr, to_addr)
        self.edges[edge_key].append(interaction)
        
    def calculate_relationship_strength(self, from_addr: str, to_addr: str) -> float:
        """
        Calculate relationship strength between two addresses.
        
        Factors:
        - Number of interactions
        - Duration of relationship
        - Reciprocity (two-way communication)
        - Recency
        """
        from_addr = from_addr.lower()
        to_addr = to_addr.lower()
        
        # Get interactions in both directions
        outgoing = self.edges.get((from_addr, to_addr), [])
        incoming = self.edges.get((to_addr, from_addr), [])
        
        if not outgoing and not incoming:
            return 0.0
            
        total_interactions = len(outgoing) + len(incoming)
        
        # Reciprocity bonus
        reciprocity = min(len(outgoing), len(incoming)) / max(len(outgoing), len(incoming), 1)
        
        # Duration factor (longer relationships = stronger)
        all_interactions = outgoing + incoming
        if all_interactions:
            first = min(i.timestamp for i in all_interactions)
            last = max(i.timestamp for i in all_interactions)
            duration_days = max(1, (last - first).days)
        else:
            duration_days = 0
            
        # Recency factor (decay for old relationships)
        if all_interactions:
            days_since_last = (datetime.now() - last).days
            recency_factor = math.exp(-days_since_last / 90)  # 90-day half-life
        else:
            recency_factor = 0
            
        # Combine factors
        strength = (
            math.log1p(total_interactions) * 0.3 +  # Interaction volume
            reciprocity * 0.3 +                       # Two-way communication
            min(duration_days / 365, 1) * 0.2 +      # Relationship age
            recency_factor * 0.2                      # Recent activity
        )
        
        return min(1.0, strength)
        
    def propagate_trust(self, iterations: int = 10, damping: float = 0.85):
        """
        PageRank-style trust propagation.
        
        Internal nodes start with high trust, which flows to external contacts
        based on relationship strength.
        """
        # Initialize trust scores
        for node in self.nodes.values():
            if node.is_internal:
                node.trust_score = 1.0
            elif node.is_executive:
                node.trust_score = 1.0
            else:
                node.trust_score = 0.1  # Unknown externals start low
                
        # Propagate trust
        for _ in range(iterations):
            new_scores = {}
            
            for addr, node in self.nodes.items():
                if node.is_internal:
                    new_scores[addr] = 1.0  # Internal always trusted
                    continue
                    
                # Sum incoming trust from edges
                incoming_trust = 0.0
                incoming_count = 0
                
                for (from_addr, to_addr), interactions in self.edges.items():
                    if to_addr == addr:
                        from_node = self.nodes.get(from_addr)
                        if from_node:
                            strength = self.calculate_relationship_strength(from_addr, addr)
                            incoming_trust += from_node.trust_score * strength
                            incoming_count += 1
                            
                if incoming_count > 0:
                    new_scores[addr] = (
                        (1 - damping) * 0.1 +  # Base score
                        damping * (incoming_trust / incoming_count)
                    )
                else:
                    new_scores[addr] = 0.1
                    
            # Update scores
            for addr, score in new_scores.items():
                self.nodes[addr].trust_score = score
                
    def get_trust_score(self, email: str) -> float:
        """Get trust score for an email address"""
        node = self.nodes.get(email.lower())
        return node.trust_score if node else 0.0
        
    def analyze_payment_request(self, from_addr: str, to_addr: str, 
                                 amount: float) -> Dict:
        """
        Analyze a payment request for BEC indicators.
        
        Returns risk assessment based on graph analysis.
        """
        from_addr = from_addr.lower()
        to_addr = to_addr.lower()
        
        from_node = self.nodes.get(from_addr)
        relationship_strength = self.calculate_relationship_strength(from_addr, to_addr)
        
        risk_factors = []
        risk_score = 0.0
        
        # Factor 1: Is this a known sender?
        if from_node is None:
            risk_factors.append("UNKNOWN_SENDER: First-time sender")
            risk_score += 0.4
        elif from_node.interaction_count < 5:
            risk_factors.append("LOW_HISTORY: Sender has few prior interactions")
            risk_score += 0.2
            
        # Factor 2: Trust score
        trust = self.get_trust_score(from_addr)
        if trust < 0.3:
            risk_factors.append(f"LOW_TRUST: Sender trust score {trust:.2f}")
            risk_score += 0.3
        elif trust < 0.5:
            risk_factors.append(f"MEDIUM_TRUST: Sender trust score {trust:.2f}")
            risk_score += 0.1
            
        # Factor 3: Relationship strength
        if relationship_strength < 0.2:
            risk_factors.append("WEAK_RELATIONSHIP: Limited prior communication")
            risk_score += 0.25
            
        # Factor 4: Does sender have history of payment requests?
        if from_node and from_node.payment_requests_made == 0:
            risk_factors.append("FIRST_PAYMENT_REQUEST: No prior payment requests from this sender")
            risk_score += 0.15
            
        # Factor 5: Internal impersonation check
        if from_node and from_node.is_internal:
            # This looks like it's from internal, but is it really?
            # (Would need email auth check here - placeholder)
            pass
            
        # Factor 6: High-value transaction from low-trust source
        if amount > 10000 and trust < 0.5:
            risk_factors.append("HIGH_VALUE_LOW_TRUST: Large amount from low-trust sender")
            risk_score += 0.2
            
        return {
            "from_address": from_addr,
            "to_address": to_addr,
            "amount": amount,
            "trust_score": trust,
            "relationship_strength": relationship_strength,
            "risk_score": min(1.0, risk_score),
            "risk_level": self._risk_level(risk_score),
            "risk_factors": risk_factors,
            "recommendation": self._recommendation(risk_score)
        }
        
    def _risk_level(self, score: float) -> str:
        if score >= 0.7:
            return "CRITICAL"
        elif score >= 0.5:
            return "HIGH"
        elif score >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
            
    def _recommendation(self, score: float) -> str:
        if score >= 0.7:
            return "BLOCK: Manual verification required before proceeding"
        elif score >= 0.5:
            return "VERIFY: Confirm request through separate channel (phone call)"
        elif score >= 0.3:
            return "REVIEW: Examine request carefully before approval"
        else:
            return "PROCEED: Normal risk level"
            
    def export_graph(self) -> Dict:
        """Export graph for visualization/analysis"""
        return {
            "nodes": [
                {
                    "address": n.address,
                    "trust_score": n.trust_score,
                    "is_internal": n.is_internal,
                    "is_executive": n.is_executive,
                    "interaction_count": n.interaction_count,
                    "first_seen": n.first_seen.isoformat() if n.first_seen else None,
                    "last_seen": n.last_seen.isoformat() if n.last_seen else None
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "from": from_addr,
                    "to": to_addr,
                    "weight": len(interactions),
                    "strength": self.calculate_relationship_strength(from_addr, to_addr)
                }
                for (from_addr, to_addr), interactions in self.edges.items()
            ]
        }


def demo():
    """Demonstrate the trust graph with sample data"""
    # Create graph for acme.com
    graph = TrustGraph("acme.com")
    
    # Add executives
    graph.add_executive("ceo@acme.com")
    graph.add_executive("cfo@acme.com")
    
    # Simulate historical email traffic
    base_time = datetime.now() - timedelta(days=180)
    
    # Lots of internal communication
    for i in range(100):
        graph.add_interaction(EmailInteraction(
            from_addr="ceo@acme.com",
            to_addr="cfo@acme.com",
            timestamp=base_time + timedelta(days=i),
            subject=f"Re: Business stuff {i}"
        ))
        
    # Regular vendor communication
    for i in range(50):
        graph.add_interaction(EmailInteraction(
            from_addr="billing@trustedvendor.com",
            to_addr="accounts@acme.com",
            timestamp=base_time + timedelta(days=i*3),
            subject=f"Invoice #{i+1000}"
        ))
        graph.add_interaction(EmailInteraction(
            from_addr="accounts@acme.com",
            to_addr="billing@trustedvendor.com",
            timestamp=base_time + timedelta(days=i*3+1),
            subject=f"Re: Invoice #{i+1000}"
        ))
        
    # Propagate trust through the network
    graph.propagate_trust()
    
    print("=== Trust Graph Demo ===\n")
    
    # Check trust scores
    print("Trust Scores:")
    for addr in ["ceo@acme.com", "cfo@acme.com", "billing@trustedvendor.com", "random@unknown.com"]:
        node = graph.nodes.get(addr)
        if node:
            print(f"  {addr}: {node.trust_score:.3f}")
        else:
            print(f"  {addr}: (unknown)")
            
    print("\n--- Scenario 1: Legitimate Vendor Payment Request ---")
    result1 = graph.analyze_payment_request(
        from_addr="billing@trustedvendor.com",
        to_addr="accounts@acme.com",
        amount=5000
    )
    print(f"Risk Level: {result1['risk_level']}")
    print(f"Risk Score: {result1['risk_score']:.2f}")
    print(f"Recommendation: {result1['recommendation']}")
    
    print("\n--- Scenario 2: BEC Attack - Unknown Sender ---")
    result2 = graph.analyze_payment_request(
        from_addr="ceo@acme-corp.com",  # Lookalike domain!
        to_addr="accounts@acme.com",
        amount=50000
    )
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Risk Score: {result2['risk_score']:.2f}")
    print(f"Risk Factors: {result2['risk_factors']}")
    print(f"Recommendation: {result2['recommendation']}")
    
    print("\n--- Scenario 3: New Vendor, Large Amount ---")
    result3 = graph.analyze_payment_request(
        from_addr="accounting@newvendor.com",
        to_addr="accounts@acme.com",
        amount=75000
    )
    print(f"Risk Level: {result3['risk_level']}")
    print(f"Risk Score: {result3['risk_score']:.2f}")
    print(f"Risk Factors: {result3['risk_factors']}")
    print(f"Recommendation: {result3['recommendation']}")


if __name__ == "__main__":
    demo()
