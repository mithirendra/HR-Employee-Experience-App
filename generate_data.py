"""
Vibe — Employee Experience Platform
MM Group · Synthetic Data Generator
─────────────────────────────────────
Run once from the project root:
    python generate_data.py

Outputs four CSV files into the data/ folder:
    employees.csv         — 5,000 employees across 9 departments
    pulse_responses.csv   — 1.3 million weekly pulse rows (5 years)
    activities.csv        — company activities across 5 years
    kudos.csv             — peer recognition across 5 years
"""

# ── BRICK 1 — Imports and Constants ──────────────────────────────────────────
# This section loads every library the script needs and defines all the
# reference data that the rest of the script will use. Nothing is generated
# here — this is purely the foundation.

# ── Imports ───────────────────────────────────────────────────────────────────
import os                                    # creates the data/ folder if needed
import random                                # picks random items from lists
import numpy as np                           # numerical random generation with patterns
import pandas as pd                          # builds and saves DataFrames as CSVs
from datetime import datetime, timedelta     # builds the weekly date range

# ── Reproducibility ───────────────────────────────────────────────────────────
# Seeds ensure the exact same data is generated every time you run the script.
# This is important for a demo — your numbers stay consistent.
# Remove these two lines if you want different data each run.
random.seed(42)
np.random.seed(42)

# ── Output folder ─────────────────────────────────────────────────────────────
# Builds the path to the data/ folder relative to where this script lives.
# exist_ok=True means it won't throw an error if the folder already exists.
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Company ───────────────────────────────────────────────────────────────────
COMPANY_NAME = "MM Group"

# ── Date range ────────────────────────────────────────────────────────────────
# 5 years of weekly pulse data — Jan 2020 to Dec 2024.
# Each week is represented by its Monday date.
# 260 weeks × 5,000 employees = 1.3 million pulse rows.
START_DATE = datetime(2026, 1, 5)    # first Monday of 2020
NUM_EMPLOYEES = 500    # Version 0: 500 · Version 1: 2000
NUM_WEEKS     = 52     # Version 0: 52  · Version 1: 156

# Build a list of 260 Monday dates — one label per week
WEEK_DATES = [START_DATE + timedelta(weeks=w) for w in range(NUM_WEEKS)]

# ── Department headcount weights ──────────────────────────────────────────────
# Percentages instead of fixed numbers — scales automatically with NUM_EMPLOYEES.
# Brick 2 will multiply these weights by NUM_EMPLOYEES to get actual headcounts.
DEPT_WEIGHTS = {
    "Retail":             0.24,   # 24% — largest department
    "Technology":         0.20,   # 20%
    "Sales":              0.16,   # 16%
    "Marketing":          0.14,   # 14%
    "Enterprise":         0.10,   # 10%
    "Finance":            0.06,   #  6%
    "HR":                 0.036,  #  3.6% — micro
    "Legal":              0.034,  #  3.4% — micro
    "Corporate Affairs":  0.030,  #  3.0% — micro
}
# These add up to 1.0 (100%).
# At 500 employees:  Retail=120, Technology=100, HR=18 etc.
# At 2000 employees: Retail=480, Technology=400, HR=72 etc.

# ── Job titles by department ──────────────────────────────────────────────────
# Each employee is randomly assigned one title from their department's list.
# Titles are realistic for a Malaysian conglomerate context.
TITLES = {
    "Retail": [
        "Store Manager", "Assistant Store Manager", "Retail Associate",
        "Visual Merchandiser", "Inventory Specialist", "Customer Experience Lead",
        "Cashier Supervisor", "Floor Supervisor", "Retail Executive",
    ],
    "Technology": [
        "Software Engineer", "Senior Engineer", "Tech Lead",
        "DevOps Engineer", "QA Engineer", "Data Analyst",
        "Product Manager", "UX Designer", "Cloud Architect",
        "Cybersecurity Analyst", "Mobile Developer",
    ],
    "Sales": [
        "Sales Executive", "Account Manager", "Business Development Manager",
        "Sales Lead", "Key Account Manager", "Regional Sales Manager",
        "Inside Sales Representative", "Sales Operations Analyst",
    ],
    "Marketing": [
        "Marketing Executive", "Content Strategist", "Brand Manager",
        "Digital Marketer", "Campaign Manager", "SEO Specialist",
        "Social Media Manager", "Marketing Analyst", "Creative Director",
    ],
    "Enterprise": [
        "Enterprise Account Manager", "Solutions Consultant",
        "Partnership Manager", "Enterprise Sales Director",
        "Client Success Manager", "Presales Engineer",
        "Strategic Accounts Lead",
    ],
    "Finance": [
        "Finance Analyst", "Senior Accountant", "FP&A Manager",
        "Finance Executive", "Treasury Analyst", "Tax Specialist",
        "Financial Controller", "Management Accountant",
    ],
    "HR": [
        "HR Business Partner", "Talent Acquisition Specialist",
        "L&D Manager", "Compensation Analyst",
        "People Operations Executive", "HR Director",
        "Employee Relations Manager",
    ],
    "Legal": [
        "Legal Counsel", "Compliance Officer", "Contract Specialist",
        "Regulatory Affairs Manager", "Legal Executive",
        "Company Secretary", "Intellectual Property Analyst",
    ],
    "Corporate Affairs": [
        "Corporate Communications Manager", "Government Relations Executive",
        "ESG Analyst", "Public Affairs Manager",
        "Media Relations Specialist", "Sustainability Lead",
        "Stakeholder Engagement Manager",
    ],
}

