import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_kazhai_score(income_entries):
    """
    Calculates KazhaiScore based on income entries.
    Entries: List of dicts [{'date': datetime, 'amount': float}]
    """
    if not income_entries:
        return {
            "score": 300, 
            "risk_tier": "High Risk", 
            "loan_range": "No Data",
            "metrics": {
                "total": 0,
                "days_active": 0,
                "avg_daily": 0
            }
        }

    df = pd.DataFrame(income_entries)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Basic Metrics
    total_earned = df['amount'].sum()
    days_active = df['date'].dt.date.nunique()
    avg_income = df['amount'].mean()
    std_dev = df['amount'].std() if len(df) > 1 else avg_income * 0.5 # Assume high variance if 1 entry

    # Time Horizon check (Active days in last 30 days)
    last_30_days = datetime.now() - timedelta(days=30)
    active_last_month = df[df['date'] > last_30_days]['date'].nunique()

    # Trend Calculation (Simple Linear Fit)
    # Convert dates to ordinal numbers for regression
    if len(df) > 1:
        x = df['date'].apply(lambda d: d.toordinal())
        y = df['amount']
        slope = np.polyfit(x, y, 1)[0]
    else:
        slope = 0

    # Score Logic
    base_score = 600
    
    # Active Bonus (Max +150)
    score = base_score + (active_last_month * 5)
    
    # Stability Check
    cv = std_dev / avg_income if avg_income > 0 else 0
    if cv < 0.2: score += 100 # Very stable
    elif cv < 0.5: score += 50 # Moderately stable
    else: score -= 50 # Unstable

    # Growth Bonus
    if slope > 0: score += 50

    # Cap Score
    score = max(300, min(900, score))

    # Determine Tier
    if score >= 750:
        tier = "Low Risk (Premium)"
        loan = "₹50,000 – ₹1,00,000"
    elif score >= 600:
        tier = "Moderate Risk"
        loan = "₹10,000 – ₹25,000"
    else:
        tier = "High Risk"
        loan = "₹2,000 – ₹5,000 (Micro)"

    return {
        "score": int(score),
        "risk_tier": tier,
        "loan_range": loan,
        "metrics": {
            "total": total_earned,
            "days_active": days_active,
            "avg_daily": round(avg_income, 2)
        }
    }
