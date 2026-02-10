"""
Temporal Pattern-of-Life Analyzer

Inspired by: Intelligence community pattern-of-life analysis + SEC ARTEMIS temporal trading detection

Key insight: Every person has a "circadian signature" - when they email, how quickly they respond,
their weekly rhythms. Attackers can't easily fake this.
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math
import statistics


@dataclass
class EmailEvent:
    """An email event with timing metadata"""
    sender: str
    recipient: str
    timestamp: datetime
    timezone_offset: int = 0  # Minutes from UTC (from headers)
    claimed_timezone: str = ""  # If specified in email
    response_to: Optional[str] = None  # Message-ID of parent
    message_id: str = ""


@dataclass
class TemporalProfile:
    """Pattern-of-life profile for an email address"""
    address: str
    
    # Hour-of-day distribution (0-23 -> count)
    hourly_distribution: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    
    # Day-of-week distribution (0=Mon, 6=Sun -> count)
    daily_distribution: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    
    # Response times (in minutes) for threads
    response_times: List[float] = field(default_factory=list)
    
    # Typical timezone offset observed
    observed_timezones: List[int] = field(default_factory=list)
    
    # Total emails for normalization
    total_emails: int = 0
    
    # Statistics
    avg_response_time: float = 0.0
    std_response_time: float = 0.0
    primary_timezone: int = 0
    active_hours: List[int] = field(default_factory=list)  # Hours with >5% activity


class TemporalAnalyzer:
    """
    Analyzes temporal patterns to detect anomalies.
    
    Like a casino's player tracking system, we build behavioral profiles
    and detect when someone deviates from their established patterns.
    """
    
    def __init__(self):
        self.profiles: Dict[str, TemporalProfile] = {}
        self.email_threads: Dict[str, List[EmailEvent]] = defaultdict(list)
        
    def get_or_create_profile(self, email: str) -> TemporalProfile:
        """Get existing profile or create new one"""
        email = email.lower()
        if email not in self.profiles:
            self.profiles[email] = TemporalProfile(address=email)
        return self.profiles[email]
        
    def add_email(self, event: EmailEvent):
        """Add an email event to the analyzer"""
        profile = self.get_or_create_profile(event.sender)
        
        # Update hourly distribution
        hour = event.timestamp.hour
        profile.hourly_distribution[hour] += 1
        
        # Update daily distribution
        day = event.timestamp.weekday()
        profile.daily_distribution[day] += 1
        
        # Track timezone
        profile.observed_timezones.append(event.timezone_offset)
        
        # Track for response time analysis
        if event.response_to:
            self.email_threads[event.response_to].append(event)
            
        profile.total_emails += 1
        
    def calculate_response_times(self):
        """Calculate response times from thread data"""
        for thread_id, events in self.email_threads.items():
            if len(events) < 2:
                continue
                
            events.sort(key=lambda e: e.timestamp)
            
            for i in range(1, len(events)):
                responder = events[i].sender
                response_time = (events[i].timestamp - events[i-1].timestamp).total_seconds() / 60
                
                if response_time > 0 and response_time < 10080:  # Less than a week
                    profile = self.get_or_create_profile(responder)
                    profile.response_times.append(response_time)
                    
    def finalize_profiles(self):
        """Calculate statistics for all profiles"""
        self.calculate_response_times()
        
        for profile in self.profiles.values():
            # Response time statistics
            if profile.response_times:
                profile.avg_response_time = statistics.mean(profile.response_times)
                if len(profile.response_times) > 1:
                    profile.std_response_time = statistics.stdev(profile.response_times)
                    
            # Primary timezone
            if profile.observed_timezones:
                profile.primary_timezone = statistics.mode(profile.observed_timezones)
                
            # Active hours (hours with >5% of total activity)
            if profile.total_emails > 0:
                threshold = profile.total_emails * 0.05
                profile.active_hours = [
                    hour for hour, count in profile.hourly_distribution.items()
                    if count >= threshold
                ]
                
    def get_hourly_probability(self, profile: TemporalProfile, hour: int) -> float:
        """Get probability of sending email at this hour based on history"""
        if profile.total_emails == 0:
            return 1.0 / 24  # Uniform if no data
            
        count = profile.hourly_distribution.get(hour, 0)
        return count / profile.total_emails
        
    def get_daily_probability(self, profile: TemporalProfile, day: int) -> float:
        """Get probability of sending email on this day based on history"""
        if profile.total_emails == 0:
            return 1.0 / 7
            
        count = profile.daily_distribution.get(day, 0)
        return count / profile.total_emails
        
    def analyze_email(self, event: EmailEvent) -> Dict:
        """
        Analyze an email for temporal anomalies.
        
        Returns anomaly scores and risk factors.
        """
        profile = self.profiles.get(event.sender.lower())
        
        anomalies = []
        anomaly_score = 0.0
        
        # Check 1: Do we have enough history?
        if profile is None or profile.total_emails < 20:
            anomalies.append("INSUFFICIENT_HISTORY: Cannot establish baseline pattern")
            # Can't assess - not necessarily risky, just unknown
            return {
                "sender": event.sender,
                "timestamp": event.timestamp.isoformat(),
                "anomaly_score": 0.5,  # Neutral
                "anomalies": anomalies,
                "has_baseline": False,
                "hour_probability": None,
                "day_probability": None
            }
            
        hour = event.timestamp.hour
        day = event.timestamp.weekday()
        
        # Check 2: Unusual hour
        hour_prob = self.get_hourly_probability(profile, hour)
        if hour_prob < 0.02:  # Less than 2% of their emails at this hour
            anomalies.append(f"UNUSUAL_HOUR: Only {hour_prob*100:.1f}% of emails sent at {hour}:00")
            anomaly_score += 0.3
            
            # Especially suspicious if it's in their "dead zone"
            if hour not in profile.active_hours:
                anomalies.append(f"DEAD_ZONE: {hour}:00 is outside active hours {profile.active_hours}")
                anomaly_score += 0.2
                
        # Check 3: Unusual day
        day_prob = self.get_daily_probability(profile, day)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if day_prob < 0.05:  # Less than 5% on this day
            anomalies.append(f"UNUSUAL_DAY: Only {day_prob*100:.1f}% of emails on {day_names[day]}")
            anomaly_score += 0.15
            
        # Check 4: Timezone mismatch
        if event.timezone_offset != 0 and profile.primary_timezone != 0:
            tz_diff = abs(event.timezone_offset - profile.primary_timezone)
            if tz_diff > 60:  # More than 1 hour difference
                anomalies.append(
                    f"TIMEZONE_MISMATCH: Email from UTC{event.timezone_offset/60:+.0f}, "
                    f"usual is UTC{profile.primary_timezone/60:+.0f}"
                )
                anomaly_score += 0.25
                
                # Major timezone jump is very suspicious
                if tz_diff > 300:  # 5+ hours
                    anomalies.append("MAJOR_TZ_SHIFT: Timezone shifted by 5+ hours from normal")
                    anomaly_score += 0.2
                    
        # Check 5: 3 AM test - CEO emails at 3 AM local time are suspicious
        local_hour = (hour + (profile.primary_timezone // 60)) % 24
        if local_hour >= 1 and local_hour <= 5:  # 1 AM to 5 AM local
            if hour_prob < 0.05:
                anomalies.append(f"LATE_NIGHT: Email at {local_hour}:00 local time is unusual")
                anomaly_score += 0.2
                
        return {
            "sender": event.sender,
            "timestamp": event.timestamp.isoformat(),
            "anomaly_score": min(1.0, anomaly_score),
            "anomalies": anomalies,
            "has_baseline": True,
            "hour_probability": hour_prob,
            "day_probability": day_prob,
            "primary_timezone": profile.primary_timezone,
            "active_hours": profile.active_hours,
            "total_baseline_emails": profile.total_emails,
            "risk_level": self._risk_level(anomaly_score)
        }
        
    def _risk_level(self, score: float) -> str:
        if score >= 0.6:
            return "HIGH"
        elif score >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
            
    def get_profile_summary(self, email: str) -> Optional[Dict]:
        """Get a summary of someone's temporal profile"""
        profile = self.profiles.get(email.lower())
        if not profile:
            return None
            
        # Find peak hours
        if profile.hourly_distribution:
            sorted_hours = sorted(
                profile.hourly_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )
            peak_hours = [h for h, _ in sorted_hours[:3]]
        else:
            peak_hours = []
            
        # Find peak days
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if profile.daily_distribution:
            sorted_days = sorted(
                profile.daily_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )
            peak_days = [day_names[d] for d, _ in sorted_days[:3]]
        else:
            peak_days = []
            
        return {
            "address": email,
            "total_emails": profile.total_emails,
            "peak_hours": peak_hours,
            "peak_days": peak_days,
            "active_hours": profile.active_hours,
            "primary_timezone_offset": profile.primary_timezone,
            "avg_response_time_minutes": profile.avg_response_time,
            "std_response_time_minutes": profile.std_response_time
        }