# ── Employment types ──────────────────────────────────────────────────────────
# Weighted list — mostly full-time, some part-time and contract.
# random.choice() picks from this list so full-time appears most often.
# Result: ~73% full-time, ~18% part-time, ~9% contract
EMPLOYMENT_TYPES = [
    "Full-time", "Full-time", "Full-time", "Full-time", "Full-time",
    "Full-time", "Full-time", "Full-time",   # 8 entries = 73%
    "Part-time", "Part-time",                # 2 entries = 18%
    "Contract",                              # 1 entry  =  9%
]

# ── Manager name pool ─────────────────────────────────────────────────────────
# Managers are generated programmatically — we don't hardcode all ~500 names.
# First and last names are combined randomly to create unique manager identities.
# Malaysian-flavoured names to match MM Group's market context.
FIRST_NAMES = [
    "Ahmad", "Nurul", "Rajesh", "Siti", "Wei", "Mei", "Harish", "Priya",
    "Farid", "Aisha", "Kevin", "Linda", "Mohamed", "Kavya", "Jason",
    "Sarah", "Ravi", "Nadia", "Daniel", "Fatimah", "James", "Lily",
    "Hassan", "Rina", "Christopher", "Zara", "Suresh", "Amelia", "Ivan",
    "Natasha", "Eugene", "Shirley", "Azlan", "Wendy", "Prakash", "Diana",
    "Terry", "Elaine", "Hafiz", "Grace", "Nelson", "Pamela", "Yazid",
    "Joanne", "Shankar", "Michelle", "Ridzwan", "Cheryl", "Ganesh", "Vivian",
]
LAST_NAMES = [
    "Tan", "Lim", "Wong", "Lee", "Ng", "Chan", "Chong", "Ooi",
    "Goh", "Teh", "Yap", "Chua", "Ong", "Koh", "Soh",
    "Kumar", "Raj", "Patel", "Singh", "Nair", "Menon", "Pillai",
    "Hassan", "Ali", "Rahman", "Aziz", "Ismail", "Yusof", "Hamid",
    "Abdullah", "Ibrahim", "Malik", "Rashid", "Karim", "Bakar",
]

# ── Engagement patterns by department ────────────────────────────────────────
# These patterns shape how pulse scores are generated per department.
#
# base          — score multiplier (below 1.0 = lower scores overall)
# trend         — weekly drift (negative = declining, positive = improving)
# volatility    — week-to-week fluctuation (higher = more erratic scores)
# recovery_week — week number where a recovering dept starts to improve
#                 (None means no recovery inflection point)
DEPT_PATTERNS = {
    "Retail": {
        "pattern":       "chronically_low",
        "base":           0.45,        # was 0.62 — now genuinely at risk
        "trend":         -0.0005,
        "volatility":     0.18,
        "recovery_week":  None,
    },
    "Technology": {
        "pattern":       "recovering",
        "base":           0.58,        # was 0.78 — starts struggling
        "trend":          0.003,
        "volatility":     0.10,
        "recovery_week":  130,
    },
    "Sales": {
        "pattern":       "trending_down",
        "base":           0.70,        # was 0.88 — starts okay, declines
        "trend":         -0.004,
        "volatility":     0.14,
        "recovery_week":  None,
    },
    "Marketing": {
        "pattern":       "stable_healthy",
        "base":           0.78,        # was 0.92 — healthy but not perfect
        "trend":          0.001,
        "volatility":     0.08,
        "recovery_week":  None,
    },
    "Enterprise": {
        "pattern":       "volatile",
        "base":           0.65,        # was 0.82 — mid-range with spikes
        "trend":          0.0,
        "volatility":     0.22,
        "recovery_week":  None,
    },
    "Finance": {
        "pattern":       "stable_neutral",
        "base":           0.62,        # was 0.80 — neutral, slightly concerning
        "trend":          0.0,
        "volatility":     0.07,
        "recovery_week":  None,
    },
    "HR": {
        "pattern":       "high_engagement",
        "base":           0.82,        # was 0.94 — still highest but realistic
        "trend":          0.001,
        "volatility":     0.06,
        "recovery_week":  None,
    },
    "Legal": {
        "pattern":       "stable_neutral",
        "base":           0.60,        # was 0.79 — low engagement, professional
        "trend":          0.0,
        "volatility":     0.07,
        "recovery_week":  None,
    },
    "Corporate Affairs": {
        "pattern":       "trending_up",
        "base":           0.55,        # was 0.75 — starts low, improves
        "trend":          0.003,
        "volatility":     0.09,
        "recovery_week":  None,
    },
}

