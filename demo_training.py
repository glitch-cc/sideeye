"""
Demo training data for the BEC scorer
"""

from datetime import datetime, timedelta
from bec_scorer import EmailToAnalyze


def load_demo_training(scorer):
    """Load realistic demo training data"""
    
    # Add known trusted senders (legitimate contacts)
    trusted_senders = [
        ("cfo@cyrenity.com", "CFO email pattern"),
        ("accounting@cyrenity.com", "Accounting team"),
        ("vendor1@trustedvendor.com", "Legitimate vendor"),
        ("partner@lawfirm.com", "Legal partner"),
    ]
    
    now = datetime.utcnow()
    
    # Generate training emails from trusted senders
    # This builds the baseline for trust graph and stylometry
    
    training_emails = [
        # CFO emails (establishes pattern)
        EmailToAnalyze(
            from_addr="cfo@cyrenity.com",
            to_addr="bbrown@cyrenity.com",
            subject="Q4 Budget Review",
            body="""Hi Brian,

I've reviewed the Q4 budget projections and everything looks on track. 
The marketing spend is slightly higher than expected, but we're seeing 
good ROI on the new campaigns.

Let's sync tomorrow to discuss the capital allocation for next quarter.

Best,
Sarah
CFO, Cyrenity""",
            timestamp=now - timedelta(days=30),
            timezone_offset=-360  # CST
        ),
        EmailToAnalyze(
            from_addr="cfo@cyrenity.com",
            to_addr="bbrown@cyrenity.com",
            subject="Re: Vendor Payment Approval",
            body="""Brian,

I've approved the vendor payment request. Please proceed through the 
normal channels - finance team will handle the wire transfer via our 
standard process.

Thanks,
Sarah""",
            timestamp=now - timedelta(days=15),
            timezone_offset=-360
        ),
        EmailToAnalyze(
            from_addr="cfo@cyrenity.com",
            to_addr="bbrown@cyrenity.com", 
            subject="Monthly financials attached",
            body="""Hi Brian,

Attached are the monthly financials for your review. Key highlights:
- Revenue up 12% MoM
- EBITDA margin improved to 23%
- Cash position remains strong

Let me know if you have any questions.

Best,
Sarah
Chief Financial Officer""",
            timestamp=now - timedelta(days=7),
            timezone_offset=-360
        ),
        
        # Vendor emails (establishes trust relationship)
        EmailToAnalyze(
            from_addr="vendor1@trustedvendor.com",
            to_addr="bbrown@cyrenity.com",
            subject="Invoice #2024-1234",
            body="""Dear Mr. Brown,

Please find attached invoice #2024-1234 for services rendered in January.
Payment terms are net-30 as per our agreement.

Our banking details remain unchanged from our master services agreement.

Best regards,
John Smith
Accounts Receivable
Trusted Vendor Inc.""",
            timestamp=now - timedelta(days=20),
            timezone_offset=-300  # EST
        ),
        
        # Partner emails
        EmailToAnalyze(
            from_addr="partner@lawfirm.com",
            to_addr="bbrown@cyrenity.com",
            subject="Contract review complete",
            body="""Brian,

Our team has completed the review of the proposed acquisition agreement.
Overall, the terms are favorable. I've marked up a few sections that 
need attention - see my comments in the attached redline.

Please call me at your convenience to discuss.

Regards,
Michael Patterson
Partner, Smith & Associates LLP""",
            timestamp=now - timedelta(days=10),
            timezone_offset=-300
        ),
        
        # Accounting team
        EmailToAnalyze(
            from_addr="accounting@cyrenity.com",
            to_addr="bbrown@cyrenity.com",
            subject="Expense report approval needed",
            body="""Hi Brian,

You have 3 expense reports pending approval in Concur:
- Marketing team Q1 travel: $4,500
- Engineering conference: $2,100  
- Client dinner: $350

Please approve when you get a chance.

Thanks,
Accounting Team""",
            timestamp=now - timedelta(days=5),
            timezone_offset=-360
        ),
    ]
    
    # Train the scorer on these emails
    for email in training_emails:
        scorer.train_on_email(email)
    
    # Mark as trained
    scorer.is_trained = True
    
    print(f"Loaded {len(training_emails)} demo training emails")
    print(f"Trust graph: {len(scorer.trust_graph.nodes)} nodes, {len(scorer.trust_graph.edges)} edges")