def demo():
    """Demonstrate temporal analysis with sample data"""
    analyzer = TemporalAnalyzer()
    
    # Simulate 6 months of email history for the CEO
    # CEO works EST (UTC-5), typically 8 AM - 6 PM, Mon-Fri
    base_time = datetime.now() - timedelta(days=180)
    
    import random
    random.seed(42)  # Reproducible
    
    print("=== Temporal Pattern-of-Life Analyzer Demo ===\n")
    print("Building baseline from 6 months of email history...")
    
    # Generate realistic email patterns for CEO
    for day_offset in range(180):
        date = base_time + timedelta(days=day_offset)
        
        # Skip weekends mostly (5% chance of working)
        if date.weekday() >= 5 and random.random() > 0.05:
            continue
            
        # Send 5-15 emails per work day
        num_emails = random.randint(5, 15)
        
        for _ in range(num_emails):
            # Working hours: mostly 8 AM - 6 PM EST
            if random.random() < 0.9:  # 90% in work hours
                hour = random.randint(8, 18)
            else:  # 10% early/late
                hour = random.choice([7, 19, 20])
                
            email_time = date.replace(hour=hour, minute=random.randint(0, 59))
            
            analyzer.add_email(EmailEvent(
                sender="ceo@acme.com",
                recipient="someone@example.com",
                timestamp=email_time,
                timezone_offset=-300,  # UTC-5 (EST)
                message_id=f"msg-{day_offset}-{_}"
            ))
            
    analyzer.finalize_profiles()
    
    # Show CEO's temporal profile
    profile = analyzer.get_profile_summary("ceo@acme.com")
    print(f"\nCEO Temporal Profile:")
    print(f"  Total emails: {profile['total_emails']}")
    print(f"  Peak hours: {profile['peak_hours']}")
    print(f"  Peak days: {profile['peak_days']}")
    print(f"  Active hours: {profile['active_hours']}")
    print(f"  Primary timezone: UTC{profile['primary_timezone_offset']/60:+.0f}")
    
    print("\n" + "="*50)
    print("\n--- Scenario 1: Legitimate Email (Tuesday 10 AM EST) ---")
    result1 = analyzer.analyze_email(EmailEvent(
        sender="ceo@acme.com",
        recipient="cfo@acme.com",
        timestamp=datetime.now().replace(hour=10, minute=30),
        timezone_offset=-300  # EST
    ))
    print(f"Anomaly Score: {result1['anomaly_score']:.2f}")
    print(f"Risk Level: {result1['risk_level']}")
    print(f"Hour Probability: {result1['hour_probability']:.1%}")
    
    print("\n--- Scenario 2: SUSPICIOUS - Email at 3 AM EST ---")
    result2 = analyzer.analyze_email(EmailEvent(
        sender="ceo@acme.com",
        recipient="cfo@acme.com",
        timestamp=datetime.now().replace(hour=3, minute=15),
        timezone_offset=-300
    ))
    print(f"Anomaly Score: {result2['anomaly_score']:.2f}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Anomalies: {result2['anomalies']}")
    
    print("\n--- Scenario 3: SUSPICIOUS - Email from wrong timezone ---")
    result3 = analyzer.analyze_email(EmailEvent(
        sender="ceo@acme.com",
        recipient="cfo@acme.com",
        timestamp=datetime.now().replace(hour=14, minute=0),
        timezone_offset=480  # UTC+8 (Singapore) - CEO is supposedly in EST!
    ))
    print(f"Anomaly Score: {result3['anomaly_score']:.2f}")
    print(f"Risk Level: {result3['risk_level']}")
    print(f"Anomalies: {result3['anomalies']}")
    
    print("\n--- Scenario 4: VERY SUSPICIOUS - Sunday 2 AM from Asia ---")
    sunday = datetime.now()
    while sunday.weekday() != 6:  # Find next Sunday
        sunday += timedelta(days=1)
    sunday = sunday.replace(hour=2, minute=30)
    
    result4 = analyzer.analyze_email(EmailEvent(
        sender="ceo@acme.com",
        recipient="cfo@acme.com",
        timestamp=sunday,
        timezone_offset=480  # Asia timezone
    ))
    print(f"Anomaly Score: {result4['anomaly_score']:.2f}")
    print(f"Risk Level: {result4['risk_level']}")
    print(f"Anomalies: {result4['anomalies']}")


if __name__ == "__main__":
    demo()