# ── Manager effect ────────────────────────────────────────────────────────────
# ~8% of managers are flagged as "low-care" during employee generation.
# Their teams receive a penalty on Care and Connection scores in pulse data.
# This creates the manager effectiveness signal that HR can detect.
LOW_CARE_MANAGER_PROBABILITY = 0.08

# ── Pulse dimensions ──────────────────────────────────────────────────────────
# The five dimensions measured in every weekly pulse survey (the 5Cs).
# Scores are generated on a 1–10 scale per dimension per employee per week.
DIMENSIONS = ["Clarity", "Connection", "Contribution", "Confidence", "Care"]

# ── Open text feedback templates ─────────────────────────────────────────────
# Realistic open text responses matched to score ranges.
# Positive = composite score >= 7, Neutral = 4-7, Negative = below 4.
# Sentiment analysis (VADER) will score these in a later brick.
FEEDBACK_POSITIVE = [
    "Feeling good about the direction of the team this week.",
    "Great collaboration with colleagues on the current project.",
    "My manager has been very supportive and communicative.",
    "Clear goals and good energy across the department.",
    "Really enjoying the work and feeling valued by the team.",
    "Strong team spirit this week — everyone is pulling together.",
    "Productive week with clear priorities and good support from leadership.",
    "Positive feedback from leadership has been very motivating.",
]
FEEDBACK_NEUTRAL = [
    "Week was okay, nothing particularly good or bad to report.",
    "Some clarity on priorities but still a few open questions.",
    "Workload is manageable but could use more direction.",
    "Average week — steady progress on ongoing tasks.",
    "Things are moving along, nothing significant to flag this week.",
    "Reasonable week but looking for more growth opportunities.",
    "Tasks completed but feeling a bit disconnected from the bigger picture.",
]
FEEDBACK_NEGATIVE = [
    "Feeling overwhelmed with the current workload and unclear priorities.",
    "Communication from management has been lacking this week.",
    "Not sure what is expected of me — need more clarity on my role.",
    "Feeling disconnected from the team and the organisation's goals.",
    "Concerned about the direction and leadership of the department.",
    "High stress this week due to unrealistic deadlines and poor planning.",
    "Morale is low — people are struggling and it is starting to show.",
    "Feeling undervalued and unsupported by immediate leadership.",
]

# ── Print confirmation ────────────────────────────────────────────────────────
print("=" * 55)
print(f"  Vibe — {COMPANY_NAME} · Synthetic Data Generator")
print("=" * 55)
print(f"  ✓ Brick 1 complete — imports and constants loaded")
print(f"  Company          : {COMPANY_NAME}")
print(f"  Departments      : {len(DEPT_WEIGHTS)}")
print(f"  Target employees : {NUM_EMPLOYEES:,}")
print(f"  Week range       : {WEEK_DATES[0].date()} → {WEEK_DATES[-1].date()}")
print(f"  Total weeks      : {NUM_WEEKS}")
print(f"  Est. pulse rows  : {NUM_EMPLOYEES * NUM_WEEKS:,}")
print("=" * 55)

# ── BRICK 2 — Employee Generation ────────────────────────────────────────────
# Creates 500 (V0) or 2,000 (V1) employee records across 9 departments.
# Manager assignment uses variable span logic — each manager gets 5-15 reports
# before a new manager is created. No hardcoded manager names.

def generate_employees():
    """Generate the employee master list and return as a DataFrame."""

    employees = []      # list to collect each employee record
    emp_id    = 1000    # starting Employee ID — increments for each employee

    # Loop through each department and generate its employees
    for dept, weight in DEPT_WEIGHTS.items():

        # Calculate how many employees this department gets
        # Round to nearest integer — final adjustment ensures exactly NUM_EMPLOYEES
        dept_count = round(NUM_EMPLOYEES * weight)

        # Generate a pool of unique manager names for this department
        # We need enough managers to cover dept_count employees at span 5-15
        # Maximum managers needed = dept_count / 5 (minimum span)
        max_managers_needed = (dept_count // 5) + 5  # add buffer
        manager_pool = []
        used_names   = set()  # track used names to avoid duplicates

        for _ in range(max_managers_needed):
            # Keep trying until we get a unique name combination
            attempts = 0
            while attempts < 100:
                name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                if name not in used_names:
                    used_names.add(name)
                    # Flag ~8% of managers as low-care (affects their team's scores)
                    is_low_care = random.random() < LOW_CARE_MANAGER_PROBABILITY
                    manager_pool.append({
                        "name":         name,
                        "is_low_care":  is_low_care,
                    })
                    break
                attempts += 1

        # Assign employees to managers using variable span (5-15)
        manager_idx        = 0     # which manager we're currently filling
        current_mgr_count  = 0     # how many reports current manager has
        # Generate a random span for the first manager
        current_mgr_span   = random.randint(5, 15)

        # Generate employee name pool for this department
        # Same first/last name pool — different from managers
        for i in range(dept_count):

            # Move to next manager if current one has reached their span
            if current_mgr_count >= current_mgr_span:
                manager_idx       += 1
                current_mgr_count  = 0
                current_mgr_span   = random.randint(5, 15)

            # Safety check — if we run out of managers, wrap around
            # This shouldn't happen with our buffer but is a safeguard
            if manager_idx >= len(manager_pool):
                manager_idx = 0

            # Get current manager details
            mgr = manager_pool[manager_idx]

            # Generate employee name
            emp_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

            # Generate tenure — years at company (0.5 to 15 years)
            # Converted to a join date relative to START_DATE
            tenure_years = round(random.uniform(0.5, 15.0), 1)
            join_date    = START_DATE - timedelta(days=int(tenure_years * 365))

            # Build the employee record as a dictionary
            employees.append({
                "employee_id":      emp_id,
                "name":             emp_name,
                "department":       dept,
                "job_title":        random.choice(TITLES[dept]),
                "manager":          mgr["name"],
                "manager_low_care": mgr["is_low_care"],  # used in pulse generation
                "employment_type":  random.choice(EMPLOYMENT_TYPES),
                "tenure_years":     tenure_years,
                "join_date":        join_date.strftime("%Y-%m-%d"),
                "status":           "Active",
                "company":          COMPANY_NAME,
            })

            emp_id            += 1   # increment employee ID
            current_mgr_count += 1   # increment this manager's report count

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(employees)

    # Trim or pad to hit exactly NUM_EMPLOYEES
    # (rounding across 9 departments may give us 1-2 extra or short)
    df = df.head(NUM_EMPLOYEES)

    print(f"  ✓ Brick 2 complete — employees generated")
    print(f"    Total employees : {len(df):,}")
    print(f"    Departments     : {df['department'].nunique()}")
    print(f"    Unique managers : {df['manager'].nunique()}")
    print(f"    Low-care mgrs   : {df[df['manager_low_care']==True]['manager'].nunique()}")
    print(f"    Avg tenure      : {df['tenure_years'].mean():.1f} years")

    return df

# ── Call Brick 2 ──────────────────────────────────────────────────────────────
df_employees = generate_employees()


# ── BRICK 3 — Pulse Response Generation ──────────────────────────────────────
# Generates 26,000 rows of weekly pulse data (500 employees × 52 weeks).
# Applies all 9 department engagement patterns, low-care manager penalties,
# tenure effects, absenteeism and overtime patterns, and open text feedback.

def generate_pulse_responses(df_employees):
    """Generate weekly pulse responses for all employees and return as DataFrame."""

    responses = []  # list to collect each weekly response record

    # Loop through every employee
    for _, emp in df_employees.iterrows():

        dept    = emp["department"]
        pattern = DEPT_PATTERNS[dept]  # get this department's engagement pattern

        # Base score for this employee — department base + small personal offset
        # Personal offset means employees in the same dept aren't all identical
        personal_base = pattern["base"] + np.random.uniform(-0.08, 0.08)
        personal_base = np.clip(personal_base, 0.3, 1.0)  # keep within bounds

        # Loop through every week
        for week_num, week_date in enumerate(WEEK_DATES):

            # ── Apply trend over time ─────────────────────────────────────────
            # Trend is a small weekly drift — negative = declining, positive = improving
            trend_effect = pattern["trend"] * week_num

            # ── Apply recovery inflection ─────────────────────────────────────
            # For Technology — scores improve more steeply after week 130
            recovery_boost = 0.0
            if pattern["recovery_week"] and week_num >= pattern["recovery_week"]:
                weeks_recovering  = week_num - pattern["recovery_week"]
                recovery_boost    = min(weeks_recovering * 0.002, 0.15)

            # ── Calculate week base score ─────────────────────────────────────
            # Combine personal base + trend + recovery + random weekly noise
            week_base = (
                personal_base
                + trend_effect
                + recovery_boost
                + np.random.normal(0, pattern["volatility"])
            )
            week_base = np.clip(week_base, 0.2, 1.0)  # keep within bounds

            # ── Generate 5 dimension scores ───────────────────────────────────
            # Each dimension gets a slight individual variation around week_base.
            # Scores are on a 1-10 scale — multiply base (0-1) by 10.
            scores = {}
            for dim in DIMENSIONS:
                # Each dimension varies slightly from the week base
                dim_score = week_base * 10 + np.random.normal(0, 0.6)
                dim_score = np.clip(dim_score, 1.0, 10.0)  # enforce 1-10 range
                scores[dim] = round(dim_score, 1)

            # ── Apply low-care manager penalty ────────────────────────────────
            # Employees under low-care managers get Care and Connection pulled down.
            # Simulates the manager effectiveness signal HR should detect.
            if emp["manager_low_care"]:
                scores["Care"]       = round(max(1.0, scores["Care"]       - np.random.uniform(1.5, 2.5)), 1)
                scores["Connection"] = round(max(1.0, scores["Connection"] - np.random.uniform(1.0, 2.0)), 1)

            # ── Apply tenure effect ───────────────────────────────────────────
            # New employees (tenure < 1 year) score lower on Connection and Confidence.
            # Reflects the onboarding gap — not yet embedded in the culture.
            if emp["tenure_years"] < 1.0:
                scores["Connection"] = round(max(1.0, scores["Connection"] - np.random.uniform(0.5, 1.5)), 1)
                scores["Confidence"] = round(max(1.0, scores["Confidence"] - np.random.uniform(0.5, 1.5)), 1)

            # ── Composite engagement score ────────────────────────────────────
            # Simple average of all 5 dimension scores, scaled to 0-100.
            composite = round(sum(scores.values()) / len(DIMENSIONS) * 10, 1)

            # ── Engagement label ──────────────────────────────────────────────
            # Bucketed into three categories based on composite score.
            if composite >= 70:
                label = "Engaged"
            elif composite >= 45:
                label = "Neutral"
            else:
                label = "At Risk"

            # ── Open text feedback ────────────────────────────────────────────
            # Matched to composite score range — positive, neutral, or negative.
            # Not every employee responds every week — 85% response rate.
            if random.random() < 0.85:
                if composite >= 70:
                    feedback = random.choice(FEEDBACK_POSITIVE)
                elif composite >= 45:
                    feedback = random.choice(FEEDBACK_NEUTRAL)
                else:
                    feedback = random.choice(FEEDBACK_NEGATIVE)
            else:
                feedback = ""   # no response this week

            # ── Absenteeism ───────────────────────────────────────────────────
            # Low engagement correlates with higher absenteeism.
            # At Risk employees have higher probability of absence days.
            if label == "At Risk":
                absent_days = np.random.choice([0, 1, 2, 3], p=[0.50, 0.25, 0.15, 0.10])
            elif label == "Neutral":
                absent_days = np.random.choice([0, 1, 2],    p=[0.75, 0.18, 0.07])
            else:
                absent_days = np.random.choice([0, 1],       p=[0.92, 0.08])

            # ── Overtime hours ────────────────────────────────────────────────
            # High overtime correlates with declining Contribution and Care.
            # Enterprise and Sales have higher overtime probability.
            if dept in ["Enterprise", "Sales", "Technology"]:
                overtime_hrs = round(np.random.choice(
                    [0, 2, 4, 6, 8, 10],
                    p=[0.35, 0.25, 0.20, 0.10, 0.07, 0.03]
                ), 0)
            else:
                overtime_hrs = round(np.random.choice(
                    [0, 2, 4, 6],
                    p=[0.60, 0.25, 0.10, 0.05]
                ), 0)

            # ── Build the response record ─────────────────────────────────────
            responses.append({
                "response_id":      f"R{emp['employee_id']}W{week_num+1:03d}",
                "employee_id":      emp["employee_id"],
                "name":             emp["name"],
                "department":       dept,
                "manager":          emp["manager"],
                "week_number":      week_num + 1,
                "week_date":        week_date.strftime("%Y-%m-%d"),
                "clarity":          scores["Clarity"],
                "connection":       scores["Connection"],
                "contribution":     scores["Contribution"],
                "confidence":       scores["Confidence"],
                "care":             scores["Care"],
                "composite_score":  composite,
                "engagement_label": label,
                "feedback":         feedback,
                "absent_days":      int(absent_days),
                "overtime_hours":   int(overtime_hrs),
                "tenure_years":     emp["tenure_years"],
                "employment_type":  emp["employment_type"],
            })

    # Convert to DataFrame
    df = pd.DataFrame(responses)

    print(f"  ✓ Brick 3 complete — pulse responses generated")
    print(f"    Total rows       : {len(df):,}")
    print(f"    Weeks covered    : {df['week_number'].nunique()}")
    print(f"    Engaged          : {(df['engagement_label']=='Engaged').sum():,} ({(df['engagement_label']=='Engaged').mean()*100:.1f}%)")
    print(f"    Neutral          : {(df['engagement_label']=='Neutral').sum():,} ({(df['engagement_label']=='Neutral').mean()*100:.1f}%)")
    print(f"    At Risk          : {(df['engagement_label']=='At Risk').sum():,} ({(df['engagement_label']=='At Risk').mean()*100:.1f}%)")
    print(f"    Avg composite    : {df['composite_score'].mean():.1f}")
    print(f"    Response rate    : {(df['feedback']!='').mean()*100:.1f}%")

    return df

# ── Call Brick 3 ──────────────────────────────────────────────────────────────
print("  Generating pulse responses — please wait...")
df_pulse = generate_pulse_responses(df_employees)


# ── BRICK 4 — Activities Generation ──────────────────────────────────────────
# Generates ~100 company activities across 52 weeks.
# Activity types: wellness, learning, social, town hall, volunteering.
# Some are org-wide, some department-specific.
# Each activity has a points value employees earn by attending.

def generate_activities():
    """Generate company activities and return as DataFrame."""

    # ── Activity templates ────────────────────────────────────────────────────
    # Each template has a name, type, and points value.
    # Points align with the points system locked in UX — attendance earns 25 pts.
    ACTIVITY_TEMPLATES = [
        # Wellness
        {"name": "Morning Wellness Walk",         "type": "Wellness",    "points": 25},
        {"name": "Mental Health Awareness Talk",  "type": "Wellness",    "points": 25},
        {"name": "Yoga and Mindfulness Session",  "type": "Wellness",    "points": 25},
        {"name": "Nutrition and Healthy Eating Workshop", "type": "Wellness", "points": 25},
        {"name": "Financial Wellness Seminar",    "type": "Wellness",    "points": 25},
        # Learning
        {"name": "Leadership Development Workshop", "type": "Learning",  "points": 25},
        {"name": "Data Literacy Bootcamp",        "type": "Learning",    "points": 25},
        {"name": "Communication Skills Training", "type": "Learning",    "points": 25},
        {"name": "AI in the Workplace Session",   "type": "Learning",    "points": 25},
        {"name": "Excel and Analytics Clinic",    "type": "Learning",    "points": 25},
        # Social
        {"name": "Team Lunch and Learn",          "type": "Social",      "points": 25},
        {"name": "Department Town Hall",          "type": "Town Hall",   "points": 25},
        {"name": "All-Hands Company Update",      "type": "Town Hall",   "points": 25},
        {"name": "Year-End Celebration Dinner",   "type": "Social",      "points": 25},
        {"name": "New Joiner Welcome Breakfast",  "type": "Social",      "points": 25},
        # Volunteering
        {"name": "Community Clean-Up Day",        "type": "Volunteering","points": 25},
        {"name": "Food Bank Volunteer Drive",     "type": "Volunteering","points": 25},
        {"name": "Tree Planting Initiative",      "type": "Volunteering","points": 25},
        # ERG / Communities
        {"name": "Women in Leadership Forum",     "type": "ERG",         "points": 25},
        {"name": "DEI Fireside Chat",             "type": "ERG",         "points": 25},
        {"name": "Young Professionals Meetup",   "type": "ERG",         "points": 25},
    ]

    # Department targets — some activities are org-wide, some dept-specific
    DEPT_TARGETS = ["All"] * 6 + list(DEPT_WEIGHTS.keys())
    # "All" appears 6 times so org-wide activities are more common than dept-specific

    activities = []
    activity_id = 1

    # Generate ~2 activities per month = ~24 activities across 52 weeks
    # Spread them across the year at roughly 2-week intervals
    for week_num in range(0, NUM_WEEKS, 2):  # every 2 weeks
        # Pick 1-2 activities this fortnight
        num_this_week = random.randint(1, 2)

        for _ in range(num_this_week):
            template   = random.choice(ACTIVITY_TEMPLATES)
            dept_target = random.choice(DEPT_TARGETS)

            # Activity date — random day within the week
            activity_date = WEEK_DATES[week_num] + timedelta(days=random.randint(0, 4))

            # Capacity — how many employees can attend
            # Org-wide events are larger, dept-specific are smaller
            if dept_target == "All":
                capacity = random.randint(50, 200)
            else:
                capacity = random.randint(10, 50)

            # Format — in-person or virtual
            format_ = random.choice(["In-Person", "In-Person", "Virtual"])
            # In-person appears twice so it's more common

            activities.append({
                "activity_id":      f"ACT{activity_id:04d}",
                "name":             template["name"],
                "type":             template["type"],
                "department_target": dept_target,
                "date":             activity_date.strftime("%Y-%m-%d"),
                "week_number":      week_num + 1,
                "format":           format_,
                "capacity":         capacity,
                "points":           template["points"],
                "company":          COMPANY_NAME,
            })

            activity_id += 1

    df = pd.DataFrame(activities)

    print(f"  ✓ Brick 4 complete — activities generated")
    print(f"    Total activities : {len(df):,}")
    print(f"    Org-wide         : {(df['department_target']=='All').sum()}")
    print(f"    Dept-specific    : {(df['department_target']!='All').sum()}")
    print(f"    Activity types   : {df['type'].nunique()}")
    print(f"    Date range       : {df['date'].min()} → {df['date'].max()}")

    return df

# ── Call Brick 4 ──────────────────────────────────────────────────────────────
df_activities = generate_activities()

# ── BRICK 5 — Kudos Generation ────────────────────────────────────────────────
# Generates peer recognition records across 52 weeks.
# Both giver and recipient earn points — giver 10pts, recipient 15pts.
# High engagement departments give more Kudos than low engagement ones.
# Max 3 Kudos given per employee per week (frequency cap from points system).

def generate_kudos(df_employees):
    """Generate Kudos recognition records and return as DataFrame."""

    # ── Kudos categories ──────────────────────────────────────────────────────
    # Employees tag each Kudos with a company value category.
    KUDOS_CATEGORIES = [
        "Teamwork",
        "Innovation",
        "Leadership",
        "Customer Focus",
        "Going Above and Beyond",
        "Integrity",
        "Problem Solving",
        "Mentoring",
    ]

    # ── Kudos message templates by category ──────────────────────────────────
    KUDOS_MESSAGES = {
        "Teamwork": [
            "Always steps up to support the team — true team player.",
            "Made the whole project easier with great collaboration.",
            "Goes out of their way to help colleagues succeed.",
        ],
        "Innovation": [
            "Brought a fresh perspective that completely changed our approach.",
            "Incredible creative thinking on a tough problem this week.",
            "Found a smarter way to do something we had been doing wrong for years.",
        ],
        "Leadership": [
            "Kept the team focused and motivated during a challenging week.",
            "Showed real leadership when it mattered most.",
            "Stepped up without being asked and made a real difference.",
        ],
        "Customer Focus": [
            "Went the extra mile for the client and it showed.",
            "Outstanding customer handling — the feedback was glowing.",
            "Always puts the customer first, even under pressure.",
        ],
        "Going Above and Beyond": [
            "Stayed late to make sure the deadline was met — thank you.",
            "Did far more than was asked and never complained once.",
            "Exceptional effort this week — the results speak for themselves.",
        ],
        "Integrity": [
            "Handled a difficult situation with complete professionalism.",
            "Always does the right thing even when no one is watching.",
            "Transparent and honest throughout a tricky project.",
        ],
        "Problem Solving": [
            "Solved a problem that had been blocking the team for weeks.",
            "Quick thinking under pressure saved the day.",
            "Found the root cause when everyone else was looking at symptoms.",
        ],
        "Mentoring": [
            "Has been an incredible mentor to new joiners on the team.",
            "Patient, generous with knowledge, and always makes time to help.",
            "The team learns so much just by working alongside them.",
        ],
    }

    # ── Kudos probability by department engagement ────────────────────────────
    # Higher engagement departments give more Kudos.
    # Probability = chance any given employee gives Kudos in a given week.
    KUDOS_PROBABILITY = {
        "Retail":             0.08,   # low engagement = fewer Kudos
        "Technology":         0.15,
        "Sales":              0.18,
        "Marketing":          0.22,   # creative, collaborative = more Kudos
        "Enterprise":         0.16,
        "Finance":            0.10,
        "HR":                 0.28,   # highest — HR culture drives recognition
        "Legal":              0.09,
        "Corporate Affairs":  0.14,
    }

    kudos    = []
    kudos_id = 1

    # Convert employees to a list for random recipient selection
    emp_list = df_employees.to_dict("records")

    # Loop through every employee and every week
    for _, giver in df_employees.iterrows():

        dept        = giver["department"]
        probability = KUDOS_PROBABILITY[dept]

        for week_num, week_date in enumerate(WEEK_DATES):

            # Does this employee give Kudos this week?
            if random.random() > probability:
                continue   # skip — no Kudos this week

            # How many Kudos does this employee give this week? Max 3.
            num_kudos = random.randint(1, 3)

            for _ in range(num_kudos):

                # Pick a recipient — anyone in the org except themselves
                recipient = random.choice(emp_list)
                while recipient["employee_id"] == giver["employee_id"]:
                    recipient = random.choice(emp_list)

                # Pick category and matching message
                category = random.choice(KUDOS_CATEGORIES)
                message  = random.choice(KUDOS_MESSAGES[category])

                # Kudos date — random day within the week
                kudos_date = week_date + timedelta(days=random.randint(0, 4))

                kudos.append({
                    "kudos_id":          f"K{kudos_id:06d}",
                    "week_number":       week_num + 1,
                    "date":              kudos_date.strftime("%Y-%m-%d"),
                    "giver_id":          giver["employee_id"],
                    "giver_name":        giver["name"],
                    "giver_dept":        giver["department"],
                    "recipient_id":      recipient["employee_id"],
                    "recipient_name":    recipient["name"],
                    "recipient_dept":    recipient["department"],
                    "category":          category,
                    "message":           message,
                    "giver_points":      10,   # giver earns 10 pts
                    "recipient_points":  15,   # recipient earns 15 pts
                    "company":           COMPANY_NAME,
                })

                kudos_id += 1

    df = pd.DataFrame(kudos)

    print(f"  ✓ Brick 5 complete — Kudos generated")
    print(f"    Total Kudos      : {len(df):,}")
    print(f"    Unique givers    : {df['giver_id'].nunique():,}")
    print(f"    Unique recipients: {df['recipient_id'].nunique():,}")
    print(f"    Top category     : {df['category'].value_counts().index[0]}")
    print(f"    Date range       : {df['date'].min()} → {df['date'].max()}")

    return df

# ── Call Brick 5 ──────────────────────────────────────────────────────────────
df_kudos = generate_kudos(df_employees)

# ── BRICK 6 — Save to CSV ─────────────────────────────────────────────────────
# Writes all four DataFrames to the data/ folder as CSV files.
# After this brick runs, your data is ready to use in the Streamlit app.

def save_all(df_employees, df_pulse, df_activities, df_kudos):
    """Save all DataFrames to CSV files in the data/ folder."""

    # Dictionary of filename → DataFrame pairs
    files = {
        "employees.csv":       df_employees,
        "pulse_responses.csv": df_pulse,
        "activities.csv":      df_activities,
        "kudos.csv":           df_kudos,
    }

    print("  Saving files...")
    print()

    total_rows = 0

    for filename, df in files.items():
        # Build full file path
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Save to CSV — no row index written to file
        df.to_csv(filepath, index=False)

        # Get file size in KB
        file_size_kb = os.path.getsize(filepath) / 1024

        # Print file summary
        print(f"    ✓ {filename}")
        print(f"      Rows     : {len(df):,}")
        print(f"      Columns  : {len(df.columns)}")
        print(f"      Size     : {file_size_kb:.1f} KB")
        print()

        total_rows += len(df)

    print("=" * 55)
    print(f"  ✓ Brick 6 complete — all files saved to data/")
    print(f"  Total rows saved : {total_rows:,}")
    print(f"  Output folder    : {OUTPUT_DIR}")
    print("=" * 55)

# ── Call Brick 6 ──────────────────────────────────────────────────────────────
save_all(df_employees, df_pulse, df_activities, df_kudos)